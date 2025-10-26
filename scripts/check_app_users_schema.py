"""
Script to check the exact schema of the app_users table
"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("ERROR: Supabase credentials not found")
    exit(1)

supabase = create_client(url, key)
print("✅ Connected to Supabase\n")

# Try to insert a test user to see what columns are expected
print("=" * 80)
print("CHECKING app_users TABLE SCHEMA")
print("=" * 80)

# First, let's try inserting with the columns we're using in the app
test_user = {
    'name': 'Test User',
    'email': 'test@example.com',
    'password': 'hashed_password_here',
    'created_at': '2025-10-26T00:00:00'
}

print("\nAttempting to insert test user with columns:")
for key in test_user.keys():
    print(f"  - {key}")

try:
    # Try inserting (we'll delete it right after)
    response = supabase.table('app_users').insert(test_user).execute()

    if response.data and len(response.data) > 0:
        print("\n✅ INSERT SUCCESSFUL!")
        print("\nReturned data shows actual table columns:")

        inserted_row = response.data[0]
        for key, value in inserted_row.items():
            print(f"  ✓ {key}: {value}")

        # Delete the test user
        user_id = inserted_row.get('id')
        if user_id:
            supabase.table('app_users').delete().eq('id', user_id).execute()
            print(f"\n🗑️  Deleted test user (id: {user_id})")
    else:
        print("\n⚠️  Insert returned no data")

except Exception as e:
    print(f"\n❌ INSERT FAILED with error:")
    print(f"   {str(e)}")

    # Parse the error to find expected columns
    error_msg = str(e)
    if "column" in error_msg.lower():
        print("\n💡 This error tells us about the table schema:")
        print(f"   {error_msg}")

print("\n" + "=" * 80)
