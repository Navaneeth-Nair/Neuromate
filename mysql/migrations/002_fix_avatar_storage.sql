-- Migration: Fix avatar storage to support larger base64 encoded images
-- This migration changes the avatar_url column from TEXT to LONGTEXT

-- For existing databases, run this migration:
ALTER TABLE profiles MODIFY COLUMN avatar_url LONGTEXT;

-- Verify the change
DESCRIBE profiles;
