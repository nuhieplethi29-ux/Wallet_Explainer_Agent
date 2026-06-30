from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    etherscan_api_key: str
    openai_api_key: str
    openai_model: str

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()

        etherscan_api_key = os.getenv("ETHERSCAN_API_KEY", "").strip()
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()

        if not etherscan_api_key:
            raise ConfigError("Missing ETHERSCAN_API_KEY. Add it to your .env file.")
        if not openai_api_key:
            raise ConfigError("Missing OPENAI_API_KEY. Add it to your .env file.")

        return cls(
            etherscan_api_key=etherscan_api_key,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
        )
