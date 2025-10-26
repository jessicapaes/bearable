"""
Script to check Supabase database tables structure and contents
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
    print("❌ Supabase credentials not found in environment variables")
    exit(1)

try:
    supabase = create_client(url, key)
    print("✅ Successfully connected to Supabase\n")
except Exception as e:
    print(f"❌ Failed to connect to Supabase: {str(e)}")
    exit(1)

# List of tables to check based on your screenshot
tables = [
    'app_users',
    'user_profiles',
    'user_logs',
    'wellness_logs',
    'n1_data',
    'observations',
    'user_therapies',
    'evidence_counts',
    'evidence_pairs',
    'user_stats'
]

print("=" * 80)
print("CHECKING SUPABASE DATABASE TABLES")
print("=" * 80)

for table_name in tables:
    print(f"\n📊 Table: {table_name}")
    print("-" * 80)

    try:
        # Try to fetch first 5 rows to check structure
        response = supabase.table(table_name).select('*').limit(5).execute()

        if response.data:
            row_count = len(response.data)
            print(f"✅ Table exists - Found {row_count} row(s) (showing first 5)")

            # Show column names from first row
            if row_count > 0:
                columns = list(response.data[0].keys())
                print(f"📋 Columns ({len(columns)}): {', '.join(columns)}")

                # Show first row as sample
                print(f"\n📄 Sample row:")
                for key, value in response.data[0].items():
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 50:
                        str_value = str_value[:47] + "..."
                    print(f"   - {key}: {str_value}")
        else:
            print(f"⚠️  Table exists but is empty (0 rows)")

    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
            print(f"❌ Table does not exist")
        else:
            print(f"❌ Error accessing table: {error_msg}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

# Check app_users table specifically for authentication
print("\n🔐 Authentication Table (app_users) Details:")
try:
    response = supabase.table('app_users').select('*').execute()
    if response.data:
        print(f"   Total users: {len(response.data)}")
        for user in response.data:
            email = user.get('email', 'N/A')
            name = user.get('name', 'N/A')
            created = user.get('created_at', 'N/A')
            print(f"   - {name} ({email}) - Created: {created}")
    else:
        print("   No users found in database")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n✅ Database check complete!")
