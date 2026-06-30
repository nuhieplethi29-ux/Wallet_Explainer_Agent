# Wallet Explainer Agent

A local CLI AI agent that explains recent Ethereum wallet activity in simple Vietnamese.

The agent accepts an Ethereum wallet address, fetches recent transactions from the Etherscan API V2, normalizes normal transactions and ERC-20 transfers, then sends the compact activity data to the OpenAI API to generate an easy-to-read Markdown explanation.

## Features

- Fetches 5-10 recent Ethereum transactions from Etherscan.
- Fetches related ERC-20 token transfers.
- Groups token transfers by transaction hash.
- Classifies basic wallet behavior:
  - ETH transfer
  - token transfer
  - possible swap
  - possible DeFi activity
  - failed transaction
- Generates a cautious Vietnamese explanation.
- Does not use a database, frontend, Docker, FastAPI, Streamlit, web3.py, or pandas.

## Requirements

- Python 3.10+
- uv
- Etherscan API key
- OpenAI API key

## Installation

From the project directory:

```bash
uv sync
```

If `uv` is not installed yet, install it with:

```bash
pip install uv
```

## Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Update `.env`:

```env
ETHERSCAN_API_KEY=your_etherscan_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Environment variables:

- `ETHERSCAN_API_KEY`: your Etherscan API key.
- `OPENAI_API_KEY`: your OpenAI API key.
- `OPENAI_MODEL`: the OpenAI model used for explanation. Defaults to `gpt-4.1-mini`.

Do not commit `.env` to Git.

## Usage

```bash
uv run python main.py --wallet 0xabc... --limit 10
```

Example:

```bash
uv run python main.py --wallet 0x0000000000000000000000000000000000000000 --limit 5
```

Use a different chain ID if needed:

```bash
uv run python main.py --wallet 0xabc... --limit 10 --chainid 1
```

CLI arguments:

- `--wallet`: required Ethereum wallet address in `0x` + 40 hex characters format.
- `--limit`: optional number of recent transactions to fetch. Defaults to `10`.
- `--chainid`: optional Etherscan V2 chain ID. Defaults to `1` for Ethereum mainnet.

Show help:

```bash
uv run python main.py --help
```

## Output

The agent prints Vietnamese Markdown to the terminal with these sections:

```md
## Tom tat vi

## Hoat dong gan day

## Suy luan hanh vi

## Luu y
```

The explanation only uses the provided transaction data. The agent does not guess the wallet owner's identity and does not provide financial advice.

## Source Structure

```txt
wallet-explainer-agent/
|-- main.py
|-- pyproject.toml
|-- .env.example
|-- README.md
`-- src/
    |-- __init__.py
    |-- config.py
    |-- constants.py
    |-- models.py
    |-- app.py
    |-- clients/
    |   |-- __init__.py
    |   `-- etherscan_client.py
    |-- services/
    |   |-- __init__.py
    |   |-- wallet_activity_service.py
    |   `-- ai_explainer.py
    `-- utils/
        |-- __init__.py
        |-- validators.py
        `-- formatters.py
```

## Processing Flow

1. `main.py` reads CLI arguments.
2. `WalletExplainerApp` validates the wallet address.
3. `EtherscanClient` calls the Etherscan API V2:
   - `account/txlist` for normal transactions.
   - `account/tokentx` for ERC-20 transfers.
4. `WalletActivityService` normalizes raw data into `WalletActivity` objects.
5. `OpenAIExplainer` sends compact JSON activity data to OpenAI.
6. The Vietnamese Markdown explanation is printed to the terminal.

## Activity Classification

- `eth_transfer`: a transaction has an ETH value and the wallet is the sender or receiver.
- `token_transfer`: a transaction has incoming or outgoing ERC-20 transfers.
- `possible_swap`: a transaction contains token out and token in, ETH out and token in, or token out and ETH in.
- `possible_defi_activity`: `functionName` contains keywords such as `supply`, `deposit`, `withdraw`, `borrow`, `repay`, `stake`, `unstake`, or `claim`.
- `failed_transaction`: Etherscan reports `isError == "1"` or `txreceipt_status == "0"`.

These are simple heuristics, so the final explanation should use cautious wording such as "co ve", "co kha nang", and "dua tren du lieu gan day".

## Error Handling

The agent reports clear errors for:

- Missing `ETHERSCAN_API_KEY`.
- Missing `OPENAI_API_KEY`.
- Invalid wallet address.
- No recent transactions.
- Etherscan API errors or timeouts.
- OpenAI API errors or empty output.

## Security Notes

- Do not hardcode API keys in source code.
- Store secrets in `.env`.
- Do not treat the output as financial advice.
- The analysis only covers a small number of recent transactions, so it may miss broader context.

## Quick Checks

Compile the source:

```bash
python -m compileall main.py src
```

Check CLI help:

```bash
python main.py --help
```
