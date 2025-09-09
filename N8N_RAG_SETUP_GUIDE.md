# n8n RAG Workflow Setup Guide

## Quick Start - Get RAG Working Now

### Step 1: Setup Database Tables
1. Connect to your Render PostgreSQL database
2. Run the SQL script: `setup-rag-database.sql`
   - This creates the `documents` table with sample medical data
   - Creates indexes for fast search

### Step 2: Import Simple Workflow to n8n
1. In n8n, click "Workflows" → "Add workflow" → "Import from file"
2. Choose `n8n-simple-rag-workflow.json` (start with simple version)
3. You'll see 3 nodes: Webhook → Search Documents → Return Results

### Step 3: Configure PostgreSQL Credentials
1. Click on the "Search Documents" node
2. Click on "Credentials" dropdown
3. Select "Create New" for PostgreSQL
4. Enter your Render database details:
   - **Host**: `dpg-d2tjrb0gjchc739ujee0-a.oregon-postgres.render.com`
   - **Database**: `hipaa_gpt_db`
   - **User**: `hipaa_gpt_db_user`
   - **Password**: `GDHcLMxieiyb15s3Ni0xgeETEzJgRePI`
   - **Port**: `5432`
   - **SSL**: Enable (Required for Render)
5. Click "Create" to save credentials

### Step 4: Activate and Get Webhook URL
1. Click "Active" toggle in top-right to activate workflow
2. Click on "RAG Search Webhook" node
3. Copy the webhook URL (looks like: `https://your-n8n.app.n8n.cloud/webhook/rag-search`)

### Step 5: Update Your App Configuration
Update `.env.local` with your actual n8n webhook URL:
```
N8N_WEBHOOK_URL=https://your-n8n.app.n8n.cloud/webhook/rag-search
```

### Step 6: Test It
1. Restart your Next.js dev server
2. Go to Settings in chat interface
3. Enable "RAG Search"
4. Ask a medical question like "tell me about diabetes management"
5. The assistant should find and use the relevant document

## Troubleshooting

### If webhook returns 404:
- Make sure workflow is ACTIVE (toggle in top-right)
- Check webhook path matches exactly: `/rag-search`

### If no documents found:
- Verify PostgreSQL credentials are correct
- Check that documents table exists with data
- Test the SQL query directly in database

### If connection fails:
- Ensure SSL is enabled in PostgreSQL credentials
- Check n8n instance is accessible from internet
- Verify webhook URL is complete with https://

## How It Works

1. **User asks question** → Chat interface sends query to `/api/rag/search`
2. **API calls n8n webhook** → Sends `{ query, userId, tenant }`
3. **n8n searches database** → Uses SQL ILIKE for text matching
4. **Returns documents** → Sends matching content back
5. **Chat uses context** → Includes documents in Azure OpenAI prompt

## Next Steps (After Basic Works)

Once simple RAG is working, you can:
1. Upgrade to vector search workflow (`n8n-vector-rag-workflow.json`)
2. Add document upload functionality
3. Connect Google Drive for automatic document sync

## Testing Without n8n (Quick Check)

To verify your database setup works, run this in PostgreSQL:
```sql
SELECT content, metadata 
FROM documents 
WHERE content ILIKE '%diabetes%' 
LIMIT 5;
```

You should see the diabetes management document.