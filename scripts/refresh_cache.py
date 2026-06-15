"""
Run the ST scan and write a Pavel-friendly cache: base-symbol -> [exchanges flagging it ST].

Scheduled under pm2 (every ~4h) so Pavel's drafter reads a fresh local file at the market-review
stage instead of making a slow, failure-prone live exchange call inside every draft. ST status
moves on the order of days, so a few-hour cache is plenty fresh.

Output: <repo>/tg/data/st-markets.json
  { "updatedAt": <unix>, "count": N, "markets": { "ABC": ["bybit","mexc"], ... } }
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from st_tracker import scan  # noqa: E402


def main() -> None:
    rows = []
    # Resilient: one exchange failing (API hiccup / ccxt metadata change) must not lose the rest.
    for name, fn in (
        ("bybit", scan.scan_bybit),
        ("gateio", scan.scan_gateio),
        ("mexc", scan.scan_mexc),
        ("kucoin", scan.scan_kucoin),
        ("htx", scan.scan_htx),
    ):
        try:
            fn(rows)
        except Exception as exc:
            print(f"[st-cache] {name} failed: {exc}", file=sys.stderr)

    by_base: dict[str, set] = {}
    for r in rows:
        base = r["symbol"].split("/")[0].upper()
        by_base.setdefault(base, set()).add(r["exchange"])

    out = {
        "updatedAt": int(time.time()),
        "count": len(by_base),
        "markets": {k: sorted(v) for k, v in sorted(by_base.items())},
    }

    dest = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "tg", "data", "st-markets.json"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, dest)  # atomic — a reader never sees a half-written file
    print(f"[st-cache] wrote {len(by_base)} ST base symbols ({len(rows)} markets) -> {dest}")


if __name__ == "__main__":
    main()
