# Wallet Explainer Agent

Local CLI AI agent giup giai thich hoat dong gan day cua mot Ethereum wallet bang tieng Viet.

Agent nhan wallet address, lay cac giao dich gan nhat tu Etherscan API V2, chuan hoa du lieu giao dich va ERC-20 transfer, sau do gui sang OpenAI API de tao phan giai thich Markdown de hieu.

## Tinh nang

- Lay 5-10 giao dich Ethereum gan nhat tu Etherscan.
- Lay them ERC-20 token transfers lien quan den wallet.
- Nhom token transfers theo transaction hash.
- Phan loai hanh vi co ban:
  - ETH transfer
  - token transfer
  - possible swap
  - possible DeFi activity
  - failed transaction
- Giai thich ket qua bang tieng Viet voi ngon ngu than trong.
- Khong dung database, frontend, Docker, FastAPI, Streamlit, web3.py hoac pandas.

## Yeu cau

- Python 3.10+
- uv
- Etherscan API key
- OpenAI API key

## Cai dat

Trong thu muc project:

```bash
uv sync
```

Neu chua co `uv`, cai theo huong dan chinh thuc cua Astral:

```bash
pip install uv
```

## Cau hinh moi truong

Copy file mau:

```bash
cp .env.example .env
```

Tren Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Cap nhat `.env`:

```env
ETHERSCAN_API_KEY=your_etherscan_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Trong do:

- `ETHERSCAN_API_KEY`: API key tu Etherscan.
- `OPENAI_API_KEY`: API key tu OpenAI.
- `OPENAI_MODEL`: model OpenAI dung de giai thich, mac dinh la `gpt-4.1-mini`.

Khong commit file `.env` len Git.

## Cach chay

```bash
uv run python main.py --wallet 0xabc... --limit 10
```

Vi du:

```bash
uv run python main.py --wallet 0x0000000000000000000000000000000000000000 --limit 5
```

Dung chain ID khac neu can:

```bash
uv run python main.py --wallet 0xabc... --limit 10 --chainid 1
```

Tham so CLI:

- `--wallet`: bat buoc, Ethereum wallet address dang `0x` + 40 ky tu hex.
- `--limit`: tuy chon, so giao dich gan nhat can lay, mac dinh `10`.
- `--chainid`: tuy chon, Etherscan V2 chain ID, mac dinh `1` cho Ethereum mainnet.

Xem help:

```bash
uv run python main.py --help
```

## Output

Agent in Markdown tieng Viet ra terminal, gom cac phan:

```md
## Tom tat vi

## Hoat dong gan day

## Suy luan hanh vi

## Luu y
```

Noi dung chi dua tren du lieu giao dich duoc cung cap. Agent khong suy doan danh tinh chu vi va khong dua ra loi khuyen dau tu.

## Cau truc source

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

## Luong xu ly

1. `main.py` doc tham so CLI.
2. `WalletExplainerApp` validate wallet address.
3. `EtherscanClient` goi Etherscan API V2:
   - `account/txlist` de lay normal transactions.
   - `account/tokentx` de lay ERC-20 transfers.
4. `WalletActivityService` chuan hoa raw data thanh `WalletActivity`.
5. `OpenAIExplainer` gui du lieu compact JSON sang OpenAI.
6. Ket qua Markdown tieng Viet duoc in ra terminal.

## Cach phan loai hoat dong

- `eth_transfer`: giao dich co ETH value va wallet la sender hoac receiver.
- `token_transfer`: giao dich co ERC-20 transfer vao hoac ra.
- `possible_swap`: cung transaction co token out va token in, ETH out va token in, hoac token out va ETH in.
- `possible_defi_activity`: `functionName` co cac tu khoa nhu `supply`, `deposit`, `withdraw`, `borrow`, `repay`, `stake`, `unstake`, `claim`.
- `failed_transaction`: Etherscan bao `isError == "1"` hoac `txreceipt_status == "0"`.

Day chi la heuristic don gian, nen output dung ngon ngu than trong nhu "co ve", "co kha nang", "dua tren du lieu gan day".

## Xu ly loi

Agent bao loi ro rang cho cac truong hop:

- Thieu `ETHERSCAN_API_KEY`.
- Thieu `OPENAI_API_KEY`.
- Wallet address khong hop le.
- Khong co transaction gan day.
- Etherscan API loi hoac timeout.
- OpenAI API loi hoac tra ve output rong.

## Ghi chu bao mat

- Khong hardcode API key trong source.
- Dat secret trong `.env`.
- Khong dung ket qua nay lam loi khuyen dau tu.
- Chi phan tich tren mot so giao dich gan day, nen co the thieu boi canh.

## Kiem tra nhanh

Compile source:

```bash
python -m compileall main.py src
```

Kiem tra CLI help:

```bash
python main.py --help
```
