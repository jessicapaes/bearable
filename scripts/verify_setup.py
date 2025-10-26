import os
from pathlib import Path
import importlib.util
import pandas as pd

ROOT = Path(__file__).resolve().parent
print(f"🧩 Checking project at: {ROOT}\n")

# --- Ensure folders ---
expected_dirs = ["app", "src", "data", "data/templates"]
for d in expected_dirs:
    p = ROOT / d
    p.mkdir(parents=True, exist_ok=True)
    print(f"📁 {d:<20}: {'✅ exists' if p.exists() else '❌ missing'}")

# --- Key files expected (some will be created if missing) ---
expected_files = {
    "requirements.txt": ROOT / "requirements.txt",
    "app/app.py": ROOT / "app/app.py",
    "src/causal.py": ROOT / "src/causal.py",
    "data/evidence_counts.csv": ROOT / "data/evidence_counts.csv",
    "data/templates/n_of_1_template.csv": ROOT / "data/templates/n_of_1_template.csv",
    "data/templates/did_template.csv": ROOT / "data/templates/did_template.csv",
}

print("\n🔍 Checking important files (creating templates if missing):")

# --- Canonical columns (must match app.py DEFAULT_COLS) ---
N_OF_1_COLUMNS = [
    "date", "therapy_on", "pain_score", "sleep_hours", "stress_score",
    "mood_score", "movement", "digestive_sounds", "bowel_movements_n",
    "stool_consistency",
    "physical_symptoms", "physical_symptoms_other",
    "emotional_symptoms", "emotional_symptoms_other",
    "patience_score", "anxiety_score", "cried_today",
    "cravings", "cravings_other",
]

# Minimal DiD template (feel free to expand later)
DID_COLUMNS = [
    "date",              # daily or weekly date
    "group",             # 0 = control, 1 = treated
    "post",              # 0 = pre, 1 = post
    "outcome_pain"       # numeric outcome (e.g., pain score)
]

# --- Create template files if missing ---
n1_tpl_path = expected_files["data/templates/n_of_1_template.csv"]
if not n1_tpl_path.exists():
    print("   ✨ Creating data/templates/n_of_1_template.csv …")
    pd.DataFrame(columns=N_OF_1_COLUMNS).to_csv(n1_tpl_path, index=False)
else:
    print("   ✅ data/templates/n_of_1_template.csv")

did_tpl_path = expected_files["data/templates/did_template.csv"]
if not did_tpl_path.exists():
    print("   ✨ Creating data/templates/did_template.csv …")
    pd.DataFrame(columns=DID_COLUMNS).to_csv(did_tpl_path, index=False)
else:
    print("   ✅ data/templates/did_template.csv")

# --- Report presence of other expected files ---
for name, path in expected_files.items():
    if name.endswith("n_of_1_template.csv") or name.endswith("did_template.csv"):
        continue  # already handled above
    print(f"   {'✅' if path.exists() else '❌'} {name}")

# --- Import causal.py sanity check ---
try:
    spec = importlib.util.spec_from_file_location("causal", ROOT / "src" / "causal.py")
    causal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(causal)
    print("\n🧠 causal.py imported successfully.")
except Exception as e:
    print(f"\n⚠️  Could not import causal.py: {e}")

# --- Check evidence CSV format (if present) ---
csv_path = ROOT / "data" / "evidence_counts.csv"
if csv_path.exists():
    try:
        df = pd.read_csv(csv_path)
        print(f"\n📊 evidence_counts.csv loaded! {len(df)} rows, {len(df.columns)} columns")
        print("   Columns:", ", ".join(df.columns))
    except Exception as e:
        print(f"\n⚠️  Could not read evidence_counts.csv: {e}")
else:
    print("\nℹ️  evidence_counts.csv not found (ok during early dev).")

# --- Validate N-of-1 template columns ---
print("\n🧪 Validating n_of_1_template.csv columns match app DEFAULT_COLS …")
try:
    n1_df = pd.read_csv(n1_tpl_path)
    have = list(n1_df.columns)
    missing = [c for c in N_OF_1_COLUMNS if c not in have]
    extras = [c for c in have if c not in N_OF_1_COLUMNS]
    if not missing and not extras:
        print("   ✅ n_of_1_template.csv columns are correct.")
    else:
        if missing:
            print("   ❌ Missing columns:", ", ".join(missing))
        if extras:
            print("   ⚠️ Extra columns (not required):", ", ".join(extras))
except Exception as e:
    print(f"   ⚠️ Could not read n_of_1_template.csv: {e}")

print("\n✅ Setup check complete.")