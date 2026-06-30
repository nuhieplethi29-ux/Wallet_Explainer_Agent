from __future__ import annotations

import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explain recent Ethereum wallet activity.")
    parser.add_argument("--wallet", required=True, help="Ethereum wallet address to analyze.")
    parser.add_argument("--limit", type=int, default=10, help="Number of recent transactions to fetch.")
    parser.add_argument("--chainid", type=int, default=1, help="Etherscan V2 chain ID.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        from src.app import WalletExplainerApp

        app = WalletExplainerApp()
        app.run(wallet=args.wallet, limit=args.limit, chainid=args.chainid)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
