"""
build_evidence_counts.py
Simple, reliable evidence fetcher:
- ClinicalTrials.gov (HTML scrape only)
- PubMed via eSearch
Saves to data/raw/evidence_counts.csv
"""
import time, random, re
from pathlib import Path
from urllib.parse import quote_plus
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS_POOL = [
    {"User-Agent": "PainReliefMap/1.0 (+capstone)"},
    {"User-Agent": "Mozilla/5.0"},
]

# -------------------------
# CONFIG
# -------------------------
conditions = [
    "Addiction", "Anxiety", "Burnout", "Cancer Pain",
    "Chronic Fatigue Syndrome", "Chronic Pain", "Depression",
    "Eating Disorders", "Endometriosis", "Fibromyalgia", "Headache",
    "Infertility", "Insomnia", "Irritable Bowel Syndrome", "Knee Pain",
    "Low Back Pain", "Menopause", "Migraine", "Myofascial Pain",
    "Neck Pain", "Neuropathic Pain", "Obsessive-Compulsive Disorder",
    "Osteoarthritis", "Perimenopause", "Polycystic Ovary Syndrome",
    "Postoperative Pain", "Post-Traumatic Stress Disorder",
    "Rheumatoid Arthritis", "Schizophrenia", "Shoulder Pain", "Stress",
]

therapies = [
    "Acupuncture", "Aromatherapy", "Cognitive Behavioural Therapy",
    "Exercise Therapy", "Herbal", "Massage",
    "Meditation", "Qi Gong", "Tai Chi", "Yoga",
]

condition_groups = {
    "Functional & Systemic": ["Chronic Fatigue Syndrome", "Irritable Bowel Syndrome", "Stress"],
    "Mental Health": ["Addiction", "Anxiety", "Burnout", "Depression", "Eating Disorders",
                      "Obsessive-Compulsive Disorder", "Post-Traumatic Stress Disorder",
                      "Schizophrenia"],
    "Musculoskeletal & Pain": ["Chronic Pain", "Fibromyalgia", "Low Back Pain", "Neck Pain",
                               "Knee Pain", "Shoulder Pain", "Myofascial Pain",
                               "Osteoarthritis", "Neuropathic Pain", "Cancer Pain",
                               "Postoperative Pain", "Migraine", "Headache",
                               "Rheumatoid Arthritis"],
    "Women's Health": ["Endometriosis", "Infertility", "Menopause",
                       "Perimenopause", "Polycystic Ovary Syndrome"],
}

def get_condition_group(cond: str) -> str:
    for group, members in condition_groups.items():
        if cond in members:
            return group
    return "Other"

# -------------------------
# HTML Scraper
# -------------------------
def get_trials_count(condition: str, therapy: str, tries: int = 3, delay: float = 0.8) -> int:
    """
    Scrape count from ClinicalTrials.gov.
    1) Try classic site (most reliable): /ct2/results?cond=&term=
    2) Fallback to new site: /search?cond=&term=
    """
    import re, time, random
    from urllib.parse import quote_plus
    import requests
    from bs4 import BeautifulSoup

    UA = [
        {"User-Agent": "PainReliefMap/1.0 (+capstone)"},
        {"User-Agent": "Mozilla/5.0"},
    ]

    cond = quote_plus(condition)
    ther = quote_plus(therapy)

    # --- 1) Classic UI (robust static HTML) ---
    classic_url = f"https://classic.clinicaltrials.gov/ct2/results?cond={cond}&term={ther}"
    for _ in range(tries):
        try:
            r = requests.get(classic_url, timeout=20, headers=random.choice(UA))
            if r.status_code == 200:
                text = r.text
                # Patterns seen on classic pages
                # e.g., "Found 67 studies" or "Found 1,234 studies"
                m = re.search(r"Found\s+([\d,]+)\s+studies", text, flags=re.I)
                if m:
                    return int(m.group(1).replace(",", ""))
            time.sleep(delay)
        except Exception:
            time.sleep(delay)

    # --- 2) New UI fallback ---
    new_url = f"https://clinicaltrials.gov/search?cond={cond}&term={ther}"
    for _ in range(tries):
        try:
            r = requests.get(new_url, timeout=20, headers=random.choice(UA))
            if r.status_code != 200:
                time.sleep(delay); continue
            soup = BeautifulSoup(r.text, "html.parser")

            # data-testid="search-count"
            node = soup.find(attrs={"data-testid": "search-count"})
            if node and node.text:
                digits = "".join(c for c in node.text if c.isdigit())
                if digits:
                    return int(digits)

            # Fallback phrase
            text = soup.get_text(" ", strip=True)
            m = re.search(r"(\d[\d,]*)\s+studies\s+found", text, flags=re.I)
            if m:
                return int(m.group(1).replace(",", ""))

            # Fallback badge
            badge = soup.select_one(".ct-number-of-studies, .ct-search-results__count")
            if badge:
                digits = re.sub(r"[^\d]", "", badge.get_text())
                if digits:
                    return int(digits)
        except Exception:
            pass
        time.sleep(delay)

    return 0

# -------------------------
# PubMed
# -------------------------
def get_pubmed_count(condition: str, therapy: str) -> int:
    try:
        q = quote_plus(f"{condition} AND {therapy}")
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term={q}"
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return int(r.json().get("esearchresult", {}).get("count", 0))
        return 0
    except Exception:
        return 0

# -------------------------
# Main
# -------------------------
def main():
    rows = []
    print("🔎 Building evidence counts (HTML scrape + PubMed)...\n")
    for i, cond in enumerate(conditions, 1):
        print(f"[{i}/{len(conditions)}] {cond} ...")
        for therapy in therapies:
            print(f"   ↳ {therapy:<30}", end="")
            trials = get_trials_count(cond, therapy)
            pubs = get_pubmed_count(cond, therapy)
            print(f" → {trials:>4} trials, {pubs:>6} pubs")

            rows.append({
                "condition_group": get_condition_group(cond),
                "condition": cond,
                "therapy_group": (
                    "Traditional" if therapy in ["Acupuncture", "Herbal"] else
                    "Mind–Body" if therapy in ["Meditation", "Yoga", "Tai Chi", "Qi Gong"] else
                    "Behavioural & Lifestyle"
                ),
                "therapy": therapy,
                "clinicaltrials_n": trials,
                "pubmed_n": pubs,
                "source": "ClinicalTrials.gov+PubMed",
                "country": "Worldwide",
                "last_updated": pd.Timestamp.today().strftime("%Y-%m-%d"),
            })
            time.sleep(0.4)

    df = pd.DataFrame(rows)
    out_path = Path("data/raw/evidence_counts.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\n✅ Done! Saved {len(df)} rows → {out_path.resolve()}")

if __name__ == "__main__":
    main()
