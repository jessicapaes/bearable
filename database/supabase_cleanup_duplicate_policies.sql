-- ============================================================================
-- CLEANUP DUPLICATE RLS POLICIES
-- Remove old policies, keep the new ones
-- ============================================================================

-- user_logs - Remove old policies
DROP POLICY IF EXISTS "Users can delete their own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can insert their own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can update their own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can view their own logs" ON user_logs;

-- user_profiles - Remove old/duplicate policies
DROP POLICY IF EXISTS "Users can update their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Enable insert for authenticated users creating their profile" ON user_profiles;

-- user_therapies - Remove old policies
DROP POLICY IF EXISTS "Users can delete their own therapies" ON user_therapies;
DROP POLICY IF EXISTS "Users can insert their own therapies" ON user_therapies;
DROP POLICY IF EXISTS "Users can update their own therapies" ON user_therapies;
DROP POLICY IF EXISTS "Users can view their own therapies" ON user_therapies;

-- ============================================================================
-- VERIFICATION - Should only show new policies (without "their own")
-- ============================================================================

SELECT 
    tablename,
    policyname,
    cmd
FROM pg_policies
WHERE tablename IN ('user_logs', 'user_profiles', 'user_therapies')
ORDER BY tablename, cmd;

-- ============================================================================
-- SUCCESS! 🎉
-- Duplicate policies removed, only clean ones remain
-- ============================================================================

