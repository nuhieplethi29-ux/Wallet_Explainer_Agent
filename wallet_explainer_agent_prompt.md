# Wallet Explainer Agent - Code Generation Prompt

Bạn là senior Python engineer. Hãy generate source code cho một local CLI crypto AI agent tên **Wallet Explainer Agent**.

## Mục tiêu

User nhập Ethereum wallet address, agent lấy 5-10 transaction gần nhất từ Etherscan API, sau đó dùng OpenAI API giải thích hành vi ví bằng tiếng Việt dễ hiểu.

Chỉ cần generate code. Không cần chạy thử. Không cần unit test. Không cần docs dài.

## Tech stack

- Python 3.10+
- uv
- requests
- python-dotenv
- openai
- Etherscan API V2
- OpenAI API

Không dùng database, frontend, Docker, FastAPI, Streamlit, web3.py, pandas.

## Command mong muốn

```bash
uv run python main.py --wallet 0xabc... --limit 10
```

Arguments:

- `--wallet`: required
- `--limit`: optional, default `10`
- `--chainid`: optional, default `1`

## Source structure

```txt
wallet-explainer-agent/
├── main.py
├── pyproject.toml
├── .env.example
└── src/
    ├── __init__.py
    ├── config.py
    ├── constants.py
    ├── models.py
    ├── app.py
    ├── clients/
    │   ├── __init__.py
    │   └── etherscan_client.py
    ├── services/
    │   ├── __init__.py
    │   ├── wallet_activity_service.py
    │   └── ai_explainer.py
    └── utils/
        ├── __init__.py
        ├── validators.py
        └── formatters.py
```

## pyproject.toml

```toml
[project]
name = "wallet-explainer-agent"
version = "0.1.0"
description = "Simple AI agent that explains recent Ethereum wallet activity"
requires-python = ">=3.10"
dependencies = [
    "requests",
    "python-dotenv",
    "openai",
]
```

## .env.example

```env
ETHERSCAN_API_KEY=your_etherscan_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

## Main classes

### Config

File: `src/config.py`

- Load `.env`
- Read `ETHERSCAN_API_KEY`
- Read `OPENAI_API_KEY`
- Read `OPENAI_MODEL`
- Raise clear error if missing API keys

### EtherscanClient

File: `src/clients/etherscan_client.py`

Use endpoint:

```txt
https://api.etherscan.io/v2/api
```

Methods:

```python
get_normal_transactions(address: str, limit: int, chainid: int = 1) -> list[dict]
get_erc20_transfers(address: str, limit: int, chainid: int = 1) -> list[dict]
```

Normal transactions params:

```txt
chainid=<chainid>
module=account
action=txlist
address=<wallet>
startblock=0
endblock=99999999
page=1
offset=<limit>
sort=desc
apikey=<ETHERSCAN_API_KEY>
```

ERC-20 transfers params:

```txt
chainid=<chainid>
module=account
action=tokentx
address=<wallet>
page=1
offset=<limit * 3>
sort=desc
apikey=<ETHERSCAN_API_KEY>
```

Use `requests.Session`, timeout, and clear error handling.

### WalletActivityService

File: `src/services/wallet_activity_service.py`

Responsibilities:

- Fetch normal txs and ERC-20 transfers
- Group token transfers by tx hash
- Convert raw data into clean `WalletActivity`
- Detect simple behavior:
  - ETH transfer
  - token transfer
  - possible swap
  - possible DeFi activity
  - failed transaction

### OpenAIExplainer

File: `src/services/ai_explainer.py`

Responsibilities:

- Convert activities to compact JSON
- Send to OpenAI
- Return Vietnamese Markdown explanation

### WalletExplainerApp

File: `src/app.py`

Responsibilities:

- Validate wallet
- Call activity service
- Call AI explainer
- Print final output

## Dataclasses

File: `src/models.py`

```python
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
```

## Simple detection rules

### ETH transfer

If `value > 0`:

- `from == wallet`: sent ETH
- `to == wallet`: received ETH

Convert wei:

```python
eth_value = int(value) / 10**18
```

### ERC-20 transfer

Convert token amount:

```python
amount = int(value) / 10**int(tokenDecimal)
```

Direction:

- `from == wallet`: `out`
- `to == wallet`: `in`

### Possible swap

If same tx hash has:

- token out and token in
- ETH out and token in
- token out and ETH in

Set:

```txt
activity_type = "possible_swap"
```

Use cautious wording. Do not claim it is definitely a swap.

### Possible DeFi activity

If `functionName` contains:

```python
["supply", "deposit", "withdraw", "borrow", "repay", "stake", "unstake", "claim"]
```

Set:

```txt
activity_type = "possible_defi_activity"
```

### Failed transaction

If `isError == "1"` or `txreceipt_status == "0"`, set `is_failed = True`.

## Constants

File: `src/constants.py`

```python
KNOWN_TOKENS = {
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",
    "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "WETH",
}

DEFI_KEYWORDS = [
    "supply",
    "deposit",
    "withdraw",
    "borrow",
    "repay",
    "stake",
    "unstake",
    "claim",
]
```

## OpenAI prompt

System prompt:

```txt
You are a crypto wallet explainer assistant.

Explain recent Ethereum wallet activity in simple Vietnamese.

Rules:
- Only use the provided wallet activity data.
- Do not invent wallet owner identity.
- Do not provide financial advice.
- Do not recommend buying, selling, shorting, longing, or copying this wallet.
- Use cautious language: "có vẻ", "có khả năng", "dựa trên dữ liệu gần đây".
- If the data is limited, say so clearly.
- Output Markdown in Vietnamese.
```

User prompt template:

```txt
Hãy giải thích ví Ethereum sau bằng tiếng Việt.

Wallet:
{wallet_address}

Activities:
{activities_json}

Output format:

## Tóm tắt ví

## Hoạt động gần đây

## Suy luận hành vi

## Lưu ý
```

## Output format

OpenAI should return Vietnamese Markdown:

```md
## Tóm tắt ví

...

## Hoạt động gần đây

- ...

## Suy luận hành vi

- ...

## Lưu ý

- Phân tích chỉ dựa trên vài giao dịch gần nhất.
- Đây không phải lời khuyên đầu tư.
```

## Error handling

Handle clearly:

- Missing `ETHERSCAN_API_KEY`
- Missing `OPENAI_API_KEY`
- Invalid wallet address
- Empty transactions
- Etherscan API error
- Network timeout
- OpenAI API error

## Code quality

Code must be:

- simple
- clean
- OOP
- modular
- type-hinted
- no tests
- no docs
- no over-engineering
- no hardcoded API keys
- no business logic in `main.py`
