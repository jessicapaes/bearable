# scripts/add_evidence_direction.py
from pathlib import Path
import pandas as pd
import requests, re

# --- locate CSV like the app does ---
ROOT = Path(__file__).resolve().parents[1]  # repo root (one up from scripts/)
candidates = [
    ROOT / "data" / "evidence_counts.csv",
    ROOT / "data" / "raw" / "evidence_counts.csv",
    ROOT / "evidence_counts.csv",
]
csv_in = next((p for p in candidates if p.exists()), None)
if csv_in is None:
    raise FileNotFoundError(
        "Couldn't find evidence_counts.csv. Looked in:\n"
        f" - {candidates[0]}\n - {candidates[1]}\n - {candidates[2]}\n"
        "Move your file to data/evidence_counts.csv or data/raw/evidence_counts.csv."
    )

print(f"📄 Reading: {csv_in}")
df = pd.read_csv(csv_in)

def get_pubmed_direction(condition, therapy):
    """Fetch PubMed abstracts and infer direction from real text (simple, real-data keywords)."""
    term = f"{condition} AND {therapy}"
    s_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    f_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    try:
        q = {"db": "pubmed", "retmax": "5", "term": term, "retmode": "json"}
        ids = requests.get(s_url, params=q, timeout=10).json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return "Unclear"
        r = requests.get(f_url, params={"db": "pubmed", "id": ",".join(ids[:5]), "rettype": "abstract", "retmode": "text"}, timeout=10)
        text = r.text.lower()

        if re.search(r"significant (improvement|reduction|benefit|effect)", text):
            return "Positive"
        if re.search(r"no (significant|difference|effect|benefit)", text):
            return "Negative"
        if re.search(r"mixed|inconclusive|limited evidence|conflicting", text):
            return "Mixed"
        return "Unclear"
    except Exception:
        return "Unclear"

print("🔎 Generating evidence_direction from PubMed summaries...")
df["evidence_direction"] = df.apply(lambda r: get_pubmed_direction(r["condition"], r["therapy"]), axis=1)

out = ROOT / "data" / "evidence_counts_with_direction.csv"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print(f"✅ Saved enriched file with evidence_direction → {out}")