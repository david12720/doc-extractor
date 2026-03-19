import csv
from datetime import datetime
from pathlib import Path

from ..abstractions.cost_logger import CostLogger
from ..config.pricing import MODEL_PRICING_USD_PER_1M
from ..config.settings import GEMINI_TIER_THRESHOLD, USD_TO_ILS

_CSV_HEADERS = ["timestamp", "model", "tier", "input_tokens", "output_tokens", "cost_usd", "cost_ils"]


def _calc_cost(pricing: dict, input_tokens: int, output_tokens: int) -> tuple[float, str | None]:
    if "input_le" in pricing:
        if input_tokens <= GEMINI_TIER_THRESHOLD:
            rate_in, rate_out, tier = pricing["input_le"], pricing["output_le"], "<=200k"
        else:
            rate_in, rate_out, tier = pricing["input_gt"], pricing["output_gt"], ">200k"
    else:
        rate_in, rate_out, tier = pricing["input"], pricing["output"], None

    cost_usd = (input_tokens * rate_in + output_tokens * rate_out) / 1_000_000
    return cost_usd, tier


class CsvCostLogger(CostLogger):
    def __init__(self, log_path: Path):
        self._log_path = log_path
        self._total_usd = 0.0
        self._call_count = 0
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        if not self._log_path.exists():
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._log_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(_CSV_HEADERS)

    def log(self, model: str, input_tokens: int, output_tokens: int) -> None:
        pricing = MODEL_PRICING_USD_PER_1M.get(model)
        if not pricing:
            print(f"[cost] {model}: no pricing data (tokens: {input_tokens:,}in + {output_tokens:,}out)")
            return

        cost_usd, tier = _calc_cost(pricing, input_tokens, output_tokens)
        cost_ils = cost_usd * USD_TO_ILS
        self._total_usd += cost_usd
        self._call_count += 1

        tier_label = f" [{tier}]" if tier else ""
        print(f"[cost] {model}{tier_label}: {input_tokens:,} in + {output_tokens:,} out = ${cost_usd:.4f} (ILS {cost_ils:.3f})")

        with open(self._log_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                model, tier or "flat", input_tokens, output_tokens,
                f"{cost_usd:.6f}", f"{cost_ils:.4f}",
            ])

    def summary(self) -> None:
        total_ils = self._total_usd * USD_TO_ILS
        print(f"[cost] -- session total: ${self._total_usd:.4f} (ILS {total_ils:.3f}) across {self._call_count} call(s) --")

    def history(self, last: int | None = None) -> None:
        if not self._log_path.exists():
            print("No cost log found.")
            return

        with open(self._log_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        if not rows:
            print("Cost log is empty.")
            return

        if last is not None:
            rows = rows[-last:]

        total_usd = sum(float(r["cost_usd"]) for r in rows)
        total_ils = total_usd * USD_TO_ILS

        col_w = [19, 20, 8, 14, 15, 10, 10]
        header = _CSV_HEADERS
        sep = "-" * (sum(col_w) + len(col_w) * 3 + 1)

        print(sep)
        print("  ".join(h.ljust(w) for h, w in zip(header, col_w)))
        print(sep)
        for r in rows:
            print("  ".join(str(r[h]).ljust(w) for h, w in zip(header, col_w)))
        print(sep)
        print(f"  Total: {len(rows)} call(s)   ${total_usd:.4f}   ILS {total_ils:.3f}")
