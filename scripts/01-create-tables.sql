-- Create games table
CREATE TABLE IF NOT EXISTS games (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  image_url TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create card_packages table
CREATE TABLE IF NOT EXISTS card_packages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  name VARCHAR(200) NOT NULL,
  points INTEGER NOT NULL,
  price_egp DECIMAL(10,2) NOT NULL,
  bonus_description VARCHAR(200),
  is_active BOOLEAN DEFAULT true,
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create admin_users table
CREATE TABLE IF NOT EXISTS admin_users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_games_slug ON games(slug);
CREATE INDEX IF NOT EXISTS idx_games_active ON games(is_active);
CREATE INDEX IF NOT EXISTS idx_card_packages_game_id ON card_packages(game_id);
CREATE INDEX IF NOT EXISTS idx_card_packages_active ON card_packages(is_active);
CREATE INDEX IF NOT EXISTS idx_card_packages_sort ON card_packages(sort_order);

-- Enable Row Level Security
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE card_packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Allow public read access to active games" ON games
  FOR SELECT USING (is_active = true);

CREATE POLICY "Allow public read access to active card packages" ON card_packages
  FOR SELECT USING (is_active = true);

-- Admin policies (will be handled by service role key)
CREATE POLICY "Allow admin full access to games" ON games
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow admin full access to card packages" ON card_packages
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow admin full access to admin users" ON admin_users
  FOR ALL USING (auth.role() = 'service_role');
