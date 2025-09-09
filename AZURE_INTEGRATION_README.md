# Azure OpenAI Chat Integration

## Overview

This implementation connects a HIPAA-compliant healthcare AI platform to Azure OpenAI services with tenant-specific system prompts, RAG (Retrieval-Augmented Generation) function calling, and document management capabilities.

## Features

### ✅ Implemented Features

1. **Azure OpenAI Integration**
   - Streaming chat completions with GPT-4 Mini
   - Function calling support for document search
   - Error handling and retry logic
   - Health check endpoint

2. **Multi-Tenant Support**
   - Three practice configurations:
     - Amanda's Mental Health Practice
     - Robbie's Med Spa
     - Dr. Emmer's Dermatology & Plastic Surgery
   - Tenant-specific system prompts
   - Isolated data and chat histories
   - Custom branding per practice

3. **RAG Function Calling**
   - Automatic document search when relevant
   - Integration with n8n webhook for document retrieval
   - Source citation in responses
   - Confidence scoring

4. **Document Upload Interface**
   - Drag-and-drop file upload
   - Support for PDF, DOCX, DOC, TXT files
   - Progress tracking
   - HIPAA compliance notices

5. **API Endpoints**
   - `/api/chat` - Main chat endpoint with streaming support
   - Health check endpoint for service status

## Setup Instructions

### 1. Environment Configuration

Update your `.env.local` file with the following:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://adavi-mf694jmx-eastus2.cognitiveservices.azure.com
AZURE_OPENAI_API_KEY=your-actual-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# n8n RAG Configuration
N8N_RAG_WEBHOOK_URL=https://your-n8n-instance.render.com/webhook/rag-search

# Google Drive Configuration (for document upload)
GOOGLE_DRIVE_CLIENT_ID=your-google-client-id
GOOGLE_DRIVE_CLIENT_SECRET=your-google-client-secret
```

### 2. Installation

```bash
# Install dependencies
npm install --legacy-peer-deps

# Run development server
npm run dev
```

### 3. Access Points

- **Main Azure Chat Interface**: http://localhost:3000/azure-chat
- **Original Interface**: http://localhost:3000
- **Ollama Test**: http://localhost:3000/test-ollama

## File Structure

```
/lib
  /api
    - azure-openai-client.ts    # Azure OpenAI client with streaming
    - rag-handler.ts            # RAG document search handler
  /config
    - tenants.ts                # Tenant configurations and prompts

/components/ui
  - tenant-selector.tsx         # Practice selector component
  - document-upload.tsx         # Document upload interface

/app
  /api/chat
    - route.ts                  # API endpoint for chat
  /azure-chat
    - page.tsx                  # Azure chat page

- chat-interface-azure.tsx     # Main Azure chat interface component
```

## Usage Guide

### 1. Selecting a Practice

Use the dropdown in the header to switch between practices:
- Each practice has unique system prompts
- Chat history is cleared when switching (HIPAA compliance)
- UI theme changes based on selected practice

### 2. Chat Features

- **Regular Chat**: Type and send messages normally
- **Search Docs**: Enable document search for RAG-powered responses
- **Deep Think**: Enhanced reasoning mode
- **Upload**: Access document upload interface

### 3. Document Upload

1. Click the Upload button in the chat interface
2. Drag and drop files or browse to select
3. Files are automatically uploaded and processed
4. Documents become searchable immediately after processing

## Testing Checklist

- [ ] Azure OpenAI connection successful
- [ ] Streaming responses working (<3 second initial response)
- [ ] Tenant switching clears chat history
- [ ] System prompts applied correctly per tenant
- [ ] RAG function calling triggers on relevant queries
- [ ] Document upload and processing pipeline works
- [ ] Error handling for network failures
- [ ] HIPAA compliance - no data leakage between tenants

## Security Considerations

1. **API Keys**: Never expose Azure API keys in frontend code
2. **Tenant Isolation**: Ensure complete data separation between practices
3. **HIPAA Compliance**: 
   - All PHI must be encrypted in transit and at rest
   - Implement audit logging for all interactions
   - Session timeout after inactivity
4. **Input Validation**: Sanitize all user inputs before processing

## Performance Optimization

1. **Streaming**: Chunk size optimized for smooth display
2. **Token Management**: Conversation history limited to prevent context overflow
3. **Caching**: Consider implementing response caching for common queries
4. **Error Recovery**: Automatic retry with exponential backoff

## Troubleshooting

### Azure OpenAI Connection Issues
```bash
# Check API endpoint health
curl http://localhost:3000/api/chat
```

### Streaming Not Working
- Ensure Azure endpoint supports streaming
- Check browser console for WebSocket errors
- Verify CORS settings

### RAG Function Not Triggering
- Check if n8n webhook URL is configured
- Verify document search keywords in query
- Enable "Search Docs" mode in chat interface

## Next Steps

1. **Production Deployment**
   - Move API keys to secure environment variables
   - Implement proper authentication
   - Set up monitoring and analytics

2. **Enhanced Features**
   - Real Google Drive integration
   - Advanced document processing pipeline
   - Multi-modal support (images, charts)
   - Conversation export functionality

3. **Testing**
   - Unit tests for all components
   - Integration tests for API endpoints
   - End-to-end tests for complete workflows
   - Load testing for concurrent users

## Support

For issues or questions, please refer to the main project documentation or contact the development team.