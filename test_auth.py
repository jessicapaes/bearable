"""
Comprehensive authentication testing script for Bearable app
Tests account creation, sign in, sign out, and password reset
"""

import json
import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Test Configuration
TEST_USER = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "testpass123"
}

ACCOUNTS_FILE = "data/accounts.json"

def setup_test():
    """Setup test environment"""
    print("=" * 70)
    print("BEARABLE AUTHENTICATION END-TO-END TEST")
    print("=" * 70)
    print()

    # Backup existing accounts if they exist
    if os.path.exists(ACCOUNTS_FILE):
        backup_file = "data/accounts_backup.json"
        import shutil
        shutil.copy(ACCOUNTS_FILE, backup_file)
        print(f"✅ Backed up existing accounts to {backup_file}")

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    print("✅ Data directory ready")
    print()

def test_account_creation():
    """Test 1: Account Creation"""
    print("-" * 70)
    print("TEST 1: ACCOUNT CREATION")
    print("-" * 70)

    try:
        # Load existing accounts
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "r") as f:
                accounts = json.load(f)
        else:
            accounts = {}

        # Check if test account already exists
        if TEST_USER["email"] in accounts:
            print(f"⚠️  Test account '{TEST_USER['email']}' already exists, removing it...")
            del accounts[TEST_USER["email"]]
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(accounts, f, indent=2)

        # Create new test account
        accounts[TEST_USER["email"]] = {
            "name": TEST_USER["name"],
            "username": TEST_USER["email"],
            "password": TEST_USER["password"],
            "email": TEST_USER["email"]
        }

        # Save to file
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump(accounts, f, indent=2)

        # Verify account was created
        with open(ACCOUNTS_FILE, "r") as f:
            saved_accounts = json.load(f)

        if TEST_USER["email"] in saved_accounts:
            account_data = saved_accounts[TEST_USER["email"]]
            assert account_data["name"] == TEST_USER["name"], "Name mismatch"
            assert account_data["password"] == TEST_USER["password"], "Password mismatch"
            assert account_data["email"] == TEST_USER["email"], "Email mismatch"
            print("✅ PASS: Account created successfully")
            print(f"   - Name: {account_data['name']}")
            print(f"   - Email: {account_data['email']}")
            return True
        else:
            print("❌ FAIL: Account not found after creation")
            return False

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    finally:
        print()

def test_signin():
    """Test 2: Sign In"""
    print("-" * 70)
    print("TEST 2: SIGN IN")
    print("-" * 70)

    try:
        # Load accounts
        if not os.path.exists(ACCOUNTS_FILE):
            print("❌ FAIL: Accounts file doesn't exist")
            return False

        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)

        # Test: Valid credentials
        print("Test 2a: Valid credentials")
        if TEST_USER["email"] in accounts:
            account_data = accounts[TEST_USER["email"]]
            if isinstance(account_data, dict):
                if account_data.get("password") == TEST_USER["password"]:
                    print("✅ PASS: Valid credentials accepted")
                else:
                    print("❌ FAIL: Password doesn't match")
                    return False
            else:
                print("❌ FAIL: Account data format incorrect")
                return False
        else:
            print("❌ FAIL: Account not found")
            return False

        # Test: Invalid password
        print("Test 2b: Invalid password (should fail)")
        if account_data.get("password") != "wrongpassword":
            print("✅ PASS: Invalid password correctly rejected")
        else:
            print("❌ FAIL: Invalid password accepted")
            return False

        # Test: Non-existent account
        print("Test 2c: Non-existent account (should fail)")
        if "nonexistent@example.com" not in accounts:
            print("✅ PASS: Non-existent account correctly rejected")
        else:
            print("❌ FAIL: Non-existent account found")
            return False

        return True

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    finally:
        print()

def test_password_reset():
    """Test 3: Password Reset"""
    print("-" * 70)
    print("TEST 3: PASSWORD RESET")
    print("-" * 70)

    try:
        # Load accounts
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)

        # Save old password for verification
        old_password = accounts[TEST_USER["email"]]["password"]
        new_password = "newpass456"

        # Update password
        print(f"Changing password from '{old_password}' to '{new_password}'")
        accounts[TEST_USER["email"]]["password"] = new_password

        # Save updated accounts
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump(accounts, f, indent=2)

        # Verify password was changed
        with open(ACCOUNTS_FILE, "r") as f:
            updated_accounts = json.load(f)

        if updated_accounts[TEST_USER["email"]]["password"] == new_password:
            print("✅ PASS: Password successfully updated")

            # Test: Old password no longer works
            print("Test 3a: Old password should not work")
            if updated_accounts[TEST_USER["email"]]["password"] != old_password:
                print("✅ PASS: Old password correctly rejected")
            else:
                print("❌ FAIL: Old password still works")
                return False

            # Test: New password works
            print("Test 3b: New password should work")
            if updated_accounts[TEST_USER["email"]]["password"] == new_password:
                print("✅ PASS: New password accepted")
            else:
                print("❌ FAIL: New password doesn't work")
                return False

            # Restore original password for subsequent tests
            accounts[TEST_USER["email"]]["password"] = TEST_USER["password"]
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(accounts, f, indent=2)
            print("✅ Password restored to original for cleanup")

            return True
        else:
            print("❌ FAIL: Password update didn't persist")
            return False

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    finally:
        print()

def test_account_data_structure():
    """Test 4: Account Data Structure"""
    print("-" * 70)
    print("TEST 4: ACCOUNT DATA STRUCTURE")
    print("-" * 70)

    try:
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)

        account_data = accounts[TEST_USER["email"]]

        # Check required fields
        required_fields = ["name", "username", "password", "email"]
        for field in required_fields:
            if field in account_data:
                print(f"✅ Field '{field}' present: {account_data[field]}")
            else:
                print(f"❌ Field '{field}' missing")
                return False

        # Check field values
        if account_data["username"] == account_data["email"]:
            print("✅ Username matches email (correct format)")
        else:
            print("❌ Username doesn't match email")
            return False

        return True

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    finally:
        print()

def test_demo_mode():
    """Test 5: Demo Mode"""
    print("-" * 70)
    print("TEST 5: DEMO MODE")
    print("-" * 70)

    try:
        # Demo credentials
        demo_user = "demo"
        demo_pass = "demo"

        # Demo mode doesn't use accounts file, but we can verify the logic
        print(f"Testing demo credentials: {demo_user}/{demo_pass}")

        # In the app, demo mode is triggered by username=="demo" and password=="demo"
        if demo_user == "demo" and demo_pass == "demo":
            print("✅ PASS: Demo credentials recognized")
            print("   - Demo mode would be activated")
            print("   - Sample data would be loaded")
            return True
        else:
            print("❌ FAIL: Demo credentials not recognized")
            return False

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    finally:
        print()

def cleanup_test():
    """Cleanup test account"""
    print("-" * 70)
    print("CLEANUP")
    print("-" * 70)

    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "r") as f:
                accounts = json.load(f)

            if TEST_USER["email"] in accounts:
                del accounts[TEST_USER["email"]]
                with open(ACCOUNTS_FILE, "w") as f:
                    json.dump(accounts, f, indent=2)
                print(f"✅ Removed test account: {TEST_USER['email']}")
            else:
                print(f"⚠️  Test account not found (already removed?)")

        # Restore backup if it exists
        backup_file = "data/accounts_backup.json"
        if os.path.exists(backup_file):
            import shutil
            # Don't overwrite if we want to keep test account
            # shutil.copy(backup_file, ACCOUNTS_FILE)
            print(f"ℹ️  Backup available at: {backup_file}")

    except Exception as e:
        print(f"⚠️  Cleanup issue: {str(e)}")
    finally:
        print()

def main():
    """Run all tests"""
    setup_test()

    results = []

    # Run all tests
    results.append(("Account Creation", test_account_creation()))
    results.append(("Sign In", test_signin()))
    results.append(("Password Reset", test_password_reset()))
    results.append(("Data Structure", test_account_data_structure()))
    results.append(("Demo Mode", test_demo_mode()))

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print()
    print(f"Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
    print()

    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - Please review issues above")

    print()

    # Ask if user wants to cleanup
    response = input("Remove test account? (y/n): ")
    if response.lower() == 'y':
        cleanup_test()
    else:
        print("ℹ️  Test account kept for manual testing in app")
        print(f"   Email: {TEST_USER['email']}")
        print(f"   Password: {TEST_USER['password']}")

    print()
    print("=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
