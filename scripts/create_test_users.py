"""
Script to create test users with 90 days of logs for UAT testing.
This script creates 20 test users with realistic health tracking data.
"""
import json
import random
from datetime import date, timedelta
import pandas as pd

def generate_test_users(num_users=20, days_per_user=90):
    """
    Generate test users with historical health tracking data.
    
    Args:
        num_users: Number of test users to create (default: 20)
        days_per_user: Number of days of data per user (default: 90)
    """
    users = {}
    
    # Therapies to choose from
    therapies = [
        "Turmeric",
        "Ginger",
        "Omega-3 Fatty Acids",
        "Vitamin D",
        "Magnesium",
        "Probiotics",
        "CBD Oil",
        "Acupuncture",
        "Meditation",
        "Exercise",
        "Sleep Hygiene",
        "Aromatherapy",
        "Massage Therapy",
        "Chiropractic",
        "Heat/Cold Therapy"
    ]
    
    symptoms = [
        "Back Pain",
        "Joint Pain",
        "Headaches",
        "Fatigue",
        "Inflammation",
        "Anxiety",
        "Depression",
        "Insomnia",
        "Digestive Issues",
        "Muscle Tension"
    ]
    
    for user_num in range(1, num_users + 1):
        email = f"testuser{user_num}@testbearable.com"
        username = f"TestUser{user_num}"
        
        # Randomly assign 1-3 therapies per user
        num_therapies = random.randint(1, 3)
        user_therapies = random.sample(therapies, num_therapies)
        
        # Randomly assign primary symptom
        primary_symptom = random.choice(symptoms)
        
        # Generate 90 days of data
        start_date = date.today() - timedelta(days=days_per_user)
        entries = []
        
        # Therapy start date (somewhere in the first 30 days)
        therapy_start_day = random.randint(10, 30)
        
        for day in range(days_per_user):
            current_date = start_date + timedelta(days=day)
            
            # Determine if therapy has started
            therapy_on = 1 if day >= therapy_start_day else 0
            therapy_name = user_therapies[0] if therapy_on else ""
            
            # If multiple therapies, sometimes add second therapy
            if len(user_therapies) > 1 and day > therapy_start_day + 30 and random.random() > 0.8:
                therapy_name = random.choice(user_therapies)
            
            # Pain/symptom scores - start higher, improve after therapy
            if day < therapy_start_day:
                # Before therapy - higher pain/symptoms
                base_pain = random.uniform(6, 9)
                base_mood = random.uniform(4, 6)
                base_stress = random.uniform(6, 8)
            else:
                # After therapy - gradual improvement
                days_post_therapy = day - therapy_start_day
                improvement = min(days_post_therapy * 0.05, 3)  # Max 3 point improvement
                base_pain = max(random.uniform(6, 9) - improvement + random.uniform(-1, 1), 1)
                base_mood = min(random.uniform(4, 6) + improvement + random.uniform(-1, 1), 10)
                base_stress = max(random.uniform(6, 8) - improvement + random.uniform(-1, 1), 1)
            
            # Sleep - improves after therapy
            if day < therapy_start_day:
                sleep_hours = random.uniform(5, 7)
            else:
                days_post_therapy = day - therapy_start_day
                improvement = min(days_post_therapy * 0.02, 1.5)  # Max 1.5 hour improvement
                sleep_hours = min(random.uniform(5, 7) + improvement + random.uniform(-0.5, 0.5), 10)
            
            entry = {
                "date": current_date.isoformat(),
                "pain_score": round(base_pain, 1),
                "sleep_hours": round(sleep_hours, 1),
                "mood_score": round(base_mood, 1),
                "stress_score": round(base_stress, 1),
                "wake_ups": random.randint(0, 3),
                "therapy_on": therapy_on,
                "therapy_name": therapy_name,
                "bowel": random.randint(0, 10),
                "appetite": random.uniform(5, 9),
                "weight": round(random.uniform(65, 85), 1),
                "temperature": round(random.uniform(36.1, 37.2), 1),
                "blood_pressure_systolic": random.randint(110, 130),
                "blood_pressure_diastolic": random.randint(70, 85),
                "heart_rate": random.randint(60, 80),
                "oxygen_saturation": random.randint(96, 100),
                "blood_sugar": random.randint(4, 7),
                "water_intake": random.randint(1, 4),
                "caffeine": random.randint(0, 4),
                "alcohol": random.randint(0, 2),
                "symptoms": f"{primary_symptom}",
                "movement": "Walk, Stretch" if random.random() > 0.3 else "",
                "digestive": random.choice(["Normal", "Sluggish", "Active"]),
                "stool": random.choice(["Normal", "Loose", "Hard"]),
                "energy": round(base_mood * 0.9, 1),
                "mental_clarity": round(base_mood * 1.1, 1),
                "motivation": round(base_mood * 0.95, 1),
                "social": random.uniform(5, 9),
                "work_performance": round(base_mood * 1.05, 1),
                "physical_activity": random.randint(1, 5),
                "meditation": random.randint(0, 3),
                "outdoor_time": random.randint(0, 4),
            }
            entries.append(entry)
        
        users[email] = {
            "password": "TestPassword123!",
            "username": username,
            "name": username,
            "data": entries
        }
    
    return users

def save_test_users():
    """Generate and save test users to JSON file."""
    print("Generating 20 test users with 90 days of health tracking data...")
    users = generate_test_users(num_users=20, days_per_user=90)
    
    # Save to JSON file
    with open("data/test_users.json", "w") as f:
        json.dump(users, f, indent=2)
    
    print(f"✓ Created {len(users)} test users")
    print(f"✓ Each user has ~90 days of health tracking data")
    print(f"✓ File saved to: data/test_users.json")
    
    # Print summary
    total_entries = sum(len(user['data']) for user in users.values())
    print(f"✓ Total entries: {total_entries}")
    
    return users

if __name__ == "__main__":
    save_test_users()

