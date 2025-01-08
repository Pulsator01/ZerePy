import logging
from src.action_handler import register_action

logger = logging.getLogger("agent")

@register_action("evm-transfer")
def evm_transfer(agent, **kwargs):
    """Transfer Native or ERC20 tokens"""
    agent.logger.info("\n💸 INITIATING TRANSFER")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="transfer",
            params=[
                kwargs.get('to_address'),
                kwargs.get('amount'),
                kwargs.get('token_mint', None)
            ]
        )
        agent.logger.info("✅ Transfer completed!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Transfer failed: {str(e)}")
        return False

@register_action("evm-swap")
def evm_swap(agent, **kwargs):
    """Swap tokens using Jupiter"""
    agent.logger.info("\n🔄 INITIATING TOKEN SWAP")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="trade",
            params=[
                kwargs.get('output_mint'),
                kwargs.get('input_amount'),
                kwargs.get('input_mint', None),
                kwargs.get('slippage_bps', 100)
            ]
        )
        agent.logger.info("✅ Swap completed!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Swap failed: {str(e)}")
        return False

@register_action("evm-balance")
def evm_balance(agent, **kwargs):
    """Check Native or token balance"""
    agent.logger.info("\n💰 CHECKING BALANCE")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="get-balance",
            params=[kwargs.get('token_address', None)]
        )
        agent.logger.info(f"Balance: {result}")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Balance check failed: {str(e)}")
        return None

@register_action("evm-stake")
def evm_stake(agent, **kwargs):
    """Stake Native"""
    agent.logger.info("\n🎯 INITIATING Native STAKE")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="stake",
            params=[kwargs.get('amount')]
        )
        agent.logger.info("✅ Staking completed!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Staking failed: {str(e)}")
        return False

@register_action("evm-lend")
def evm_lend(agent, **kwargs):
    """Lend assets using Lulo"""
    agent.logger.info("\n🏦 INITIATING LENDING")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="lend-assets",
            params=[kwargs.get('amount')]
        )
        agent.logger.info("✅ Lending completed!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Lending failed: {str(e)}")
        return False

@register_action("evm-request-funds")
def request_faucet_funds(agent, **kwargs):
    """Request faucet funds for testing"""
    agent.logger.info("\n🚰 REQUESTING FAUCET FUNDS")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="request-faucet",
            params=[]
        )
        agent.logger.info("✅ Faucet request completed!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Faucet request failed: {str(e)}")
        return False

@register_action("evm-deploy-token")
def evm_deploy_token(agent, **kwargs):
    """Deploy a new token"""
    agent.logger.info("\n🪙 DEPLOYING NEW TOKEN")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="deploy-token",
            params=[kwargs.get('decimals', 9)]
        )
        agent.logger.info("✅ Token deployed!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Token deployment failed: {str(e)}")
        return False

@register_action("evm-get-price")
def evm_get_price(agent, **kwargs):
    """Get token price"""
    agent.logger.info("\n💲 FETCHING TOKEN PRICE")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="fetch-price",
            params=[kwargs.get('token_id')]
        )
        agent.logger.info(f"Price: {result}")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Price fetch failed: {str(e)}")
        return None

@register_action("evm-get-tps")
def evm_get_tps(agent, **kwargs):
    """Get current Evm TPS"""
    agent.logger.info("\n📊 FETCHING CURRENT TPS")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="get-tps",
            params=[]
        )
        agent.logger.info(f"Current TPS: {result}")
        return result
    except Exception as e:
        agent.logger.error(f"❌ TPS fetch failed: {str(e)}")
        return None

@register_action("evm-get-token-by-ticker")
def get_token_data_by_ticker(agent, **kwargs):
    """Get token data by ticker"""
    agent.logger.info("\n🔍 FETCHING TOKEN DATA BY TICKER")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="get-token-by-ticker",
            params=[kwargs.get('ticker')]
        )
        agent.logger.info("✅ Token data retrieved!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Token data fetch failed: {str(e)}")
        return None

@register_action("evm-get-token-by-address")
def get_token_data_by_address(agent, **kwargs):
    """Get token data by address"""
    agent.logger.info("\n🔍 FETCHING TOKEN DATA BY ADDRESS")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="get-token-by-address",
            params=[kwargs.get('mint')]
        )
        agent.logger.info("✅ Token data retrieved!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Token data fetch failed: {str(e)}")
        return None

@register_action("evm-launch-pump-token")
def launch_pump_fun_token(agent, **kwargs):
    """Launch a Pump & Fun token"""
    agent.logger.info("\n🚀 LAUNCHING PUMP & FUN TOKEN")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="launch-pump-token",
            params=[
                kwargs.get('token_name'),
                kwargs.get('token_ticker'),
                kwargs.get('description'),
                kwargs.get('image_url'),
                kwargs.get('options', {})
            ]
        )
        agent.logger.info("✅ Token launched successfully!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Token launch failed: {str(e)}")
        return False

@register_action("evm-list-contract-functions")
def list_contract_functions(agent, **kwargs):
    """List contract functions"""
    agent.logger.info("\n📜 LISTING CONTRACT FUNCTIONS")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="list-contract-functions",
            params=[kwargs.get('contract_address')]
        )
        agent.logger.info("✅ Contract functions listed!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Contract functions listing failed: {str(e)}")
        return None
    
@register_action("evm-call-contract-function")
def call_contract_function(agent, **kwargs):
    """Call contract function"""
    agent.logger.info("\n📞 CALLING CONTRACT FUNCTION")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="call-contract-function",
            params=[
                kwargs.get('contract_address'),
                kwargs.get('function_name'),
                kwargs.get('args', [])
            ]
        )
        agent.logger.info("✅ Contract function called!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ Contract function call failed: {str(e)}")
        return None
    
@register_action("evm-wrap-eth")
def wrap_eth(agent, **kwargs):
    """Wrap ETH to WETH"""
    agent.logger.info("\n🎁 WRAPPING ETH TO WETH")
    try:
        result = agent.connection_manager.perform_action(
            connection_name="evm",
            action_name="wrap-eth",
            params=[kwargs.get('amount')]
        )
        agent.logger.info("✅ ETH wrapped to WETH!")
        return result
    except Exception as e:
        agent.logger.error(f"❌ ETH wrapping failed: {str(e)}")
        return False