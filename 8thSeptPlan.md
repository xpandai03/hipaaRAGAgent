
    🎯 Goal

    Create a flawless system where users can:
    1. Dynamically adjust system prompts that actually take effect
    2. Drag-and-drop upload documents seamlessly
    3. Get properly formatted responses with document citations
    4. Have a smooth, professional experience

    📋 Issues to Fix

    Issue 1: System Prompt Not Working

    - Problem: System prompt is hardcoded in FastAPI, user changes 
    have no effect
    - Solution: Pass system prompt from frontend through API to 
    FastAPI

    Issue 2: No Drag-and-Drop Upload

    - Problem: Current upload requires clicking a button
    - Solution: Add drag-and-drop zone with visual feedback

    Issue 3: No Document Citations

    - Problem: AI doesn't cite which document chunks it's using
    - Solution: Include source metadata in responses

    Issue 4: Too Many Duplicate Processes

    - Problem: Multiple npm dev servers running
    - Solution: Clean up all duplicates, keep only necessary services

    🛠️ Implementation Plan

    Phase 1: Fix System Prompt Flow

    1. Update API Route (app/api/chat/fastapi/route.ts)
      - Extract system prompt from user settings/database
      - Pass system prompt in request to FastAPI
    2. Update FastAPI (rag_service.py)
      - Accept system_prompt parameter in chat endpoint
      - Use provided prompt instead of hardcoded one
      - Default to standard prompt if none provided
    3. Update Frontend (chat-interface-v0-azure.tsx)
      - Ensure system prompt from settings is included in API calls
      - Add visual indicator showing current system prompt

    Phase 2: Enhance Document Upload

    1. Add Drag-and-Drop (components/document-upload.tsx)
      - Create drop zone with visual states (idle, hover, uploading)
      - Support multiple file formats (PDF, TXT, DOCX)
      - Show file preview before upload
      - Add progress indicators
    2. Improve PDF Processing (rag_service.py)
      - Better error handling for corrupted PDFs
      - Extract metadata (title, author, date)
      - Handle multi-column layouts

    Phase 3: Add Document Citations

    1. Enhance RAG Response (rag_service.py)
      - Include chunk metadata in search results
      - Format citations in responses
      - Add relevance scores
    2. Update Response Display (chat-interface-v0-azure.tsx)
      - Show citations as footnotes or inline references
      - Link to source documents
      - Display confidence scores

    Phase 4: Clean System & Best Practices

    1. Process Management
      - Kill all duplicate npm processes
      - Create startup script for clean launches
      - Add process monitoring
    2. User Isolation
      - Implement user-specific document storage
      - Add document management (list, delete)
      - Secure document access by user ID
    3. Performance & UX
      - Add response caching
      - Implement streaming with proper buffering
      - Add loading states and error boundaries
      - Create user onboarding flow

    📊 Technical Details

    API Request Structure

    {
      query: string,
      session_id: string,
      system_prompt: string,  // NEW
      max_tokens: number,
      temperature: number,
      top_k: number,
      include_citations: boolean  // NEW
    }

    Response with Citations

    {
      "content": "Based on the document...",
      "citations": [
        {
          "document": "release_authorization.pdf",
          "chunk_id": 42,
          "relevance": 0.89,
          "excerpt": "...relevant text..."
        }
      ]
    }

    🚀 Expected Outcomes

    1. System prompts will immediately affect responses
    2. Drag-and-drop upload with visual feedback
    3. Responses include proper citations
    4. Clean, professional user experience
    5. Proper user isolation and security
    6. No duplicate processes or resource waste

    ⏱️ Implementation Order

    1. Fix system prompt (Critical - 15 mins)
    2. Clean up processes (Important - 5 mins)
    3. Add drag-and-drop (Enhancement - 20 mins)
    4. Add citations (Enhancement - 25 mins)
    5. User isolation (Security - 15 mins)

    This plan follows best practices:
    - Progressive enhancement
    - User-centric design
    - Security first
    - Clean architecture
    - Proper error handli