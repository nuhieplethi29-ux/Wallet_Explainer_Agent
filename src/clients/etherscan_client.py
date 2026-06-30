from __future__ import annotations

from typing import Any

import requests


class EtherscanClient:
    BASE_URL = "https://api.etherscan.io/v2/api"
    TIMEOUT_SECONDS = 20

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.session = requests.Session()

    def get_normal_transactions(
        self,
        address: str,
        limit: int,
        chainid: int = 1,
    ) -> list[dict[str, Any]]:
        params = {
            "chainid": chainid,
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": limit,
            "sort": "desc",
            "apikey": self.api_key,
        }
        return self._get_result(params)

    def get_erc20_transfers(
        self,
        address: str,
        limit: int,
        chainid: int = 1,
    ) -> list[dict[str, Any]]:
        params = {
            "chainid": chainid,
            "module": "account",
            "action": "tokentx",
            "address": address,
            "page": 1,
            "offset": limit * 3,
            "sort": "desc",
            "apikey": self.api_key,
        }
        return self._get_result(params)

    def _get_result(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=self.TIMEOUT_SECONDS)
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise RuntimeError("Etherscan request timed out. Please try again.") from exc
        except requests.RequestException as exc:
            raise RuntimeError(f"Etherscan network error: {exc}") from exc
        except ValueError as exc:
            raise RuntimeError("Etherscan returned an invalid JSON response.") from exc

        status = str(payload.get("status", ""))
        message = str(payload.get("message", ""))
        result = payload.get("result")

        if isinstance(result, str):
            if status == "0" and "No transactions found" in result:
                return []
            raise RuntimeError(f"Etherscan API error: {result}")

        if status == "0" and not isinstance(result, list):
            raise RuntimeError(f"Etherscan API error: {message or 'Unknown error'}")

        if not isinstance(result, list):
            raise RuntimeError("Etherscan returned an unexpected response format.")

        return result
