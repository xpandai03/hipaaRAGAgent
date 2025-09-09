# Medical AI Chat Interface - Project Context

## Overview
This is a HIPAA-compliant healthcare AI platform chat interface that connects to Azure OpenAI GPT-5-mini. The interface is built with Next.js 15.2.4 and features streaming responses, chat persistence, and tenant-specific system prompts.

## Current Status: ⚠️ AWAITING AZURE DEPLOYMENT CREATION

### The Critical Issue
**No Azure OpenAI deployment exists yet!** The Azure resource has the models available but no deployments created. This is why all API calls return "DeploymentNotFound" errors.

## Azure Credentials (Working & Verified)
```
Endpoint: https://adavi-mf694jmx-eastus2.cognitiveservices.azure.com
API Key: YOUR_AZURE_API_KEY_HERE
```

## Available Models on Azure Resource
- `gpt-5-mini-2025-08-07` ✅ (Available but NOT deployed)
- `gpt-5-nano-2025-08-07` ✅ (Available but NOT deployed)
- `gpt-5-chat-2025-08-07` ✅ (Available but NOT deployed)
- `gpt-4o-mini-2024-07-18` ✅ (Available but NOT deployed)

## What's Been Built

### 1. Main Chat Interface (`/chat-interface-v0-azure.tsx`)
- ✅ V0 design with DeepSearch and Think buttons
- ✅ Streaming response support
- ✅ Chat persistence with localStorage
- ✅ Thread-based conversation management
- ✅ Hamburger menu with saved chats sidebar
- ✅ Auto-save and delete functionality
- ✅ Handles both streaming and non-streaming responses

### 2. API Route (`/app/api/chat/route.ts`)
- ✅ Server-side Azure OpenAI calls (avoids CORS)
- ✅ Comprehensive logging for debugging
- ✅ Tries multiple deployment names and API versions
- ✅ Supports streaming via Server-Sent Events (SSE)
- ✅ Fallback to non-streaming if streaming fails

### 3. Azure OpenAI Client (`/lib/api/azure-openai-client.ts`)
- ✅ OpenAI SDK configuration for Azure
- ✅ Streaming chat completion support
- ✅ Error handling and retry logic

### 4. Chat Storage System (`/lib/storage/chat-storage.ts`)
- ✅ Thread-based chat management
- ✅ Automatic title generation (first 30 chars)
- ✅ Tenant isolation support (Amanda, Robbie, Dr. Emmer)
- ✅ localStorage persistence
- ✅ Thread lifecycle management

### 5. Tenant System (`/lib/tenants/tenant-config.ts`)
- ✅ Three practice configurations
- ✅ Custom system prompts per practice
- ✅ HIPAA-compliant settings

### 6. UI Components
- ✅ Saved chats sidebar (`/components/ui/saved-chats-sidebar.tsx`)
- ✅ All shadcn/ui components configured

## What Needs to Be Done

### IMMEDIATE ACTION REQUIRED:
1. **Create Azure Deployment**
   - Go to Azure Portal → Your OpenAI Resource
   - Click "Model deployments" → "+ Create"
   - Select model: `gpt-5-mini-2025-08-07`
   - Give it a deployment name (e.g., "gpt5mini")
   - Click "Create"
   - Wait 2-3 minutes for deployment

2. **Update Deployment Name**
   Once deployment is created, update these files with the exact deployment name:
   - `/app/api/chat/route.ts` - Line 20 (first in deploymentOptions array)
   - `/lib/api/azure-openai-client.ts` - Line 11 (DEPLOYMENT_NAME constant)

3. **Test Connection**
   - Edit `/test-azure.sh` and replace `YOUR_DEPLOYMENT_NAME_HERE`
   - Run: `./test-azure.sh`
   - Should return: "I am working!"

## Running the Application
```bash
# Start development server
npm run dev

# Access at
http://localhost:3000/chat
```

## Known Issues & Solutions

### Error: "DeploymentNotFound"
**Cause:** No deployment exists in Azure
**Solution:** Create deployment in Azure Portal (see above)

### Error: "Sorry, I encountered an error"
**Cause:** API call failed
**Solution:** Check console logs, usually deployment name issue

### No response after sending message
**Cause:** API route not finding working deployment
**Solution:** Create Azure deployment first

## File Structure
```
/chat-interface (2)
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts          # API endpoint for Azure OpenAI
│   └── chat/
│       └── page.tsx              # Chat page wrapper
├── lib/
│   ├── api/
│   │   └── azure-openai-client.ts  # Azure OpenAI client
│   ├── storage/
│   │   └── chat-storage.ts         # Chat persistence
│   └── tenants/
│       └── tenant-config.ts        # Tenant configurations
├── components/
│   └── ui/
│       └── saved-chats-sidebar.tsx # Saved chats UI
├── chat-interface-v0-azure.tsx     # Main chat interface
└── test-azure.sh                   # Test script for Azure connection
```

## Testing Deployment Names
The API route currently tries these deployment names:
1. gpt-5-mini
2. gpt5-mini  
3. gpt-5
4. gpt5
5. gpt-4o-mini

With API versions:
- 2024-08-01-preview
- 2024-02-01
- 2023-12-01-preview

## Debug Commands
```bash
# List available models (works)
curl -X GET "https://adavi-mf694jmx-eastus2.cognitiveservices.azure.com/openai/models?api-version=2024-02-01" \
  -H "api-key: YOUR_AZURE_API_KEY_HERE"

# Test specific deployment (replace DEPLOYMENT_NAME)
curl -X POST "https://adavi-mf694jmx-eastus2.cognitiveservices.azure.com/openai/deployments/DEPLOYMENT_NAME/chat/completions?api-version=2024-02-01" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_AZURE_API_KEY_HERE" \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "temperature": 0.7, "max_tokens": 50}'
```

## Success Criteria
- [x] Chat interface loads without errors
- [x] Can send messages without client errors
- [ ] Receives responses from Azure OpenAI
- [ ] Streaming works properly
- [x] Chat history saves and loads
- [x] Hamburger menu shows past chats
- [x] Can delete chats

## Next Steps After Deployment Creation
1. Update deployment name in code
2. Test with test-azure.sh script
3. Verify streaming responses work
4. Test all three response modes (normal, DeepSearch, Think)
5. Verify chat persistence across sessions
6. Test tenant switching functionality

## Contact for Issues
If deployment exists but still getting errors:
1. Check deployment name exactly matches (case-sensitive)
2. Verify API version compatibility
3. Check Azure logs for rate limiting
4. Ensure deployment is in "Succeeded" state
5. Try with non-streaming first (simpler to debug)

---
*Last Updated: September 5, 2025 at 1:40 AM*
*Status: Waiting for Azure deployment to be created*