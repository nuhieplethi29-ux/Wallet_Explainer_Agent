from __future__ import annotations

import json
from dataclasses import asdict

from openai import OpenAI, OpenAIError

from src.models import WalletActivity


SYSTEM_PROMPT = """You are a crypto wallet explainer assistant.

Explain recent Ethereum wallet activity in simple Vietnamese.

Rules:
- Only use the provided wallet activity data.
- Do not invent wallet owner identity.
- Do not provide financial advice.
- Do not recommend buying, selling, shorting, longing, or copying this wallet.
- Use cautious language: "co ve", "co kha nang", "dua tren du lieu gan day".
- If the data is limited, say so clearly.
- Output Markdown in Vietnamese.
"""

USER_PROMPT_TEMPLATE = """Hay giai thich vi Ethereum sau bang tieng Viet.

Wallet:
{wallet_address}

Activities:
{activities_json}

Output format:

## Tom tat vi

## Hoat dong gan day

## Suy luan hanh vi

## Luu y
"""


class OpenAIExplainer:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def explain_wallet(self, wallet_address: str, activities: list[WalletActivity]) -> str:
        activities_json = json.dumps(
            [asdict(activity) for activity in activities],
            ensure_ascii=False,
            indent=2,
        )
        user_prompt = USER_PROMPT_TEMPLATE.format(
            wallet_address=wallet_address,
            activities_json=activities_json,
        )

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except OpenAIError as exc:
            raise RuntimeError(f"OpenAI API error: {exc}") from exc

        output_text = getattr(response, "output_text", "").strip()
        if not output_text:
            raise RuntimeError("OpenAI returned an empty explanation.")

        return output_text
