-- Update image_url for existing games to use the new logo paths
UPDATE games
SET image_url = '/images/game-logos/crossfire-logo.png'
WHERE slug = 'crossfire';

UPDATE games
SET image_url = '/images/game-logos/free-fire-logo.png'
WHERE slug = 'free-fire';

UPDATE games
SET image_url = '/images/game-logos/pubg-mobile-logo.png'
WHERE slug = 'pubg-mobile';
