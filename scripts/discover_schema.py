"""
Discover the actual schema of app_users table
"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("Testing different column combinations...\n")

# Test 1: Just email and password
print("Test 1: email + password only")
try:
    response = supabase.table('app_users').insert({
        'email': 'test1@example.com',
        'password': 'test_hash'
    }).execute()
    print(f"✅ SUCCESS! Columns in response:")
    if response.data:
        for key in response.data[0].keys():
            print(f"  - {key}")
        # Delete it
        supabase.table('app_users').delete().eq('email', 'test1@example.com').execute()
        print("  (Cleaned up)\n")
except Exception as e:
    print(f"❌ Failed: {str(e)}\n")

# Test 2: email, password, name
print("Test 2: email + password + name")
try:
    response = supabase.table('app_users').insert({
        'email': 'test2@example.com',
        'password': 'test_hash',
        'name': 'Test User'
    }).execute()
    print(f"✅ SUCCESS! Columns in response:")
    if response.data:
        for key in response.data[0].keys():
            print(f"  - {key}")
        # Delete it
        supabase.table('app_users').delete().eq('email', 'test2@example.com').execute()
        print("  (Cleaned up)\n")
except Exception as e:
    print(f"❌ Failed: {str(e)}\n")

# Test 3: Just email (minimal)
print("Test 3: email only")
try:
    response = supabase.table('app_users').insert({
        'email': 'test3@example.com'
    }).execute()
    print(f"✅ SUCCESS! Columns in response:")
    if response.data:
        for key, value in response.data[0].items():
            print(f"  - {key}: {value}")
        # Delete it
        supabase.table('app_users').delete().eq('email', 'test3@example.com').execute()
        print("  (Cleaned up)\n")
except Exception as e:
    print(f"❌ Failed: {str(e)}\n")

print("\n" + "=" * 80)
print("Based on these tests, we can determine the exact table schema.")
