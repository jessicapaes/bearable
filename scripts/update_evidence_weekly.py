#!/usr/bin/env python3
"""
update_evidence_weekly.py
Automatically update evidence data weekly from live APIs.
This can be scheduled to run via cron (Linux/Mac) or Task Scheduler (Windows).

Usage:
    python scripts/update_evidence_weekly.py

Or schedule it with cron (Linux/Mac):
    0 0 * * 0  cd /path/to/project && python scripts/update_evidence_weekly.py

Or schedule it with Task Scheduler (Windows):
    - Create a new task
    - Set trigger to "Weekly" on Sunday at 12:00 AM
    - Set action to run: pythonw.exe scripts\update_evidence_weekly.py
"""

import sys
from pathlib import Path
import pandas as pd
import time

# Add parent directory to path to import functions
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the evidence fetching functions from the app
try:
    from app.app_v28_final import get_live_evidence_data
except ImportError:
    print("Error: Could not import app functions. Make sure you're running from the correct directory.")
    sys.exit(1)

def update_evidence_data():
    """Fetch and save the latest evidence data"""
    
    # Define therapies and conditions
    therapies_list = [
        "Acupuncture", "Yoga", "Meditation", "Massage", "Tai Chi", 
        "Cognitive Behavioural Therapy", "Herbal", "Aromatherapy", 
        "Exercise Therapy", "Qi Gong"
    ]
    
    conditions_list = [
        "Addiction", "Anxiety", "Burnout", "Cancer Pain", "Chronic Fatigue Syndrome",
        "Chronic Pain", "Depression", "Eating Disorders", "Endometriosis", "Fibromyalgia",
        "Headache", "Infertility", "Insomnia", "Irritable Bowel Syndrome", "Knee Pain",
        "Low Back Pain", "Menopause", "Migraine", "Myofascial Pain", "Neck Pain",
        "Neuropathic Pain", "Obsessive-Compulsive Disorder", "Osteoarthritis", "Perimenopause",
        "Polycystic Ovary Syndrome", "Postoperative Pain", "Post-Traumatic Stress Disorder",
        "Rheumatoid Arthritis", "Schizophrenia", "Shoulder Pain", "Stress"
    ]
    
    total_combinations = len(therapies_list) * len(conditions_list)
    print(f"🔄 Starting evidence data update for {total_combinations} condition-therapy combinations...")
    
    rows = []
    current = 0
    
    for therapy in therapies_list:
        for condition in conditions_list:
            current += 1
            
            try:
                live_data = get_live_evidence_data(condition, therapy)
                rows.append({
                    'therapy': therapy,
                    'condition': condition,
                    'clinicaltrials_n': live_data['clinicaltrials_n'],
                    'pubmed_n': live_data['pubmed_n'],
                    'evidence_direction': 'Unclear',
                    'data_source': live_data['data_source'],
                    'last_updated': live_data['last_updated']
                })
                
                if current % 10 == 0:
                    print(f"  Progress: {current}/{total_combinations} ({(current/total_combinations)*100:.1f}%)")
                
                # Small delay to avoid overwhelming APIs
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ⚠️  Error fetching {therapy} for {condition}: {e}")
                continue
    
    # Save to CSV
    df = pd.DataFrame(rows)
    output_path = Path("data/evidence_counts.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Successfully updated evidence data!")
    print(f"   Saved {len(df)} records to {output_path}")
    print(f"   Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return output_path

if __name__ == "__main__":
    try:
        update_evidence_data()
    except Exception as e:
        print(f"❌ Error during evidence update: {e}")
        sys.exit(1)

