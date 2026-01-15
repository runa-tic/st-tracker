import csv
from typing import List, Dict

import ccxt
import requests

OUTPUT_CSV = "st_markets.csv"


def write_row(rows: List[Dict[str, str]], exchange: str, symbol: str, risk_state: str, trade_url: str) -> None:
    rows.append(
        {
            "exchange": exchange,
            "symbol": symbol,
            "risk_state": risk_state,
            "trade_url": trade_url,
        }
    )


# =========================
# BYBIT — CCXT
# =========================

def scan_bybit(rows: List[Dict[str, str]]) -> None:
    ex = ccxt.bybit({"enableRateLimit": True})
    markets = ex.load_markets()

    for market in markets.values():
        if not market.get("spot"):
            continue
        info = market.get("info", {})
        if info.get("stTag") == "1" and info.get("status") == "Trading":
            url = f"https://www.bybit.com/trade/spot/{market['base']}/{market['quote']}"
            write_row(rows, "bybit", market["symbol"], "ST (monitoring, tradable)", url)


# =========================
# GATE.IO — CCXT
# =========================

def scan_gateio(rows: List[Dict[str, str]]) -> None:
    ex = ccxt.gateio({"enableRateLimit": True})
    markets = ex.load_markets()

    for market in markets.values():
        if not market.get("spot"):
            continue
        info = market.get("info", {})
        if info.get("st_tag") is True and info.get("trade_status") == "tradable":
            url = f"https://www.gate.io/trade/{market['base']}_{market['quote']}"
            write_row(rows, "gateio", market["symbol"], "ST (monitoring, tradable)", url)


# =========================
# MEXC — CCXT
# =========================

def scan_mexc(rows: List[Dict[str, str]]) -> None:
    ex = ccxt.mexc({"enableRateLimit": True})
    markets = ex.load_markets()

    for market in markets.values():
        if not market.get("spot"):
            continue
        info = market.get("info", {})
        if info.get("st") is True and info.get("status") == "1":
            url = f"https://www.mexc.com/exchange/{market['base']}_{market['quote']}"
            write_row(rows, "mexc", market["symbol"], "ST (monitoring, tradable)", url)


# =========================
# KUCOIN — CCXT
# =========================

def scan_kucoin(rows: List[Dict[str, str]]) -> None:
    ex = ccxt.kucoin({"enableRateLimit": True})
    markets = ex.load_markets()

    for market in markets.values():
        if not market.get("spot"):
            continue
        info = market.get("info", {})
        if info.get("st") is True and info.get("enableTrading") is True:
            url = f"https://www.kucoin.com/trade/{market['base']}-{market['quote']}"
            write_row(rows, "kucoin", market["symbol"], "ST (monitoring, tradable)", url)


# =========================
# HTX / HUOBI — DIRECT REST
# =========================

def scan_htx(rows: List[Dict[str, str]]) -> None:
    url = "https://api.huobi.pro/v1/common/symbols"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json().get("data", [])
    for symbol in data:
        tags = (symbol.get("tags") or "").lower()
        if symbol.get("state") != "online":
            continue
        if "st" not in tags.split(",") and tags != "st":
            if "st" not in tags:
                continue

        base = symbol["base-currency"].upper()
        quote = symbol["quote-currency"].upper()
        market_symbol = f"{base}/{quote}"

        trade_url = f"https://www.htx.com/trade/{base.lower()}_{quote.lower()}"
        write_row(rows, "htx", market_symbol, "ST (monitoring, tradable)", trade_url)


def main(output_csv: str = OUTPUT_CSV) -> None:
    rows: List[Dict[str, str]] = []

    scan_bybit(rows)
    scan_gateio(rows)
    scan_mexc(rows)
    scan_kucoin(rows)
    scan_htx(rows)

    with open(output_csv, "w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["exchange", "symbol", "risk_state", "trade_url"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_csv}")


if __name__ == "__main__":
    main()
