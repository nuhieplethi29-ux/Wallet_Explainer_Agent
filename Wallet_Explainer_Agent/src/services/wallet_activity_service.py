from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.clients.etherscan_client import EtherscanClient
from src.constants import DEFI_KEYWORDS, KNOWN_TOKENS
from src.models import NormalTransaction, TokenTransfer, WalletActivity
from src.utils.formatters import format_amount


class WalletActivityService:
    def __init__(self, etherscan_client: EtherscanClient) -> None:
        self.etherscan_client = etherscan_client

    def get_recent_activity(self, wallet: str, limit: int, chainid: int = 1) -> list[WalletActivity]:
        wallet_lower = wallet.lower()
        raw_transactions = self.etherscan_client.get_normal_transactions(wallet, limit, chainid)
        raw_transfers = self.etherscan_client.get_erc20_transfers(wallet, limit, chainid)

        transactions = [self._parse_normal_transaction(item) for item in raw_transactions]
        transfers = [self._parse_token_transfer(item, wallet_lower) for item in raw_transfers]

        transfers_by_hash: dict[str, list[TokenTransfer]] = defaultdict(list)
        for transfer in transfers:
            transfers_by_hash[transfer.tx_hash].append(transfer)

        activities = [
            self._build_activity(transaction, transfers_by_hash.get(transaction.tx_hash, []), wallet_lower)
            for transaction in transactions
        ]

        seen_hashes = {activity.tx_hash for activity in activities}
        transfer_only_groups = {
            tx_hash: tx_transfers
            for tx_hash, tx_transfers in transfers_by_hash.items()
            if tx_hash not in seen_hashes
        }

        for tx_hash, tx_transfers in transfer_only_groups.items():
            activities.append(self._build_transfer_only_activity(tx_hash, tx_transfers))

        activities.sort(key=lambda activity: activity.timestamp, reverse=True)
        return activities[:limit]

    def _parse_normal_transaction(self, item: dict[str, Any]) -> NormalTransaction:
        return NormalTransaction(
            tx_hash=str(item.get("hash", "")),
            timestamp=self._safe_int(item.get("timeStamp")),
            from_address=str(item.get("from", "")).lower(),
            to_address=str(item.get("to", "")).lower(),
            eth_value=self._wei_to_eth(item.get("value", "0")),
            function_name=str(item.get("functionName") or "") or None,
            method_id=str(item.get("methodId") or "") or None,
            is_failed=item.get("isError") == "1" or item.get("txreceipt_status") == "0",
        )

    def _parse_token_transfer(self, item: dict[str, Any], wallet_lower: str) -> TokenTransfer:
        token_decimal = self._safe_int(item.get("tokenDecimal"))
        amount = self._token_amount(item.get("value", "0"), token_decimal)
        from_address = str(item.get("from", "")).lower()
        to_address = str(item.get("to", "")).lower()
        contract_address = str(item.get("contractAddress", "")).lower()
        token_symbol = KNOWN_TOKENS.get(contract_address) or str(item.get("tokenSymbol") or "UNKNOWN")

        direction = "other"
        if from_address == wallet_lower:
            direction = "out"
        elif to_address == wallet_lower:
            direction = "in"

        return TokenTransfer(
            tx_hash=str(item.get("hash", "")),
            timestamp=self._safe_int(item.get("timeStamp")),
            from_address=from_address,
            to_address=to_address,
            token_symbol=token_symbol,
            token_name=str(item.get("tokenName") or token_symbol),
            token_decimal=token_decimal,
            value_raw=str(item.get("value", "0")),
            direction=direction,
            amount=amount,
        )

    def _build_activity(
        self,
        transaction: NormalTransaction,
        transfers: list[TokenTransfer],
        wallet_lower: str,
    ) -> WalletActivity:
        tokens_sent = self._token_labels(transfers, "out")
        tokens_received = self._token_labels(transfers, "in")
        eth_sent = transaction.eth_value if transaction.from_address == wallet_lower else 0.0
        eth_received = transaction.eth_value if transaction.to_address == wallet_lower else 0.0

        activity_type = self._detect_activity_type(
            transaction=transaction,
            tokens_sent=tokens_sent,
            tokens_received=tokens_received,
            eth_sent=eth_sent,
            eth_received=eth_received,
        )

        summary = self._build_summary(activity_type, tokens_sent, tokens_received, eth_sent, eth_received)
        protocol_hint = transaction.function_name if self._looks_like_defi(transaction.function_name) else None

        return WalletActivity(
            tx_hash=transaction.tx_hash,
            timestamp=transaction.timestamp,
            activity_type=activity_type,
            summary=summary,
            tokens_sent=tokens_sent,
            tokens_received=tokens_received,
            eth_sent=eth_sent,
            eth_received=eth_received,
            protocol_hint=protocol_hint,
            is_failed=transaction.is_failed,
        )

    def _build_transfer_only_activity(
        self,
        tx_hash: str,
        transfers: list[TokenTransfer],
    ) -> WalletActivity:
        tokens_sent = self._token_labels(transfers, "out")
        tokens_received = self._token_labels(transfers, "in")
        activity_type = "possible_swap" if tokens_sent and tokens_received else "token_transfer"

        return WalletActivity(
            tx_hash=tx_hash,
            timestamp=max((transfer.timestamp for transfer in transfers), default=0),
            activity_type=activity_type,
            summary=self._build_summary(activity_type, tokens_sent, tokens_received, 0.0, 0.0),
            tokens_sent=tokens_sent,
            tokens_received=tokens_received,
            eth_sent=0.0,
            eth_received=0.0,
            protocol_hint=None,
            is_failed=False,
        )

    def _detect_activity_type(
        self,
        transaction: NormalTransaction,
        tokens_sent: list[str],
        tokens_received: list[str],
        eth_sent: float,
        eth_received: float,
    ) -> str:
        if transaction.is_failed:
            return "failed_transaction"

        if (
            tokens_sent
            and tokens_received
            or eth_sent > 0
            and tokens_received
            or tokens_sent
            and eth_received > 0
        ):
            return "possible_swap"

        if self._looks_like_defi(transaction.function_name):
            return "possible_defi_activity"

        if tokens_sent or tokens_received:
            return "token_transfer"

        if eth_sent > 0 or eth_received > 0:
            return "eth_transfer"

        return "contract_interaction"

    def _build_summary(
        self,
        activity_type: str,
        tokens_sent: list[str],
        tokens_received: list[str],
        eth_sent: float,
        eth_received: float,
    ) -> str:
        parts: list[str] = []

        if eth_sent:
            parts.append(f"sent {format_amount(eth_sent)} ETH")
        if eth_received:
            parts.append(f"received {format_amount(eth_received)} ETH")
        if tokens_sent:
            parts.append(f"sent {', '.join(tokens_sent)}")
        if tokens_received:
            parts.append(f"received {', '.join(tokens_received)}")

        if parts:
            return "; ".join(parts)

        return activity_type.replace("_", " ")

    def _token_labels(self, transfers: list[TokenTransfer], direction: str) -> list[str]:
        return [
            f"{format_amount(transfer.amount)} {transfer.token_symbol}"
            for transfer in transfers
            if transfer.direction == direction
        ]

    def _looks_like_defi(self, function_name: str | None) -> bool:
        if not function_name:
            return False
        function_name_lower = function_name.lower()
        return any(keyword in function_name_lower for keyword in DEFI_KEYWORDS)

    def _wei_to_eth(self, value: Any) -> float:
        return self._safe_int(value) / 10**18

    def _token_amount(self, value: Any, decimals: int) -> float:
        return self._safe_int(value) / 10**decimals

    def _safe_int(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
