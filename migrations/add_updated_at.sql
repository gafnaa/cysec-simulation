-- Add updated_at column if it doesn't exist
ALTER TABLE products
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP;