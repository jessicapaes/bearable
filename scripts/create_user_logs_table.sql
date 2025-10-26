-- ============================================================================
-- Bearable App - User Logs Table Setup
-- ============================================================================
-- This script creates the user_logs table and Row Level Security policies
-- Run this in your Supabase SQL Editor
-- ============================================================================

-- Create user_logs table
CREATE TABLE IF NOT EXISTS user_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  
  -- Core health metrics
  pain_score NUMERIC,
  sleep_hours NUMERIC,
  mood_score NUMERIC,
  stress_score NUMERIC,
  wake_ups_n INTEGER,
  
  -- Condition and therapy tracking
  condition_today TEXT,
  therapy_used TEXT,
  therapy_on BOOLEAN,
  therapy_name TEXT,
  
  -- Menstrual cycle tracking
  menstruating_today BOOLEAN,
  cycle_day INTEGER,
  flow TEXT,
  pms_symptoms TEXT,
  
  -- Mental health metrics
  anxiety_score NUMERIC,
  patience_score NUMERIC,
  emotional_symptoms TEXT,
  
  -- Physical symptoms
  physical_symptoms TEXT,
  cravings TEXT,
  movement TEXT,
  
  -- Digestive health
  bowel_movements_n INTEGER,
  digestive_sounds TEXT,
  stool_consistency TEXT,
  
  -- Overall day rating
  good_day BOOLEAN,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Prevent duplicate entries for same user on same date
  UNIQUE(user_id, date)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_logs_user_id ON user_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_logs_date ON user_logs(date);
CREATE INDEX IF NOT EXISTS idx_user_logs_user_date ON user_logs(user_id, date DESC);

-- Enable Row Level Security
ALTER TABLE user_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for re-running script)
DROP POLICY IF EXISTS "Users can view own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can insert own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can update own logs" ON user_logs;
DROP POLICY IF EXISTS "Users can delete own logs" ON user_logs;

-- RLS Policy: Users can only view their own logs
CREATE POLICY "Users can view own logs" ON user_logs
  FOR SELECT 
  USING (auth.uid() = user_id);

-- RLS Policy: Users can only insert their own logs
CREATE POLICY "Users can insert own logs" ON user_logs
  FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can only update their own logs
CREATE POLICY "Users can update own logs" ON user_logs
  FOR UPDATE 
  USING (auth.uid() = user_id);

-- RLS Policy: Users can only delete their own logs
CREATE POLICY "Users can delete own logs" ON user_logs
  FOR DELETE 
  USING (auth.uid() = user_id);

-- ============================================================================
-- Trigger to automatically update updated_at timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists (for re-running script)
DROP TRIGGER IF EXISTS update_user_logs_updated_at ON user_logs;

-- Create trigger
CREATE TRIGGER update_user_logs_updated_at
    BEFORE UPDATE ON user_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Grant permissions (if needed)
-- ============================================================================
-- Grant authenticated users access to the table
GRANT SELECT, INSERT, UPDATE, DELETE ON user_logs TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE user_logs_id_seq TO authenticated;

-- ============================================================================
-- Verify table creation
-- ============================================================================
-- Check if table exists and RLS is enabled
SELECT 
    tablename, 
    rowsecurity as rls_enabled 
FROM pg_tables 
WHERE tablename = 'user_logs';

-- View RLS policies
SELECT * FROM pg_policies WHERE tablename = 'user_logs';

-- ============================================================================
-- SUCCESS!
-- ============================================================================
-- The user_logs table is now ready for use in the Bearable app
-- Users will be able to save and retrieve their health tracking data
-- ============================================================================

