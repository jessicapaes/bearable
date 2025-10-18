# scripts/fill_pubmed_counts.py
from pathlib import Path
import time
import json
import requests
import pandas as pd
from urllib.parse import quote_plus

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
HEADERS = {"User-Agent": "PainReliefMap/1.0 (+capstone)"}

# --- aliases to make PubMed queries robust ---
COND_ALIASES = {
    "Addiction": ["Substance Use Disorder","Substance-Related Disorders","Addiction"],
    "Chronic Fatigue Syndrome": ["Myalgic Encephalomyelitis","ME/CFS","Chronic Fatigue Syndrome"],
    "Headache": ["Headache Disorders","Headache Disorders, Primary","Headache"],
    "Myofascial Pain": ["Myofascial Pain Syndromes","Myofascial Pain"],
    "Neuropathic Pain": ["Neuropathic Pain","Neuralgia","Peripheral Neuropathy"],
    "Obsessive-Compulsive Disorder": ["Obsessive-Compulsive Disorder","OCD"],
    "Post-Traumatic Stress Disorder": ["Post-Traumatic Stress Disorder","PTSD"],
}
THER_ALIASES = {
    "Cognitive Behavioural Therapy": ["Cognitive Behavioral Therapy","CBT","Cognitive Behaviour Therapy"],
    "Qi Gong": ["Qigong","Chi Kung","Qi Gong"],
    "Tai Chi": ["Tai Chi","Taiji","Tai Ji"],
    "Herbal": ["Herbal","Herbal Medicine","Phytotherapy"],
    "Exercise Therapy": ["Exercise Therapy","Therapeutic Exercise","Physical Exercise","Exercise Intervention"],
    "Meditation": ["Meditation","Mindfulness","Mindfulness-Based Stress Reduction","MBSR"],
    "Massage": ["Massage","Massage Therapy"],
    "Acupuncture": ["Acupuncture","Electroacupuncture"],
    "Aromatherapy": ["Aromatherapy","Essential Oils"],
    "Yoga": ["Yoga"],
}

def build_term(condition: str, therapy: str) -> str:
    c_terms = [condition] + COND_ALIASES.get(condition, [])
    t_terms = [therapy] + THER_ALIASES.get(therapy, [])
    c_block = " OR ".join([f'"{t}"' for t in dict.fromkeys(c_terms)])  # dedupe, keep order
    t_block = " OR ".join([f'"{t}"' for t in dict.fromkeys(t_terms)])
    # You can scope to Title/Abstract if you want fewer false positives: [tiab]
    # return f"(({c_block})[tiab]) AND (({t_block})[tiab])"
    return f"({c_block}) AND ({t_block})"

def pubmed_count(term: str) -> int:
    params = {
        "db": "pubmed",
        "retmode": "json",
        "term": term,
    }
    r = requests.get(EUTILS, params=params, timeout=20, headers=HEADERS)
    if r.status_code == 200:
        try:
            return int(r.json()["esearchresult"]["count"])
        except Exception:
            return 0
    return 0

def main():
    root = Path(__file__).resolve().parents[1]
    csv_path = root / "data" / "raw" / "evidence_counts.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}. Run your AACT script first.")
    df = pd.read_csv(csv_path)

    # Build a set of unique (condition, therapy) to query
    pairs = df[["condition","therapy"]].drop_duplicates().to_records(index=False)

    results = {}
    print(f"🔎 Fetching PubMed counts for {len(pairs)} pairs...")
    for i, (cond, ther) in enumerate(pairs, 1):
        term = build_term(cond, ther)
        count = pubmed_count(term)
        results[(cond, ther)] = count
        print(f"[{i}/{len(pairs)}] {cond} × {ther} → {count}")
        time.sleep(0.35)  # be polite to E-utilities (3 req/sec)

    # Map counts back into df
    df["pubmed_n"] = df.apply(lambda r: results.get((r["condition"], r["therapy"]), 0), axis=1)

    # Save in-place (same file your app reads)
    df.to_csv(csv_path, index=False)
    print(f"✅ Updated PubMed counts → {csv_path.resolve()}")

if __name__ == "__main__":
    main()