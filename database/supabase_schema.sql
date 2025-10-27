-- ============================================================================
-- BEARABLE APP - SUPABASE DATABASE SCHEMA
-- Run this SQL in Supabase SQL Editor to set up your database
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: user_health_data
-- Stores daily health tracking entries for each user
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_health_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Pain tracking
    pain_level INTEGER CHECK (pain_level >= 0 AND pain_level <= 10),
    pain_areas TEXT[], -- Array of pain locations
    
    -- Sleep tracking
    sleep_hours DECIMAL(4,2) CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    sleep_quality INTEGER CHECK (sleep_quality >= 1 AND sleep_quality <= 5),
    
    -- Mood tracking
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    
    -- Activity tracking
    activities TEXT[], -- Array of activities performed
    exercise_minutes INTEGER CHECK (exercise_minutes >= 0),
    
    -- Therapy tracking
    therapies_used TEXT[], -- Array of therapies used
    therapy_started_today TEXT, -- New therapy started
    
    -- Symptoms
    symptoms TEXT[], -- Array of symptoms
    symptom_severity INTEGER CHECK (symptom_severity >= 1 AND symptom_severity <= 5),
    
    -- Diet/Triggers
    foods TEXT[], -- Array of foods consumed
    potential_triggers TEXT[], -- Array of potential triggers
    
    -- Medication
    medications TEXT[], -- Array of medications taken
    
    -- Women's health
    menstrual_cycle_day INTEGER CHECK (menstrual_cycle_day >= 1 AND menstrual_cycle_day <= 45),
    period_started BOOLEAN DEFAULT FALSE,
    
    -- Notes
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, date) -- One entry per user per day
);

-- Index for faster queries
DROP INDEX IF EXISTS idx_user_health_data_user_date;
CREATE INDEX idx_user_health_data_user_date ON user_health_data(user_id, date DESC);

DROP INDEX IF EXISTS idx_user_health_data_user_therapies;
CREATE INDEX idx_user_health_data_user_therapies ON user_health_data USING GIN(therapies_used);

-- ============================================================================
-- TABLE: user_profiles
-- Stores user preferences and settings
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- User info
    full_name TEXT,
    email TEXT,
    
    -- Preferences
    primary_condition TEXT,
    health_goals TEXT[],
    
    -- Settings
    notifications_enabled BOOLEAN DEFAULT TRUE,
    data_sharing_enabled BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for user lookup
DROP INDEX IF EXISTS idx_user_profiles_user_id;
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- ============================================================================
-- TABLE: user_therapy_effects
-- Stores calculated therapy effectiveness analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_therapy_effects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    therapy_name TEXT NOT NULL,
    
    -- Effect metrics
    pain_reduction_percent DECIMAL(5,2),
    sleep_improvement_percent DECIMAL(5,2),
    mood_improvement_percent DECIMAL(5,2),
    
    -- Statistical confidence
    confidence_level DECIMAL(3,2) CHECK (confidence_level >= 0 AND confidence_level <= 1),
    sample_size INTEGER,
    
    -- Date range
    start_date DATE,
    end_date DATE,
    
    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, therapy_name)
);

-- Index for therapy lookups
CREATE INDEX idx_therapy_effects_user ON user_therapy_effects(user_id, therapy_name);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Ensures users can only access their own data
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE user_health_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_therapy_effects ENABLE ROW LEVEL SECURITY;

-- Policies for user_health_data
DROP POLICY IF EXISTS "Users can view own health data" ON user_health_data;
CREATE POLICY "Users can view own health data" 
    ON user_health_data FOR SELECT 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own health data" ON user_health_data;
CREATE POLICY "Users can insert own health data" 
    ON user_health_data FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own health data" ON user_health_data;
CREATE POLICY "Users can update own health data" 
    ON user_health_data FOR UPDATE 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own health data" ON user_health_data;
CREATE POLICY "Users can delete own health data" 
    ON user_health_data FOR DELETE 
    USING (auth.uid() = user_id);

-- Policies for user_profiles
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
CREATE POLICY "Users can view own profile" 
    ON user_profiles FOR SELECT 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
CREATE POLICY "Users can insert own profile" 
    ON user_profiles FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
CREATE POLICY "Users can update own profile" 
    ON user_profiles FOR UPDATE 
    USING (auth.uid() = user_id);

-- Policies for user_therapy_effects
DROP POLICY IF EXISTS "Users can view own therapy effects" ON user_therapy_effects;
CREATE POLICY "Users can view own therapy effects" 
    ON user_therapy_effects FOR SELECT 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own therapy effects" ON user_therapy_effects;
CREATE POLICY "Users can insert own therapy effects" 
    ON user_therapy_effects FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own therapy effects" ON user_therapy_effects;
CREATE POLICY "Users can update own therapy effects" 
    ON user_therapy_effects FOR UPDATE 
    USING (auth.uid() = user_id);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for user_health_data
DROP TRIGGER IF EXISTS update_user_health_data_updated_at ON user_health_data;
CREATE TRIGGER update_user_health_data_updated_at
    BEFORE UPDATE ON user_health_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_profiles
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA (Optional)
-- ============================================================================

-- You can add any seed data here if needed

-- ============================================================================
-- VERIFICATION QUERIES
-- Run these to verify your setup
-- ============================================================================

-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE';

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- ============================================================================
-- SUCCESS! 🎉
-- Your database is ready for the Bearable app
-- ============================================================================

