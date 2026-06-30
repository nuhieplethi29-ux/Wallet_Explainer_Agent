from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TokenTransfer:
    tx_hash: str
    timestamp: int
    from_address: str
    to_address: str
    token_symbol: str
    token_name: str
    token_decimal: int
    value_raw: str
    direction: str
    amount: float


@dataclass
class NormalTransaction:
    tx_hash: str
    timestamp: int
    from_address: str
    to_address: str
    eth_value: float
    function_name: str | None
    method_id: str | None
    is_failed: bool


@dataclass
class WalletActivity:
    tx_hash: str
    timestamp: int
    activity_type: str
    summary: str
    tokens_sent: list[str]
    tokens_received: list[str]
    eth_sent: float
    eth_received: float
    protocol_hint: str | None
    is_failed: bool
