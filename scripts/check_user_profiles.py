"""
Check user_profiles table schema
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

print("Checking user_profiles table structure...\n")

# Test with minimal data first
print("Test 1: Insert minimal record to discover required columns")
try:
    response = supabase.table('user_profiles').insert({
        'email': 'test@example.com'
    }).execute()
    print(f"✅ SUCCESS with just email! Columns:")
    if response.data:
        for key, value in response.data[0].items():
            print(f"  - {key}: {value}")
        # Delete
        user_id = response.data[0].get('user_id')
        if user_id:
            supabase.table('user_profiles').delete().eq('user_id', user_id).execute()
        print("  (Cleaned up)\n")
except Exception as e:
    print(f"❌ Failed: {str(e)}\n")

# Test with more fields
print("Test 2: Try with email + display_name + password")
try:
    response = supabase.table('user_profiles').insert({
        'email': 'test2@example.com',
        'display_name': 'Test User',
        'password': 'hashed_password'
    }).execute()
    print(f"✅ SUCCESS! Columns:")
    if response.data:
        for key, value in response.data[0].items():
            print(f"  - {key}: {value}")
        # Delete
        user_id = response.data[0].get('user_id')
        if user_id:
            supabase.table('user_profiles').delete().eq('user_id', user_id).execute()
        print("  (Cleaned up)\n")
except Exception as e:
    print(f"❌ Failed: {str(e)}\n")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print("Based on the results, I'll determine which table to use for authentication.")
