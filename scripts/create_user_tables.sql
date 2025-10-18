-- Database schema for Pain Relief Map with user authentication
-- Run this in your Supabase SQL Editor or PostgreSQL database

-- Table: user_profiles
-- Stores additional user information beyond Supabase Auth
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Table: user_logs
-- Stores daily wellness logs for each user
CREATE TABLE IF NOT EXISTS user_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    
    -- Core symptoms
    pain_score INT CHECK (pain_score >= 0 AND pain_score <= 10),
    stress_score INT CHECK (stress_score >= 0 AND stress_score <= 10),
    anxiety_score INT CHECK (anxiety_score >= 0 AND anxiety_score <= 10),
    patience_score INT CHECK (patience_score >= 0 AND patience_score <= 10),
    mood_score INT CHECK (mood_score >= 0 AND mood_score <= 10),
    sleep_hours DECIMAL(3,1) CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    
    -- Conditions and therapies
    sex_at_birth VARCHAR(20),
    condition_today TEXT,
    therapy_used TEXT,
    
    -- Physical state
    movement TEXT,
    bowel_movements_n INT CHECK (bowel_movements_n >= 0),
    digestive_sounds VARCHAR(100),
    stool_consistency VARCHAR(100),
    
    -- Symptoms
    physical_symptoms TEXT,
    emotional_symptoms TEXT,
    cravings TEXT,
    
    -- Menstrual tracking
    menstruating_today BOOLEAN DEFAULT FALSE,
    cycle_day INT,
    flow VARCHAR(20),
    pms_symptoms TEXT,
    
    -- Therapy tracking
    therapy_on INT DEFAULT 0,
    therapy_name VARCHAR(200),
    
    -- Additional
    good_day BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Prevent duplicate entries for same user on same day
    UNIQUE(user_id, log_date)
);

-- Table: user_therapies
-- Track therapy sessions and their effects
CREATE TABLE IF NOT EXISTS user_therapies (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    therapy_name VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_logs_user_id ON user_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_logs_date ON user_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_user_logs_user_date ON user_logs(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_user_therapies_user_id ON user_therapies(user_id);
CREATE INDEX IF NOT EXISTS idx_user_therapies_active ON user_therapies(user_id, is_active);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_logs_updated_at BEFORE UPDATE ON user_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_therapies_updated_at BEFORE UPDATE ON user_therapies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_therapies ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only access their own data
CREATE POLICY "Users can view their own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile"
    ON user_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- User logs policies
CREATE POLICY "Users can view their own logs"
    ON user_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own logs"
    ON user_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own logs"
    ON user_logs FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own logs"
    ON user_logs FOR DELETE
    USING (auth.uid() = user_id);

-- User therapies policies
CREATE POLICY "Users can view their own therapies"
    ON user_therapies FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own therapies"
    ON user_therapies FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own therapies"
    ON user_therapies FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own therapies"
    ON user_therapies FOR DELETE
    USING (auth.uid() = user_id);

-- Grant permissions (adjust as needed)
GRANT ALL ON user_profiles TO authenticated;
GRANT ALL ON user_logs TO authenticated;
GRANT ALL ON user_therapies TO authenticated;

-- Sample view: Get user statistics
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.user_id,
    u.email,
    u.display_name,
    COUNT(l.id) as total_logs,
    AVG(l.pain_score) as avg_pain,
    AVG(l.stress_score) as avg_stress,
    AVG(l.sleep_hours) as avg_sleep,
    MIN(l.log_date) as first_log_date,
    MAX(l.log_date) as last_log_date
FROM user_profiles u
LEFT JOIN user_logs l ON u.user_id = l.user_id
GROUP BY u.user_id, u.email, u.display_name;

GRANT SELECT ON user_stats TO authenticated;

