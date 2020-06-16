# Gaica (Shinsei Bank)
https://www.gaica.jp/

Fetch balance and domestic/international spendings from command line (残高照会)

## Setup
```bash
pip install -r requirements.txt
```

## Docker

```bash
docker build -f Dockerfile -t premy/gaica-server:latest .
docker run -d -p 4783:4783 premy/gaica-server
```

## Usage

### Environment variables (credentials)
```bash
export GAICA_USER=...
export GAICA_PASS=...
```

### CLI
```bash
python gaica.py
```

### Result
```
{
    "通貨コード": "JPY",
    "金額": "36,486.00",
    "国内ショッピング": {
        "1日": "2,300 円",
        "1ヶ月": "22,456 円"
    },
    "海外ショッピング": {
        "1日": "0 円",
        "1ヶ月": "0 円"
    },
    "海外現金引出": {
        "1日": "0 円",
        "1ヶ月": "0 円"
    }
}
```
