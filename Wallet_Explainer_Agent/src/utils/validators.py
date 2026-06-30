from __future__ import annotations

import re


ETH_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")


def validate_wallet_address(wallet: str) -> str:
    normalized = wallet.strip()
    if not ETH_ADDRESS_RE.fullmatch(normalized):
        raise ValueError("Invalid wallet address. Expected a 0x-prefixed 40-byte Ethereum address.")
    return normalized
