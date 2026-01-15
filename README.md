# ST Tracker

Scan multiple crypto exchanges for spot markets flagged as special treatment (ST) and emit a CSV report with trade URLs.

## Project structure

```
.
├── README.md
├── requirements.txt
├── scripts
│   └── run_scan.py
└── src
    └── st_tracker
        ├── __init__.py
        └── scan.py
```

## Requirements

- Python 3.10+
- Network access to exchange APIs

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the scan module directly (add `src` to `PYTHONPATH`):

```bash
PYTHONPATH=src python -m st_tracker.scan
```

Or use the helper script (it sets `PYTHONPATH` internally):

```bash
python scripts/run_scan.py
```

The script writes a CSV file named `st_markets.csv` in the working directory.

## Output format

The CSV file contains the following columns:

- `exchange`: Exchange identifier (bybit, gateio, mexc, kucoin, htx)
- `symbol`: Spot market symbol (e.g., `ABC/USDT`)
- `risk_state`: Human-friendly status label
- `trade_url`: Web UI trade URL for the market

## Notes

- Each exchange has different metadata keys for ST/monitoring flags; see `scan.py` for the exact rules.
- HTX (Huobi) uses a direct REST endpoint instead of CCXT.
- Rate limiting is enabled for CCXT clients.

## Building a macOS executable

Create a standalone macOS binary with `pyinstaller` (must be run on macOS):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
```

Build the executable from the repository root:

```bash
PYTHONPATH=src pyinstaller --name st-tracker --onefile --console scripts/run_scan.py
```

The compiled binary will be available at `dist/st-tracker`. Run it from the folder where you
want the `st_markets.csv` report to be generated:

```bash
./dist/st-tracker
```
