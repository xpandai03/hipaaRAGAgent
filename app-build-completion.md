Let me analyze the current state and map out the cleanest path to
  achieve your goals.

  Current State Analysis

  What We Have:

  1. Working Azure OpenAI Chat - GPT-5-mini connected and streaming
  2. Local Storage - Chat persistence per browser session
  3. Basic Tenant System - Pre-defined tenants (Amanda, Robbie, Dr.
  Emmer)
  4. Thread Management - Each session has unique thread ID
  5. System Prompts - Hard-coded per tenant

  What You Want:

  1. User-Editable System Prompts - Let users customize AI behavior
  2. RAG Integration - Connect to n8n workflow for Google Drive files
  3. User Authentication - Login system with isolated data
  4. Per-User Persistence - System prompts, chats, files per user

  Cleanest Implementation Path

  Phase 1: Authentication Foundation (Week 1)

  Why First: Everything else depends on knowing WHO the user is

  1. NextAuth.js Setup
    - Easiest auth for Next.js
    - Supports multiple providers (Google would align with Drive)
    - Session management built-in
    - Database adapter for user data
  2. Database Choice: Supabase
    - Free tier generous
    - Built-in auth (backup option)
    - PostgreSQL (reliable for medical data)
    - Real-time subscriptions (future feature)
    - Row-level security (HIPAA compliance)

  Phase 2: User Data Layer (Week 1-2)

  Database Schema:
  users (from NextAuth)
  ├── id
  ├── email
  ├── name

  user_settings
  ├── user_id (FK)
  ├── system_prompt
  ├── preferences (JSON)

  chat_threads
  ├── id
  ├── user_id (FK)
  ├── title
  ├── created_at
  ├── updated_at

  chat_messages
  ├── thread_id (FK)
  ├── role
  ├── content
  ├── created_at

  uploaded_files
  ├── user_id (FK)
  ├── file_name
  ├── drive_file_id
  ├── n8n_workflow_id
  ├── uploaded_at

  Phase 3: System Prompt Editor (Week 2)

  Simple Implementation:
  1. Settings Modal in current UI
    - Textarea for system prompt
    - Save to user_settings table
    - Load on chat initialization
    - Default templates available
  2. Prompt Variables (Advanced)
    - {{userName}}, {{specialty}}, {{date}}
    - Token counter
    - Prompt history/versions

  Phase 4: n8n RAG Integration (Week 2-3)

  Architecture:
  User uploads to Drive → n8n webhook triggered
                       ↓
                n8n processes file
                (extract, chunk, embed)
                       ↓
                Store in vector DB
                (Pinecone/Weaviate)
                       ↓
                Return webhook to our app
                (file ready for chat)

  Our App Side:
  1. File Upload UI
    - Google Drive picker (uses same Google auth)
    - Or drag-drop with API upload
  2. RAG Toggle in Chat
    - Checkbox: "Include my documents"
    - Shows list of available files
    - Select which to include
  3. Modified API Route
  // If RAG enabled
  if (includeDocuments) {
    // Call n8n webhook first
    const context = await fetchRelevantContext(message, userId)
    // Prepend to system prompt
    systemPrompt += `\n\nRelevant documents:\n${context}`
  }

  Phase 5: Integration Points (Week 3)

  n8n Workflow Needs:
  1. Webhook Trigger - Receive queries from our app
  2. Vector Search - Find relevant chunks
  3. Response Webhook - Return context to our app

  Our App Needs:
  1. n8n Webhook URL - Environment variable
  2. API Key - For n8n authentication
  3. User File Mapping - Track which files belong to which user

  Technical Decisions

  Authentication: NextAuth.js + Google Provider

  - Why: Users already have Google for Drive
  - Benefit: Single sign-on for app + Drive access

  Database: Supabase

  - Why: Fastest to implement, great free tier
  - Alternative: PostgreSQL on Railway if need more control

  File Processing: n8n + Google Drive

  - Why: n8n already handles workflows well
  - Storage: Keep files in Drive, only store metadata

  Vector Database: Pinecone

  - Why: Best performance, generous free tier
  - Alternative: Supabase pgvector (simpler but slower)

  Implementation Order (Recommended)

  Week 1: Auth + Database

  1. Add NextAuth.js with Google provider
  2. Setup Supabase with schema
  3. Migrate localStorage to database
  4. Test user isolation

  Week 2: System Prompts + UI

  1. Add settings modal to UI
  2. Create prompt editor component
  3. Save/load from database
  4. Add prompt templates

  Week 3: RAG Integration

  1. Create n8n webhook workflow
  2. Add file upload UI
  3. Implement context fetching
  4. Test with sample documents

  Quick Wins First

  Before the full implementation, we could:

  1. Quick System Prompt Editor (2 hours)
    - Simple modal with textarea
    - Save to localStorage initially
    - No auth needed yet
  2. Basic n8n Integration (4 hours)
    - Hardcoded webhook for testing
    - Single shared document collection
    - Prove the concept works
  3. Simple Password Protection (1 hour)
    - Environment variable password
    - Basic gate before chat loads
    - Temporary until proper auth

  Risks & Mitigations

  1. HIPAA Compliance
    - Risk: Medical data exposure
    - Mitigation: Encrypt at rest, audit logs, signed BAAs
  2. Rate Limiting
    - Risk: Costs from excessive API calls
    - Mitigation: User quotas, caching, request throttling
  3. Context Window
    - Risk: RAG context too large
    - Mitigation: Smart chunking, relevance scoring

  Next Immediate Steps

  Option A: Quick Prototype (1 day)
  - Add system prompt editor (localStorage)
  - Basic n8n webhook integration
  - Test RAG with hardcoded files

  Option B: Production Path (1 week)
  - Start with NextAuth setup
  - Add Supabase database
  - Then build features properly

  Option C: Hybrid (Recommended)
  - Day 1: Quick system prompt editor
  - Day 2: Test n8n RAG integration
  - Week 2: Add proper auth/database

  Which path would you prefer? The hybrid approach lets you test the
  core features quickly while building the proper foundation in
  parallel.