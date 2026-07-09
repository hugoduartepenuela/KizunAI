flowchart TD

A[User] --> B[Streamlit Web App]

B --> C[Card Scanner]
C --> D[OpenAI Vision Model]
D --> E[Structured Card Data]
E --> F[Human Verification]
F --> G[SKU Generator]
G --> H[Inventory CSV]

B --> I[KizunAI LangChain Agent]

I --> J[Inventory Search Tool]
J --> K[Inventory AI Analysis]
K --> H
K --> L[GPT-4.1-mini]

I --> M[YouTube Knowledge Tool]
M --> N[YouTube Transcript]
N --> O[Text Splitting]
O --> P[Embeddings]
P --> Q[ChromaDB Vector Store]
Q --> R[RAG Answer Generation]
R --> L

I --> S[SKU Generator Tool]
S --> G

I --> T[Conversation Memory]

I --> U[LangSmith Observability]
U --> V[Agent Traces]
U --> W[Tool Selection]
U --> X[Token / Cost / Latency Tracking]

## KizunAI Architecture

KizunAI is a multimodal AI inventory assistant built for Trading Card Game businesses and collectors.

The system combines:

- OpenAI Vision for card image understanding
- Human-in-the-loop verification before saving inventory data
- Deterministic SKU generation based on business rules
- CSV-based inventory storage for the MVP
- Natural language inventory analysis
- YouTube transcript processing with RAG
- ChromaDB as the vector database
- LangChain Agent with specialized tools
- Conversation memory for follow-up questions
- LangSmith for observability, tracing, tool selection, latency, token usage and cost monitoring

The LangChain Agent can dynamically select between three tools:

1. Inventory Search Tool  
2. YouTube Knowledge Tool  
3. SKU Generator Tool  

This allows the user to interact with the system naturally while the agent decides which internal capability should be used.
