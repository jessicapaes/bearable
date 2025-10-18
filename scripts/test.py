"""
build_evidence_counts.py
Robust evidence fetch: ClinicalTrials.gov v2 -> v2 text -> v1 -> HTML scrape
PubMed via eSearch.
Saves to data/raw/evidence_counts.csv
"""
import time
import requests
import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "PainReliefMap/1.0 (+evidence-counts)"}

# -------------------------
# CONFIG (your lists)
# -------------------------
conditions = [
    "Addiction","Anxiety","Burnout","Cancer Pain","Chronic Fatigue Syndrome",
    "Chronic Pain","Depression","Eating Disorders","Endometriosis","Fibromyalgia",
    "Headache","Infertility","Insomnia","Irritable Bowel Syndrome","Knee Pain",
    "Low Back Pain","Menopause","Migraine","Myofascial Pain","Neck Pain",
    "Neuropathic Pain","Obsessive-Compulsive Disorder","Osteoarthritis",
    "Perimenopause","Polycystic Ovary Syndrome","Postoperative Pain",
    "Post-Traumatic Stress Disorder","Rheumatoid Arthritis","Schizophrenia",
    "Shoulder Pain","Stress"
]

therapies = [
    "Acupuncture","Aromatherapy","Cognitive Behavioural Therapy","Exercise Therapy",
    "Herbal","Massage","Meditation","Qi Gong","Tai Chi","Yoga"
]

condition_groups = {
    "Functional & Systemic": ["Chronic Fatigue Syndrome","Irritable Bowel Syndrome","Stress"],
    "Mental Health": ["Addiction","Anxiety","Burnout","Depression","Eating Disorders",
                      "Obsessive-Compulsive Disorder","Post-Traumatic Stress Disorder","Schizophrenia"],
    "Musculoskeletal & Pain": ["Chronic Pain","Fibromyalgia","Low Back Pain","Neck Pain","Knee Pain",
                               "Shoulder Pain","Myofascial Pain","Osteoarthritis","Neuropathic Pain",
                               "Cancer Pain","Postoperative Pain","Migraine","Headache","Rheumatoid Arthritis"],
    "Women's Health": ["Endometriosis","Infertility","Menopause","Perimenopause","Polycystic Ovary Syndrome"]
}

def get_condition_group(cond):
    for g, members in condition_groups.items():
        if cond in members:
            return g
    return "Other"

# -------------------------
# ClinicalTrials.gov — helpers
# -------------------------
def ct_v2_cond_intr(condition, therapy):
    url = (f"https://clinicaltrials.gov/api/v2/studies"
           f"?query.cond={quote_plus(condition)}"
           f"&query.intr={quote_plus(therapy)}"
           f"&pageSize=1")
    r = requests.get(url, timeout=20, headers=HEADERS)
    return r

def ct_v2_text(condition, therapy):
    query = quote_plus(f"\"{condition}\" AND \"{therapy}\"")
    url = f"https://clinicaltrials.gov/api/v2/studies?query.text={query}&pageSize=1"
    r = requests.get(url, timeout=20, headers=HEADERS)
    return r

def ct_v1_expr(condition, therapy):
    expr = quote_plus(f"{condition} AND {therapy}")
    url = (f"https://clinicaltrials.gov/api/query/study_fields?"
           f"expr={expr}&fields=NCTId&fmt=json")
    r = requests.get(url, timeout=20, headers=HEADERS)
    return r

def parse_ct_v2_total(r):
    try:
        return int(r.json().get("meta", {}).get("totalCount", 0))
    except Exception:
        return None

def parse_ct_v1_total(r):
    try:
        return int(r.json()["StudyFieldsResponse"]["NStudiesFound"])
    except Exception:
        return None

def ct_html_fallback(condition, therapy):
    # Public search page fallback
    url = f"https://clinicaltrials.gov/search?cond={quote_plus(condition)}&term={quote_plus(therapy)}"
    r = requests.get(url, timeout=20, headers=HEADERS)
    if r.status_code != 200:
        return 0
    soup = BeautifulSoup(r.text, "html.parser")

    # Preferred data-testid used in new UI:
    node = soup.find(attrs={"data-testid": "search-count"})
    if node and node.text:
        txt = node.text.strip().replace(",", "")
        digits = "".join([c for c in txt if c.isdigit()])
        return int(digits) if digits else 0

    # Alternate patterns:
    # sometimes "X studies found" appears in body text
    text = soup.get_text(" ", strip=True)
    import re
    m = re.search(r"(\d[\d,]*)\s+studies\s+found", text, re.IGNORECASE)
    if m:
        return int(m.group(1).replace(",", ""))
    return 0

def get_trials_count(condition, therapy):
    # 1) v2 structured
    try:
        r = ct_v2_cond_intr(condition, therapy)
        if r.status_code == 200:
            n = parse_ct_v2_total(r)
            if n is not None and n > 0:
                return n
    except Exception:
        pass

    # 2) v2 text
    try:
        r = ct_v2_text(condition, therapy)
        if r.status_code == 200:
            n = parse_ct_v2_total(r)
            if n is not None and n > 0:
                return n
    except Exception:
        pass

    # 3) v1 classic
    try:
        r = ct_v1_expr(condition, therapy)
        if r.status_code == 200:
            n = parse_ct_v1_total(r)
            if n is not None:
                return n
    except Exception:
        pass

    # 4) HTML fallback
    try:
        n = ct_html_fallback(condition, therapy)
        return n
    except Exception:
        return 0

# -------------------------
# PubMed — simple count
# -------------------------
def get_pubmed_count(condition, therapy):
    try:
        q = quote_plus(f"{condition} AND {therapy}")
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term={q}"
        r = requests.get(url, timeout=20, headers=HEADERS)
        if r.status_code == 200:
            return int(r.json().get("esearchresult", {}).get("count", 0))
        return 0
    except Exception:
        return 0

# -------------------------
# Main
# -------------------------
def main():
    out = []
    print("🔎 Building evidence counts from ClinicalTrials.gov and PubMed...\n")
    for i, cond in enumerate(conditions, 1):
        print(f"[{i}/{len(conditions)}] {cond} ...")
        for therapy in therapies:
            print(f"   ↳ {therapy:<30}", end="")
            trials = get_trials_count(cond, therapy)
            pubs = get_pubmed_count(cond, therapy)
            print(f" → {trials:>4} trials, {pubs:>6} pubs")

            row = {
                "condition_group": get_condition_group(cond),
                "condition": cond,
                "therapy_group": (
                    "Traditional" if therapy in ["Acupuncture","Herbal"] else
                    "Mind–Body" if therapy in ["Meditation","Yoga","Tai Chi","Qi Gong"] else
                    "Behavioural & Lifestyle"
                ),
                "therapy": therapy,
                "clinicaltrials_n": trials,
                "pubmed_n": pubs,
                "source": "ClinicalTrials.gov+PubMed",
                "country": "Worldwide",
                "last_updated": pd.Timestamp.today().strftime("%Y-%m-%d"),
            }
            out.append(row)
            time.sleep(0.4)  # respectful pacing

    df = pd.DataFrame(out)
    out_path = Path("data/raw/evidence_counts.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\n✅ Done! Saved {len(df)} rows → {out_path.resolve()}")

if __name__ == "__main__":
    main()