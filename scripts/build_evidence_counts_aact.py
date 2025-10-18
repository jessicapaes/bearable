"""
build_evidence_counts_aact.py
One-shot builder for PainReliefMap Evidence Explorer:
- Reads AACT flat files (studies/conditions/interventions) from data/raw/
- Computes ClinicalTrials.gov trial counts per (condition, therapy)
- Fetches PubMed counts per (condition, therapy)
- Adds link + filter metadata columns
- Saves a single CSV to data/raw/evidence_counts.csv

Run:
  conda activate painreliefmap312
  pip install pandas requests
  python -u scripts/build_evidence_counts_aact.py
"""

from pathlib import Path
import re
import time
from typing import List, Dict, Tuple

import pandas as pd
import requests
from urllib.parse import quote_plus

# =========================
# Configuration
# =========================

# Canonical conditions (31)
conditions = [
    "Addiction","Anxiety","Burnout","Cancer Pain","Chronic Fatigue Syndrome",
    "Chronic Pain","Depression","Eating Disorders","Endometriosis","Fibromyalgia",
    "Headache","Infertility","Insomnia","Irritable Bowel Syndrome","Knee Pain",
    "Low Back Pain","Menopause","Migraine","Myofascial Pain","Neck Pain",
    "Neuropathic Pain","Obsessive-Compulsive Disorder","Osteoarthritis",
    "Perimenopause","Polycystic Ovary Syndrome","Postoperative Pain",
    "Post-Traumatic Stress Disorder","Rheumatoid Arthritis","Schizophrenia",
    "Shoulder Pain","Stress",
]

# Canonical therapies (11) — includes Ayurveda
therapies = [
    "Acupuncture","Aromatherapy","Ayurveda","Cognitive Behavioural Therapy","Exercise Therapy",
    "Herbal","Massage","Meditation","Qi Gong","Tai Chi","Yoga",
]

condition_groups = {
    "Functional & Systemic": ["Chronic Fatigue Syndrome","Irritable Bowel Syndrome","Stress"],
    "Mental Health": ["Addiction","Anxiety","Burnout","Depression","Eating Disorders",
                      "Obsessive-Compulsive Disorder","Post-Traumatic Stress Disorder","Schizophrenia"],
    "Musculoskeletal & Pain": ["Chronic Pain","Fibromyalgia","Low Back Pain","Neck Pain",
                               "Knee Pain","Shoulder Pain","Myofascial Pain","Osteoarthritis",
                               "Neuropathic Pain","Cancer Pain","Postoperative Pain","Migraine",
                               "Headache","Rheumatoid Arthritis"],
    "Women's Health": ["Endometriosis","Infertility","Menopause","Perimenopause","Polycystic Ovary Syndrome"],
}
def group_for_condition(c: str) -> str:
    for g, members in condition_groups.items():
        if c in members:
            return g
    return "Other"

# Aliases to improve matching against AACT and PubMed
COND_ALIASES: Dict[str, List[str]] = {
    "Addiction": ["substance use disorder","substance-related disorders","addiction"],
    "Chronic Fatigue Syndrome": ["myalgic encephalomyelitis","me/cfs","chronic fatigue syndrome"],
    "Headache": ["headache disorders","headache disorders, primary","headache"],
    "Myofascial Pain": ["myofascial pain syndromes","myofascial pain"],
    "Neuropathic Pain": ["neuropathic pain","neuralgia","peripheral neuropathy"],
    "Obsessive-Compulsive Disorder": ["obsessive-compulsive disorder","ocd"],
    "Post-Traumatic Stress Disorder": ["post-traumatic stress disorder","ptsd"],
}
for c in conditions:
    COND_ALIASES.setdefault(c, [c.lower()])

THER_ALIASES: Dict[str, List[str]] = {
    "Ayurveda": ["ayurveda","ayurvedic","ayurvedic medicine"],
    "Cognitive Behavioural Therapy": ["cognitive behavioral therapy","cbt","cognitive behaviour therapy"],
    "Qi Gong": ["qigong","chi kung","qi gong"],
    "Tai Chi": ["tai chi","taiji","tai ji"],
    "Herbal": ["herbal","herbal medicine","phytotherapy"],
    "Exercise Therapy": ["exercise therapy","therapeutic exercise","physical exercise","exercise intervention"],
    "Meditation": ["meditation","mindfulness","mbsr","mindfulness-based stress reduction"],
    "Massage": ["massage","massage therapy"],
    "Acupuncture": ["acupuncture","electroacupuncture"],
    "Aromatherapy": ["aromatherapy","essential oils"],
    "Yoga": ["yoga"],
}
for t in therapies:
    THER_ALIASES.setdefault(t, [t.lower()])

# PubMed API
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_HEADERS = {"User-Agent": "PainReliefMap/1.0 (+capstone)"}
# polite pacing to respect NCBI (<= 3 req/s)
PUBMED_DELAY_SEC = 0.35

# =========================
# Helpers (AACT files)
# =========================

def find_one(folder: Path, stem: str) -> Path | None:
    """Return the first file matching studies*/conditions*/interventions* in folder."""
    for pat in (f"{stem}*.txt", f"{stem}*.txt.gz", f"{stem}*.csv", f"{stem}*.csv.gz"):
        hits = list(folder.glob(pat))
        if hits:
            return hits[0]
    return None

def read_table_any(path: Path, cols: List[str]) -> pd.DataFrame:
    """
    Read AACT flat files or CSVs with robust delimiter detection.
    - Detect '|' vs ',' by peeking at the first line
    - Handle common null markers
    - Return only requested columns when present
    """
    with open(path, "rb") as f:
        head = f.read(8192)
    try:
        first = head.decode("utf-8", errors="ignore").splitlines()[0]
    except Exception:
        first = ""

    sep = "|" if ("|" in first) or path.suffix.lower() in {".txt", ".gz"} else ","

    read_kwargs = dict(
        sep=sep,
        engine="python",               # tolerant parser
        dtype=str,                     # keep nct_id formatting intact
        na_values=["", "NULL", r"\N"], # common null markers
        keep_default_na=True,
        on_bad_lines="skip",
    )
    df = pd.read_csv(path, **read_kwargs)

    keep = [c for c in cols if c in df.columns]
    if keep:
        df = df[keep].copy()
    return df

def contains_any(series: pd.Series, terms: List[str]) -> pd.Series:
    """Vectorized OR of substring matches (case-insensitive)."""
    mask = pd.Series(False, index=series.index)
    s = series.fillna("").str.lower()
    for term in terms:
        mask |= s.str.contains(re.escape(term), regex=True)
    return mask

# =========================
# PubMed helpers
# =========================

def build_pubmed_term(condition: str, therapy: str) -> str:
    # broaden with aliases; de-duplicate while preserving order
    c_terms = list(dict.fromkeys([condition] + COND_ALIASES.get(condition, [])))
    t_terms = list(dict.fromkeys([therapy] + THER_ALIASES.get(therapy, [])))
    c_block = " OR ".join([f'"{t}"' for t in c_terms])
    t_block = " OR ".join([f'"{t}"' for t in t_terms])
    # If you prefer fewer false positives, scope to Title/Abstract by appending [tiab] to each block.
    # return f"(({c_block})[tiab]) AND (({t_block})[tiab])"
    return f"({c_block}) AND ({t_block})"

def pubmed_count(term: str) -> int:
    params = {"db":"pubmed","retmode":"json","term":term}
    r = requests.get(EUTILS, params=params, timeout=25, headers=PUBMED_HEADERS)
    if r.status_code == 200:
        try:
            return int(r.json()["esearchresult"]["count"])
        except Exception:
            return 0
    return 0

def ctgov_search(cond: str, ther: str) -> str:
    q = quote_plus(f"({cond}) AND ({ther})")
    return f"https://clinicaltrials.gov/search?cond={q}"

def pubmed_search(cond: str, ther: str) -> str:
    term = quote_plus(build_pubmed_term(cond, ther))
    return f"https://pubmed.ncbi.nlm.nih.gov/?term={term}"

# =========================
# Main
# =========================

def main():
    print("🔎 Starting AACT + PubMed build...")
    root = Path(__file__).resolve().parents[1]
    aact_dir = root / "data" / "raw"

    if not aact_dir.exists():
        raise FileNotFoundError(f"Missing folder {aact_dir}. Extract AACT Flat Text Files here.")

    studies_fp = find_one(aact_dir, "studies")
    conds_fp   = find_one(aact_dir, "conditions")
    inter_fp   = find_one(aact_dir, "interventions")

    if not studies_fp or not conds_fp or not inter_fp:
        raise FileNotFoundError(
            "Could not find studies*/conditions*/interventions* in data/raw/\n"
            f"Found: studies={studies_fp}, conditions={conds_fp}, interventions={inter_fp}"
        )

    print("📄 Reading AACT flat files:")
    print(" -", studies_fp.name)
    print(" -", conds_fp.name)
    print(" -", inter_fp.name)

    studies = read_table_any(studies_fp, ["nct_id","study_type"])
    conditions_df = read_table_any(conds_fp, ["nct_id","name"])
    interventions_df = read_table_any(inter_fp, ["nct_id","name"])

    # Normalize ids and lowercased names for matching
    for df in (conditions_df, interventions_df, studies):
        if "nct_id" in df.columns:
            df["nct_id"] = df["nct_id"].astype(str)

    conditions_df["name_l"] = conditions_df["name"].astype(str).str.lower()
    interventions_df["name_l"] = interventions_df["name"].astype(str).str.lower()

    print("🧮 Building condition hits...")
    cond_hits_parts = []
    for canon, aliases in COND_ALIASES.items():
        mask = contains_any(conditions_df["name_l"], aliases)
        if mask.any():
            tmp = conditions_df.loc[mask, ["nct_id"]].copy()
            tmp["condition"] = canon
            cond_hits_parts.append(tmp)
    cond_hits = pd.concat(cond_hits_parts, ignore_index=True) if cond_hits_parts else pd.DataFrame(columns=["nct_id","condition"])

    print("🧮 Building therapy hits...")
    ther_hits_parts = []
    for canon, aliases in THER_ALIASES.items():
        mask = contains_any(interventions_df["name_l"], aliases)
        if mask.any():
            tmp = interventions_df.loc[mask, ["nct_id"]].copy()
            tmp["therapy"] = canon
            ther_hits_parts.append(tmp)
    ther_hits = pd.concat(ther_hits_parts, ignore_index=True) if ther_hits_parts else pd.DataFrame(columns=["nct_id","therapy"])

    print("🔗 Joining & counting trials...")
    pair = cond_hits.merge(ther_hits, on="nct_id", how="inner")

    # If you want ONLY interventional trials, uncomment:
    # pair = pair.merge(studies, on="nct_id", how="left")
    # pair = pair[pair["study_type"] == "Interventional"]

    counts = (
        pair.groupby(["condition","therapy"])["nct_id"]
            .nunique()
            .reset_index(name="clinicaltrials_n")
    )

    # Full grid (31 × 11 = 341) to include zeros and ensure Ayurveda appears
    grid = pd.MultiIndex.from_product([conditions, therapies], names=["condition","therapy"]).to_frame(index=False)
    out = grid.merge(counts, on=["condition","therapy"], how="left").fillna({"clinicaltrials_n": 0})
    out["clinicaltrials_n"] = out["clinicaltrials_n"].astype(int)

    # PubMed counts (polite pacing)
    print("📚 Fetching PubMed counts (polite pacing)...")
    pairs = out[["condition","therapy"]].to_records(index=False)
    pubmed_results: Dict[Tuple[str,str], int] = {}
    for i, (cond, ther) in enumerate(pairs, 1):
        term = build_pubmed_term(cond, ther)
        n = pubmed_count(term)
        pubmed_results[(cond, ther)] = n
        print(f"[{i}/{len(pairs)}] {cond} × {ther} → PubMed {n}")
        time.sleep(PUBMED_DELAY_SEC)

    out["pubmed_n"] = out.apply(lambda r: pubmed_results.get((r["condition"], r["therapy"]), 0), axis=1)

    # Groups/metadata
    out["condition_group"] = out["condition"].map(group_for_condition)
    out["therapy_group"] = out["therapy"].map(
        lambda t: "Traditional" if t in ["Acupuncture","Herbal","Ayurveda"]
        else "Mind–Body" if t in ["Meditation","Yoga","Tai Chi","Qi Gong"]
        else "Behavioural & Lifestyle"
    )
    out["source"] = "AACT (flat files) + PubMed eSearch"
    out["country"] = "Worldwide"
    out["last_updated"] = pd.Timestamp.today().strftime("%Y-%m-%d")

    # NEW link + filter columns (nullable-safe)
    out["trials_url"]   = out.apply(lambda r: ctgov_search(r["condition"], r["therapy"]), axis=1)
    out["articles_url"] = out.apply(lambda r: pubmed_search(r["condition"], r["therapy"]), axis=1)
    out["year_min"] = None
    out["year_max"] = None
    out["study_types"] = None          # e.g., ["Interventional","Observational"]
    out["countries"] = None            # e.g., ["USA","Australia"]
    out["evidence_direction"] = "Positive"
    out["effect_size_estimate"] = None
    out["quality_rating"] = None
    out["sample_size_min"] = None

    # Column order
    cols = [
        "condition_group","condition","therapy_group","therapy",
        "clinicaltrials_n","pubmed_n",
        "trials_url","articles_url",
        "year_min","year_max","study_types","countries",
        "evidence_direction","effect_size_estimate","quality_rating","sample_size_min",
        "source","country","last_updated"
    ]
    out = out[cols]

    # Save CSV
    out_path = Path("data/raw/evidence_counts.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"✅ Saved {len(out)} rows → {out_path.resolve()}")

    # OPTIONAL: upsert to Supabase if DATABASE_URL is set
    try:
        from src.db import upsert_pairs
        ok = upsert_pairs(out)
        print("⬆️  Supabase upsert:", "OK" if ok else "skipped")
    except Exception as e:
        print("Supabase upsert skipped:", e)

    print("🎉 Done! Launch your app with:  streamlit run app/app.py")

# Entrypoint
if __name__ == "__main__":
    main()