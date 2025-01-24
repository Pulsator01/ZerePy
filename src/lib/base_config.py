import logging
from typing import Any, Dict, Optional
from pydantic import Field, BaseModel as PydanticBaseModel
from pydantic_settings import BaseSettings as PydanticBaseSettings
from src.lib.types import Directory
from src.lib.agent_config import AgentConfig, get_agents
from pydantic import ValidationInfo, ValidatorFunctionWrapHandler
from typing import Annotated
from pydantic import WrapValidator
from typing_extensions import TypeAliasType

logger = logging.getLogger(__name__)


class BaseConfigException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BaseSettings(PydanticBaseSettings):
    agents_dir: Directory = Field(validation_alias="AGENTS_DIR")


class BaseConfig(PydanticBaseModel):
    version: str = "0.2.0"
    agents: Dict[str, AgentConfig] = {}
    base_settings: BaseSettings = BaseSettings()

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.agents = get_agents(self.base_settings.agents_dir)

    def get_agents(self) -> list[str]:
        return list(self.agents.keys())

    def is_agent_name(self, agent_name: str) -> bool:
        return agent_name in self.agents


BASE_CONFIG = BaseConfig()


def agent_name_validator(
    value: str, handler: ValidatorFunctionWrapHandler, _info: ValidationInfo
) -> str:
    if not BASE_CONFIG.is_agent_name(value):
        raise ValueError(f"Agent {value} not found in config")
    return value


AgentName = TypeAliasType(
    "AgentName", Annotated[str, WrapValidator(agent_name_validator)]
)
