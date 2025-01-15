import datetime
import decimal
import sys
from decimal import Decimal
from typing import Optional
from venv import logger
import math
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from eth_defi.revert_reason import fetch_transaction_revert_reason
from eth_defi.token import fetch_erc20_details
from eth_defi.confirmation import wait_transactions_to_complete
from eth_defi.uniswap_v3.constants import UNISWAP_V3_DEPLOYMENTS
from eth_defi.uniswap_v3.deployment import fetch_deployment
from eth_defi.uniswap_v3.swap import swap_with_slippage_protection
from src.constants import GAS, GAS_PRICE, GAS_PRICE_UNIT
from web3 import Web3

from src.helpers.evm.contract import EvmContractHelper


class EvmTradeHelper:
    @staticmethod
    async def trade(
        web3: Web3,
        private_key: str,
        output_token: str,
        input_amount: float,
        input_token: Optional[str],
        slippage_bps: int = 100,
    ) -> str:
        QUOTE_TOKEN_ADDRESS = input_token
        BASE_TOKEN_ADDRESS = output_token
        account: LocalAccount = Account.from_key(private_key)
        my_address = account.address
        block_height = web3.eth.block_number
        logger.debug(f"\n\nBLOCK NUMBER: {block_height}\n\n")
        logger.debug(
            f"Connected to blockchain, chain id is {web3.eth.chain_id}. the latest block is {web3.eth.block_number:,}"
        )

        # Grab Uniswap v3 smart contract addreses for Polygon.
        #
        deployment_data = UNISWAP_V3_DEPLOYMENTS["ethereum"]
        # check if localnet is used
        uniswap_v3 = fetch_deployment(
            web3,
            factory_address=deployment_data["factory"],
            router_address=deployment_data["router"],
            position_manager_address=deployment_data["position_manager"],
            quoter_address=deployment_data["quoter"],
        )

        logger.debug(
            f"Using Uniwap v3 compatible router at {uniswap_v3.swap_router.address}"
        )
        # Enable eth_sendTransaction using this private key
        web3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        # Read on-chain ERC-20 token data (name, symbol, etc.)
        base = fetch_erc20_details(web3, BASE_TOKEN_ADDRESS)
        quote = fetch_erc20_details(web3, QUOTE_TOKEN_ADDRESS)

        # Native token balance
        # See https://tradingstrategy.ai/glossary/native-token
        gas_balance = web3.eth.get_balance(account.address)

        logger.debug(f"Your address is {my_address}")
        logger.debug(f"Your have {base.fetch_balance_of(my_address)} {base.symbol}")
        logger.debug(f"Your have {quote.fetch_balance_of(my_address)} {quote.symbol}")
        logger.debug(f"Your have {gas_balance / (10 ** 18)} for gas fees")

        assert (
            quote.fetch_balance_of(my_address) > 0
        ), f"Cannot perform swap, as you have zero {quote.symbol} needed to swap"
        decimals = await EvmContractHelper.read_contract(web3, input_token, "decimals")
        # Ask for transfer details
        decimal_amount = input_amount
        # Some input validation
        try:
            decimal_amount = Decimal(decimal_amount)
        except (ValueError, decimal.InvalidOperation) as e:
            raise AssertionError(f"Not a good decimal amount: {decimal_amount}") from e

        # Fat-fingering check
        logger.info(
            f"Confirm swap amount {decimal_amount} {quote.symbol} to {base.symbol}"
        )
        confirm = input("Ok [y/n]?")
        if not confirm.lower().startswith("y"):
            logger.debug("Aborted")
            sys.exit(1)

        # Convert a human-readable number to fixed decimal with 18 decimal places
        raw_amount = quote.convert_to_raw(input_amount)

        # Each DEX trade is two transactions
        # - ERC-20.approve()
        # - swap (various functions)
        # This is due to bad design of ERC-20 tokens,
        # more here https://twitter.com/moo9000/status/1619319039230197760

        # Uniswap router must be allowed to spent our quote token
        # and we do this by calling ERC20.approve() from our account
        # to the token contract.
        needs_approval = quote.contract.functions.allowance(
            my_address, uniswap_v3.swap_router.address
        ).call()

        needs_approval = needs_approval / 10**decimals
        logger.debug(
            f"Needs approval: {needs_approval} {quote.symbol} to spend {raw_amount} {quote.symbol}"
        )
        if needs_approval >= raw_amount:
            logger.debug("Already approved")
            tx_1 = None
        else:
            logger.debug("Approving")
            approve = quote.contract.functions.approve(
                uniswap_v3.swap_router.address, raw_amount
            )
            tx_1 = approve.build_transaction(
                {
                    # approve() may take more than 500,000 gas on Arbitrum One
                    "gas": GAS,
                    "gasPrice": web3.to_wei(GAS_PRICE, GAS_PRICE_UNIT),
                    "from": my_address,
                }
            )

        #
        # Uniswap v3 may have multiple pools per
        # trading pair differetiated by the fee tier. For example
        # WETH-USDC has pools of 0.05%, 0.30% and 1%
        # fees. Check for different options
        # in https://tradingstrategy.ai/search
        #
        # Here we use 5 BPS fee pool (5/10,000).
        #
        #
        # Build a swap transaction with slippage protection
        #
        # Slippage protection is very important, or you
        # get instantly overrun by MEV bots with
        # sandwitch attacks
        #
        # https://tradingstrategy.ai/glossary/mev
        #
        #
        bound_solidity_func = swap_with_slippage_protection(
            uniswap_v3,
            base_token=base,
            quote_token=quote,
            max_slippage=slippage_bps,  # Allow 20 BPS slippage before tx reverts
            amount_in=raw_amount,
            recipient_address=my_address,
            pool_fees=[500],  # 5 BPS pool WETH-USDC
        )
        nonce = web3.eth.get_transaction_count(my_address)
        tx_2 = bound_solidity_func.build_transaction(
            {
                # Uniswap swap should not take more than 1M gas units.
                # We do not use automatic gas estimation, as it is unreliable
                # and the number here is the maximum value only.
                # Only way to know this number is by trial and error
                # and experience.
                "gas": GAS,
                "gasPrice": web3.to_wei(GAS_PRICE, GAS_PRICE_UNIT),
                "from": my_address,
                "nonce": nonce,
            }
        )

        # Sign and broadcast the transaction using our private key
        # tx_hash_1 = web3.eth.send_transaction(tx_1)
        tx_hash_2 = web3.eth.send_transaction(tx_2)

        # This will raise an exception if we do not confirm within the timeout.
        # If the timeout occurs the script abort and you need to
        # manually check the transaction hash in a blockchain explorer
        # whether the transaction completed or not.
        tx_wait_minutes = 2.5
        logger.debug(
            f"Broadcasted transactions {tx_hash_1.hex()}, {tx_hash_2.hex()}, now waiting {tx_wait_minutes} minutes for it to be included in a new block"
        )
        logger.debug(
            f"View your transactions confirming at https://polygonscan/address/{my_address}"
        )
        receipts = wait_transactions_to_complete(
            web3,
            [tx_hash_2],
            max_timeout=datetime.timedelta(minutes=tx_wait_minutes),
            confirmation_block_count=1,
        )

        # Check if any our transactions failed
        # and display the reason
        for completed_tx_hash, receipt in receipts.items():
            if receipt["status"] == 0:
                revert_reason = fetch_transaction_revert_reason(web3, completed_tx_hash)
                raise AssertionError(
                    f"Our transaction {completed_tx_hash.hex()} failed because of: {revert_reason}"
                )

        logger.debug("All ok!")
        logger.debug(
            f"After swap, you have {base.fetch_balance_of(my_address)} {base.symbol}"
        )
        logger.debug(
            f"After swap, you have {quote.fetch_balance_of(my_address)} {quote.symbol}"
        )
        logger.debug(
            f"After swap, you have {gas_balance / (10 ** 18)} native token left"
        )
