# src/db.py
from __future__ import annotations
import os
import pandas as pd
from sqlalchemy import create_engine, text

def _engine():
    url = os.getenv("DATABASE_URL")
    return create_engine(url, pool_pre_ping=True) if url else None

def _clean_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce types & replace NaN/None with proper None for DB insert/update."""
    import numpy as np
    out = df.copy()

    int_cols = [
        "clinicaltrials_n", "pubmed_n",
        "year_min", "year_max",
        "quality_rating", "sample_size_min",
    ]
    float_cols = ["effect_size_estimate"]

    for c in int_cols:
        if c in out.columns:
            s = pd.to_numeric(out[c], errors="coerce")
            out[c] = [
                int(x) if pd.notna(x) and not isinstance(x, (str, list, dict)) else None
                for x in s
            ]

    for c in float_cols:
        if c in out.columns:
            s = pd.to_numeric(out[c], errors="coerce")
            out[c] = [
                float(x) if pd.notna(x) and not isinstance(x, (str, list, dict)) else None
                for x in s
            ]

    for c in ("study_types", "countries"):
        if c in out.columns:
            out[c] = out[c].apply(lambda v: v if isinstance(v, (list, tuple)) else None)

    for c in ("trials_url", "articles_url", "evidence_direction",
              "source", "last_updated", "condition", "therapy"):
        if c in out.columns:
            out[c] = out[c].astype(object).where(out[c].notna(), None)

    return out


def upsert_pairs(df: pd.DataFrame) -> bool:
    eng = _engine()
    if not eng or df is None or df.empty:
        return False

    cols = [
        "condition","therapy","clinicaltrials_n","pubmed_n",
        "trials_url","articles_url","year_min","year_max",
        "study_types","countries","evidence_direction",
        "effect_size_estimate","quality_rating","sample_size_min",
        "source","last_updated"
    ]
    payload = df[[c for c in cols if c in df.columns]].copy()
    payload = _clean_for_db(payload)

    with eng.begin() as con:
        for r in payload.to_dict("records"):
            con.execute(text("""
                insert into evidence_pairs
                (condition,therapy,clinicaltrials_n,pubmed_n,
                 trials_url,articles_url,year_min,year_max,study_types,countries,
                 evidence_direction,effect_size_estimate,quality_rating,sample_size_min,source,last_updated)
                values
                (:condition,:therapy,:clinicaltrials_n,:pubmed_n,
                 :trials_url,:articles_url,:year_min,:year_max,:study_types,:countries,
                 :evidence_direction,:effect_size_estimate,:quality_rating,:sample_size_min,:source,:last_updated)
                on conflict (condition,therapy) do update set
                  clinicaltrials_n=excluded.clinicaltrials_n,
                  pubmed_n=excluded.pubmed_n,
                  trials_url=excluded.trials_url,
                  articles_url=excluded.articles_url,
                  year_min=excluded.year_min,
                  year_max=excluded.year_max,
                  study_types=excluded.study_types,
                  countries=excluded.countries,
                  evidence_direction=excluded.evidence_direction,
                  effect_size_estimate=excluded.effect_size_estimate,
                  quality_rating=excluded.quality_rating,
                  sample_size_min=excluded.sample_size_min,
                  source=excluded.source,
                  last_updated=excluded.last_updated;
            """), r)
    return True

def read_pairs() -> pd.DataFrame | None:
    eng = _engine()
    if not eng: return None
    return pd.read_sql("select * from evidence_pairs", eng)