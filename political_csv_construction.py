"""Convert political response JSONL files, or a log-probability CSV, into analysis tables."""

import argparse
import json
import math
from pathlib import Path

import pandas as pd

from political_query_construction import IDENTITY_PAIRS


def read_responses(source):
    rows = []
    for model in ["gpt_3_5", "gpt_4"]:
        for identity_a, identity_b in IDENTITY_PAIRS:
            folder = source / f"data_{model}" / f"{identity_a}_{identity_b}"
            files = sorted(folder.glob("*_rated.jsonl"))
            if not files:
                raise FileNotFoundError(f"No rated responses in {folder}")
            for path in files:
                with path.open(encoding="utf-8") as file:
                    for line in file:
                        record = json.loads(line)
                        rows.append({
                            "question": record["question"],
                            "option_A": record[f"option_{identity_a}"],
                            "option_B": record[f"option_{identity_b}"],
                            "agree_A": record[f"{identity_a}_agree"],
                            "agree_B": record[f"{identity_b}_agree"],
                            "empty_A": record[f"empty_{identity_a}"],
                            "empty_B": record[f"empty_{identity_b}"],
                            "model": model,
                            "identityA": identity_a,
                            "identityB": identity_b,
                            "topic": path.stem.removesuffix("_rated"),
                        })
    return pd.DataFrame(rows)


def write_csvs(log_data, output):
    percent = log_data.copy()
    for column in ["agree_A", "agree_B", "empty_A", "empty_B"]:
        percent[column] = log_data[column].map(lambda value: 100 * math.exp(value))
    percent.insert(7, "disagree_A", 100 - percent["agree_A"])
    percent.insert(8, "disagree_B", 100 - percent["agree_B"])

    output.mkdir(parents=True, exist_ok=True)
    for filename, data in [("pol_data.csv", log_data), ("pol_data_percent.csv", percent)]:
        data.to_csv(output / filename, index=False)
        for model in ["gpt_3_5", "gpt_4"]:
            (output / model).mkdir(exist_ok=True)
            data.loc[data["model"] == model].to_csv(output / model / filename, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original repository or pol_data.csv")
    parser.add_argument("output", type=Path, help="Directory for the six output CSVs")
    args = parser.parse_args()
    data = pd.read_csv(args.source) if args.source.is_file() else read_responses(args.source)
    write_csvs(data, args.output)
