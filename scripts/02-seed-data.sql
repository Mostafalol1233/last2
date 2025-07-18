-- Insert sample games
INSERT INTO games (name, slug, description, image_url, is_active) VALUES
('CrossFire', 'crossfire', 'Top up your CrossFire account with instant delivery', '/placeholder.svg?height=200&width=300', true),
('Free Fire', 'free-fire', 'Get Free Fire diamonds and dominate the battlefield', '/placeholder.svg?height=200&width=300', true),
('PUBG Mobile', 'pubg-mobile', 'Purchase UC for PUBG Mobile and unlock premium content', '/placeholder.svg?height=200&width=300', true);

-- Insert sample card packages for CrossFire
INSERT INTO card_packages (game_id, name, points, price_egp, bonus_description, is_active, sort_order) 
SELECT 
  g.id,
  '5,000 Points (Half Bonus)',
  5000,
  120.00,
  'Get 50% extra points',
  true,
  1
FROM games g WHERE g.slug = 'crossfire';

INSERT INTO card_packages (game_id, name, points, price_egp, bonus_description, is_active, sort_order) 
SELECT 
  g.id,
  '10,000 Points (Half Bonus)',
  10000,
  240.00,
  'Get 50% extra points',
  true,
  2
FROM games g WHERE g.slug = 'crossfire';

INSERT INTO card_packages (game_id, name, points, price_egp, bonus_description, is_active, sort_order) 
SELECT 
  g.id,
  '20,000 Points (Extra Bonus)',
  20000,
  470.00,
  'Get extra bonus points',
  true,
  3
FROM games g WHERE g.slug = 'crossfire';

INSERT INTO card_packages (game_id, name, points, price_egp, bonus_description, is_active, sort_order) 
SELECT 
  g.id,
  '30,000 Points (Special Bonus)',
  30000,
  700.00,
  'Get special bonus points',
  true,
  4
FROM games g WHERE g.slug = 'crossfire';

-- Insert sample packages for Free Fire
INSERT INTO card_packages (game_id, name, points, price_egp, bonus_description, is_active, sort_order) 
SELECT 
  g.id,
  '100 Diamonds',
  100,
  25.00,
  'Perfect for beginners',
  true,
  1
FROM games g WHERE g.slug = 'free-fire';

INSERT INTO card_packages (game_id, name, points, price_egp, bonus_description, is_active, sort_order) 
SELECT 
  g.id,
  '500 Diamonds',
  500,
  120.00,
  'Most popular choice',
  true,
  2
FROM games g WHERE g.slug = 'free-fire';

-- Insert sample packages for PUBG Mobile
INSERT INTO card_packages (game_id, name, points, price_egp, bonus_description, is_active, sort_order) 
SELECT 
  g.id,
  '60 UC',
  60,
  15.00,
  'Basic UC package',
  true,
  1
FROM games g WHERE g.slug = 'pubg-mobile';

INSERT INTO card_packages (game_id, name, points, price_egp, bonus_description, is_active, sort_order) 
SELECT 
  g.id,
  '325 UC',
  325,
  75.00,
  'Popular UC package',
  true,
  2
FROM games g WHERE g.slug = 'pubg-mobile';

-- Insert default admin user (password: admin123)
-- Note: In production, use a proper password hashing library
INSERT INTO admin_users (username, password_hash) VALUES
('admin', '$2a$10$rOzJqQZQQQQQQQQQQQQQQOeKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK');
