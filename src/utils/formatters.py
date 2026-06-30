from __future__ import annotations


def format_amount(value: float) -> str:
    if value == 0:
        return "0"
    if value < 0.000001:
        return f"{value:.10f}".rstrip("0").rstrip(".")
    if value < 1:
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return f"{value:.4f}".rstrip("0").rstrip(".")
