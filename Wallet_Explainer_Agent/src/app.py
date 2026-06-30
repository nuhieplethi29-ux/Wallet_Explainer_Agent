from __future__ import annotations

from src.clients.etherscan_client import EtherscanClient
from src.config import Config
from src.services.ai_explainer import OpenAIExplainer
from src.services.wallet_activity_service import WalletActivityService
from src.utils.validators import validate_wallet_address


class WalletExplainerApp:
    def __init__(self) -> None:
        self.config = Config.from_env()
        self.etherscan_client = EtherscanClient(self.config.etherscan_api_key)
        self.activity_service = WalletActivityService(self.etherscan_client)
        self.ai_explainer = OpenAIExplainer(
            api_key=self.config.openai_api_key,
            model=self.config.openai_model,
        )

    def run(self, wallet: str, limit: int = 10, chainid: int = 1) -> None:
        wallet = validate_wallet_address(wallet)

        if limit < 1:
            raise ValueError("--limit must be greater than 0.")

        activities = self.activity_service.get_recent_activity(wallet, limit, chainid)
        if not activities:
            raise RuntimeError("No recent transactions found for this wallet.")

        explanation = self.ai_explainer.explain_wallet(wallet, activities)
        print(explanation)
