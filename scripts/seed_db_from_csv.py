# scripts/seed_db_from_csv.py
from pathlib import Path
import sys
import pandas as pd

# add repo root for "src" import
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.db import upsert_pairs

CSV_PATHS = [
    ROOT / "data" / "raw" / "evidence_counts.csv",
    ROOT / "data" / "evidence_counts.csv",  # fallback if your file is here
]

def load_csv() -> pd.DataFrame:
    for p in CSV_PATHS:
        if p.exists():
            df = pd.read_csv(p)
            print(f"📄 Loaded {p} with {len(df)} rows")
            return df
    raise FileNotFoundError("Could not find evidence_counts.csv in data/raw/ or data/")

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    # match DB schema; add missing columns with safe defaults
    defaults = {
        "trials_url": None,
        "articles_url": None,
        "year_min": None,
        "year_max": None,
        "study_types": None,
        "countries": None,
        "evidence_direction": "Positive",
        "effect_size_estimate": None,
        "quality_rating": None,
        "sample_size_min": None,
        "source": None,
        "last_updated": None,
    }
    for k, v in defaults.items():
        if k not in df.columns:
            df[k] = v

    # normalize expected base columns
    if "articles_n" in df.columns and "pubmed_n" not in df.columns:
        df = df.rename(columns={"articles_n": "pubmed_n"})
    # title case for nicer UI
    for c in ("condition", "therapy"):
        if c in df.columns:
            df[c] = df[c].astype(str).str.title()
    return df

def main():
    df = load_csv()
    df = ensure_columns(df)
    ok = upsert_pairs(df)
    print("✅ Upsert complete" if ok else "⚠️ Upsert skipped (no engine or empty df).")

if __name__ == "__main__":
    main()