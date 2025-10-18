# scripts/test_db.py
from src.db import read_pairs

print("🔍 Testing Supabase DB connection...")
df = read_pairs()

if df is None:
    print("⚠️  Could not connect or table empty. Check DATABASE_URL.")
else:
    print(f"✅ Connected! Retrieved {len(df)} rows.")
    print(df.head().to_string(index=False))