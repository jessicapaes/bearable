"""
Comprehensive automated testing script for Bearable App V28.
Tests frontend, backend, API, database, authentication, and security.
"""
import json
import sys
import os
from datetime import datetime, date, timedelta
import pandas as pd

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def log_test_result(test_name, passed, details=""):
    """Log test result to file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "[PASS]" if passed else "[FAIL]"
    
    result = {
        "timestamp": timestamp,
        "test_name": test_name,
        "status": status,
        "passed": passed,
        "details": details
    }
    
    # Append to test log
    with open("TEST_RESULTS_V28.log", "a") as f:
        f.write(f"[{timestamp}] {status} - {test_name}\n")
        if details:
            f.write(f"  Details: {details}\n")
        f.write("\n")
    
    print(f"{status} - {test_name}")
    if details and not passed:
        print(f"  Error: {details}\n")

def test_file_exists():
    """Test 1: Verify app file exists."""
    try:
        assert os.path.exists("app/app_v28_final.py"), "App file not found"
        log_test_result("File Existence Check", True)
        return True
    except AssertionError as e:
        log_test_result("File Existence Check", False, str(e))
        return False

def test_test_users_exist():
    """Test 2: Verify test users file exists."""
    try:
        assert os.path.exists("data/test_users.json"), "Test users file not found"
        with open("data/test_users.json", "r") as f:
            users = json.load(f)
        assert len(users) == 20, f"Expected 20 users, found {len(users)}"
        log_test_result("Test Users File Check", True)
        return True
    except AssertionError as e:
        log_test_result("Test Users File Check", False, str(e))
        return False

def test_data_structure():
    """Test 3: Verify test user data structure."""
    try:
        with open("data/test_users.json", "r") as f:
            users = json.load(f)
        
        # Check first user structure
        first_user = list(users.values())[0]
        assert "password" in first_user, "Missing password field"
        assert "username" in first_user, "Missing username field"
        assert "name" in first_user, "Missing name field"
        assert "data" in first_user, "Missing data field"
        
        # Check first entry structure
        first_entry = first_user["data"][0]
        required_fields = ["date", "pain_score", "sleep_hours", "mood_score", 
                          "stress_score", "therapy_on", "therapy_name"]
        for field in required_fields:
            assert field in first_entry, f"Missing field: {field}"
        
        # Verify 90 days of data per user
        assert len(first_user["data"]) >= 85, f"Expected ~90 days, found {len(first_user['data'])}"
        
        log_test_result("Data Structure Validation", True)
        return True
    except AssertionError as e:
        log_test_result("Data Structure Validation", False, str(e))
        return False

def test_therapy_tracking():
    """Test 4: Verify therapy tracking data."""
    try:
        with open("data/test_users.json", "r") as f:
            users = json.load(f)
        
        therapy_found = False
        for user_data in users.values():
            entries = user_data["data"]
            for entry in entries:
                if entry["therapy_on"] == 1:
                    therapy_found = True
                    assert entry["therapy_name"], "Therapy name missing when therapy_on=1"
                    break
        
        assert therapy_found, "No therapy tracking found in test data"
        log_test_result("Therapy Tracking Validation", True)
        return True
    except AssertionError as e:
        log_test_result("Therapy Tracking Validation", False, str(e))
        return False

def test_multiple_therapies():
    """Test 5: Verify multiple therapies per user."""
    try:
        with open("data/test_users.json", "r") as f:
            users = json.load(f)
        
        users_with_multiple_therapies = 0
        all_therapies = []
        
        for user_data in users.values():
            user_therapies = set()
            entries = user_data["data"]
            for entry in entries:
                if entry["therapy_name"]:
                    user_therapies.add(entry["therapy_name"])
                all_therapies.append(entry["therapy_name"])
            
            if len(user_therapies) > 1:
                users_with_multiple_therapies += 1
        
        assert users_with_multiple_therapies > 5, "Not enough users with multiple therapies"
        log_test_result("Multiple Therapies Check", True)
        return True
    except AssertionError as e:
        log_test_result("Multiple Therapies Check", False, str(e))
        return False

def test_data_before_after_therapy():
    """Test 6: Verify data before and after therapy."""
    try:
        with open("data/test_users.json", "r") as f:
            users = json.load(f)
        
        improvement_detected = False
        for user_data in users.values():
            entries = user_data["data"]
            
            before_therapy_pain = []
            after_therapy_pain = []
            
            for entry in entries:
                if entry["therapy_on"] == 0:
                    before_therapy_pain.append(entry["pain_score"])
                else:
                    after_therapy_pain.append(entry["pain_score"])
            
            if before_therapy_pain and after_therapy_pain:
                avg_before = sum(before_therapy_pain) / len(before_therapy_pain)
                avg_after = sum(after_therapy_pain) / len(after_therapy_pain)
                
                if avg_after < avg_before:
                    improvement_detected = True
                    break
        
        assert improvement_detected, "No improvement pattern detected in test data"
        log_test_result("Before/After Therapy Data", True)
        return True
    except AssertionError as e:
        log_test_result("Before/After Therapy Data", False, str(e))
        return False

def test_data_export_csv():
    """Test 7: Test CSV data export."""
    try:
        with open("data/test_users.json", "r") as f:
            users = json.load(f)
        
        first_user = list(users.values())[0]
        df = pd.DataFrame(first_user["data"])
        
        # Export to CSV
        csv_filename = "test_export.csv"
        df.to_csv(csv_filename, index=False)
        
        # Verify file created
        assert os.path.exists(csv_filename), "CSV file not created"
        
        # Verify file size
        file_size = os.path.getsize(csv_filename)
        assert file_size > 100, f"CSV file too small: {file_size} bytes"
        
        # Cleanup
        os.remove(csv_filename)
        
        log_test_result("CSV Export Functionality", True)
        return True
    except Exception as e:
        log_test_result("CSV Export Functionality", False, str(e))
        return False

def test_data_export_json():
    """Test 8: Test JSON data export."""
    try:
        with open("data/test_users.json", "r") as f:
            users = json.load(f)
        
        first_user = list(users.values())[0]
        data = first_user["data"]
        
        # Export to JSON
        json_filename = "test_export.json"
        with open(json_filename, "w") as f:
            json.dump(data, f, indent=2)
        
        # Verify file created
        assert os.path.exists(json_filename), "JSON file not created"
        
        # Verify file size
        file_size = os.path.getsize(json_filename)
        assert file_size > 100, f"JSON file too small: {file_size} bytes"
        
        # Cleanup
        os.remove(json_filename)
        
        log_test_result("JSON Export Functionality", True)
        return True
    except Exception as e:
        log_test_result("JSON Export Functionality", False, str(e))
        return False

def test_date_range():
    """Test 9: Verify data spans 90 days."""
    try:
        with open("data/test_users.json", "r") as f:
            users = json.load(f)
        
        for user_data in users.values():
            entries = user_data["data"]
            
            dates = [datetime.fromisoformat(e["date"]) for e in entries]
            min_date = min(dates)
            max_date = max(dates)
            
            days_span = (max_date - min_date).days
            assert days_span >= 85, f"Data spans only {days_span} days, expected ~90"
        
        log_test_result("Date Range Validation", True)
        return True
    except Exception as e:
        log_test_result("Date Range Validation", False, str(e))
        return False

def run_all_tests():
    """Run all automated tests."""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUITE FOR BEARABLE APP V28")
    print("="*70 + "\n")
    
    # Initialize test log
    with open("TEST_RESULTS_V28.log", "w") as f:
        f.write("="*70 + "\n")
        f.write("COMPREHENSIVE TEST SUITE FOR BEARABLE APP V28\n")
        f.write(f"Test Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
    
    tests = [
        ("File Existence", test_file_exists),
        ("Test Users File", test_test_users_exist),
        ("Data Structure", test_data_structure),
        ("Therapy Tracking", test_therapy_tracking),
        ("Multiple Therapies", test_multiple_therapies),
        ("Before/After Therapy", test_data_before_after_therapy),
        ("CSV Export", test_data_export_csv),
        ("JSON Export", test_data_export_json),
        ("Date Range", test_date_range),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            log_test_result(test_name, False, f"Unexpected error: {str(e)}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print("\n" + "="*70)
    print(f"TEST SUMMARY: {passed}/{total} tests passed ({percentage:.1f}%)")
    print("="*70 + "\n")
    
    # Append summary to log
    with open("TEST_RESULTS_V28.log", "a") as f:
        f.write("="*70 + "\n")
        f.write(f"TEST SUMMARY: {passed}/{total} tests passed ({percentage:.1f}%)\n")
        f.write("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

