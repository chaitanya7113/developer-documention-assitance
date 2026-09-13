                         USER
                          │
                          ▼
              ┌─────────────────────┐
              │   React Frontend    │
              │   JavaScript        │
              └──────────┬──────────┘
                         │
                    HTTP / JSON
                         │
                         ▼
              ┌─────────────────────┐
              │    Django + DRF     │
              │      Backend        │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │    RAG Service      │
              │                     │
              │  1. Query           │
              │  2. Embedding       │
              │  3. Retrieval       │
              │  4. Context         │
              │  5. LLM             │
              └───────┬─────┬───────┘
                      │     │
             ┌────────┘     └─────────┐
             ▼                        ▼
     ┌─────────────────┐      ┌─────────────────┐
     │  Vector Store   │      │   PostgreSQL    │
     │                 │      │                 │
     │ Embeddings      │      │ Users           │
     │ Chunks          │      │ Conversations   │
     │ Metadata        │      │ Messages        │
     └─────────────────┘      └─────────────────┘
                      │
                      ▼
               ┌─────────────┐
               │     LLM     │
               └─────────────┘



               Flow A — Document ingestion

               React Markdown Files
                        │
                        ▼
                Document Loader
                        │
                        ▼
                    Text
                        │
                        ▼
                    Chunking
                        │
                        ▼
                Text Chunks
                        │
                        ▼
                    Embedding
                        │
                        ▼
                Vector Database



                Flow B — User asks a question



                User Question
                    │
                    ▼
                React Frontend
                    │
                    │ POST /api/chat/
                    ▼
                Django REST API
                    │
                    ▼
                RAG Service
                    │
                    ▼
                Create Query Embedding
                    │
                    ▼
                Search Vector Database
                    │
                    ▼
                Top Relevant Chunks
                    │
                    ▼
                Build Prompt
                    │
                    ▼
                LLM
                    │
                    ▼
                Answer + Sources
                    │
                    ▼
                Django API
                    │
                    ▼
                React
                    │
                    ▼
                User



       frontend/
│
├── src/
│   ├── components/
│   │   ├── ChatBox.jsx
│   │   ├── Message.jsx
│   │   └── SourceCard.jsx
│   │
│   ├── pages/
│   │   └── ChatPage.jsx
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── hooks/
│   │
│   ├── App.jsx
│   └── main.jsx
│
└── package.json



┌─────────────────────────────────────────────┐
│ Developer Documentation Assistant           │
├─────────────────────────────────────────────┤
│                                             │
│ User: How does useEffect work?              │
│                                             │
│ AI: useEffect lets you synchronize...       │
│                                             │
│ Sources:                                    │
│ ┌─────────────────────────────────────────┐ │
│ │ Synchronizing with Effects              │ │
│ └─────────────────────────────────────────┘ │
│                                             │
├─────────────────────────────────────────────┤
│ Ask a question...                    [Send] │
└─────────────────────────────────────────────┘

Backend architecture

backend/
│
├── manage.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── apps/
│   ├── chat/
│   ├── documents/
│   └── rag/
│
└── requirements.txt


chat/
   → conversations
   → messages
   → chat API

documents/
   → document metadata
   → document management

rag/
   → loading
   → chunking
   → embeddings
   → retrieval
   → prompt construction
   → LLM




developer-doc-assistant/
│
├── backend/
│   ├── config/
│   ├── apps/
│   │   ├── chat/
│   │   ├── documents/
│   │   └── rag/
│   │
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── hooks/
│   │
│   └── package.json
│
├── docs/
│   └── react/
│       ├── learn/
│       └── reference/
│
├── .gitignore
├── README.md
└── docker-compose.yml       ← later
