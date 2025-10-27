-- ============================================================================
-- BEARABLE APP - ADD ROW LEVEL SECURITY TO EXISTING TABLES
-- Run this in your Supabase SQL Editor to secure your existing tables
-- ============================================================================

-- Enable RLS on user_logs (if not already enabled)
ALTER TABLE user_logs ENABLE ROW LEVEL SECURITY;

-- Enable RLS on user_profiles (if not already enabled)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICIES FOR user_logs
-- Users can only access their own log entries
-- ============================================================================

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Users can view own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can insert own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can update own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can delete own logs" ON user_logs;

-- Create new policies
CREATE POLICY "Users can view own logs" 
    ON user_logs FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own logs" 
    ON user_logs FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own logs" 
    ON user_logs FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own logs" 
    ON user_logs FOR DELETE 
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICIES FOR user_profiles
-- Users can only access their own profile
-- ============================================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;

-- Create new policies
CREATE POLICY "Users can view own profile" 
    ON user_profiles FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" 
    ON user_profiles FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" 
    ON user_profiles FOR UPDATE 
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICIES FOR user_therapies (if using this table)
-- ============================================================================

-- Enable RLS
ALTER TABLE user_therapies ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own therapies" ON user_therapies;
DROP POLICY IF EXISTS "Users can insert own therapies" ON user_therapies;
DROP POLICY IF EXISTS "Users can update own therapies" ON user_therapies;
DROP POLICY IF EXISTS "Users can delete own therapies" ON user_therapies;

-- Create policies
CREATE POLICY "Users can view own therapies" 
    ON user_therapies FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own therapies" 
    ON user_therapies FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own therapies" 
    ON user_therapies FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own therapies" 
    ON user_therapies FOR DELETE 
    USING (auth.uid() = user_id);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check that RLS is enabled
SELECT 
    tablename,
    rowsecurity as "RLS Enabled"
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('user_logs', 'user_profiles', 'user_therapies')
ORDER BY tablename;

-- Check policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE tablename IN ('user_logs', 'user_profiles', 'user_therapies')
ORDER BY tablename, policyname;

-- ============================================================================
-- SUCCESS! 🎉
-- Your existing tables now have proper Row Level Security
-- Users can only access their own data
-- ============================================================================

