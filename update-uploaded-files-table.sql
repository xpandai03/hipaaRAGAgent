-- Update the UploadedFile table to add new columns for N8N processing
ALTER TABLE "UploadedFile" 
  ADD COLUMN IF NOT EXISTS "processingStatus" VARCHAR(50) DEFAULT 'pending',
  ADD COLUMN IF NOT EXISTS "n8nProcessedAt" TIMESTAMP,
  ADD COLUMN IF NOT EXISTS "errorMessage" TEXT;

-- Migrate existing isProcessed to processingStatus
UPDATE "UploadedFile" 
SET "processingStatus" = CASE 
  WHEN "isProcessed" = true THEN 'completed'
  ELSE 'pending'
END
WHERE "processingStatus" IS NULL;

-- Drop the old column (optional - can keep for backward compatibility)
-- ALTER TABLE "UploadedFile" DROP COLUMN IF EXISTS "isProcessed";

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS "UploadedFile_processingStatus_idx" ON "UploadedFile"("processingStatus");