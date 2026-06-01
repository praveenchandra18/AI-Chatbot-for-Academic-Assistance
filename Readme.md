# AI Chatbot for Academic Assistance

An AI-powered academic assistant built with FastAPI, LangChain, Ollama, and ChromaDB. The application enables users to interact with academic documents through a conversational interface powered by Retrieval-Augmented Generation (RAG).

Unlike a basic chatbot, the system implements a complete document intelligence pipeline including PDF ingestion, hybrid retrieval, query reformulation, retrieval validation, reranking, conversation memory, and local LLM inference.

---

## Features

- Context-aware question answering from academic PDFs
- Hybrid retrieval using semantic and keyword search
- Query reformulation using conversation history
- Retrieval relevance validation before answer generation
- Cross-encoder reranking for improved context selection
- Local LLM inference using Ollama
- Persistent chat history and conversation memory
- JWT-based authentication and user management
- Streaming responses for real-time interaction
- Source-aware answers grounded in document content

---

## Tech Stack

| Category | Technology |
|-----------|------------|
| Backend | FastAPI, Python |
| Frontend | HTML, CSS, Jinja2 |
| Database | SQLite, SQLModel |
| Authentication | JWT, HTTP-only Cookies |
| LLM Framework | LangChain |
| LLM Runtime | Ollama |
| Language Model | phi4-mini |
| Embeddings | nomic-embed-text |
| Vector Database | ChromaDB |
| Retrieval | BM25, Vector Search, Ensemble Retrieval |
| Reranking | BAAI/bge-reranker-base |
| PDF Processing | PyMuPDF |

---

## Architecture

```text
User
 │
 ▼
FastAPI Application
 │
 ├── Authentication & Chat Management
 │       │
 │       ▼
 │   SQLite + SQLModel
 │
 ▼
User Question
 │
 ▼
Question Rewriter
 │
 ▼
Hybrid Retrieval
 ├── Chroma Vector Search
 ├── BM25 Search
 └── Ensemble Retrieval
 │
 ▼
Cross-Encoder Reranker
 │
 ▼
Retrieval Relevance Check
 │
 ├── Relevant Context → Generate Answer
 └── Irrelevant Context → Skip Generation
 │
 ▼
Ollama (phi4-mini)
 │
 ▼
Streaming Response
```

---

## How It Works

### Document Processing

PDFs are extracted using PyMuPDF and converted into page-level documents while preserving source metadata such as filename and page number.

The content is split into overlapping chunks using LangChain's `RecursiveCharacterTextSplitter`.

To ensure idempotent ingestion, each chunk is assigned a deterministic SHA-256 hash generated from:

- Chunk content
- Source filename
- Page metadata

This guarantees that the same document can be reprocessed without creating duplicate vector entries in the database.

### Embedding and Storage

Chunks are embedded using Ollama embeddings (`nomic-embed-text`) and stored in a persistent ChromaDB collection for semantic retrieval.

### Conversational Query Reformulation

User questions are not sent directly to the retrieval pipeline.

The system first uses the language model to rewrite the user's query based on recent conversation history, transforming follow-up questions into standalone searchable queries.

### Hybrid Retrieval Pipeline

The retrieval layer combines multiple search strategies:

1. Dense vector similarity search through ChromaDB
2. BM25 keyword retrieval
3. Ensemble retrieval to merge semantic and lexical results
4. Cross-encoder reranking to improve final context quality

### Retrieval Validation

Before generating a response, the system evaluates the relevance score of the retrieved context.

If the retrieved documents fail to meet a predefined relevance threshold:

- The context is considered unreliable
- The generation step is skipped
- The model is prevented from answering based on weak or unrelated information

This acts as a guardrail against hallucinations and irrelevant responses, improving answer reliability.

### Response Generation

Once relevant context is confirmed, the retrieved chunks, chat history, and user query are assembled into a prompt and sent to a locally running Ollama model.

Responses are streamed back to the client in real time, providing a responsive chat experience.

---

## Key Engineering Highlights

### Retrieval-Augmented Generation (RAG)

- Context-grounded responses
- Reduced hallucinations
- Source-aware answer generation
- Academic document question answering

### Advanced Retrieval Strategy

- Query rewriting using conversation history
- Hybrid semantic and keyword retrieval
- Ensemble ranking
- Cross-encoder reranking
- Retrieval relevance validation

### Reliable Document Ingestion

- Metadata-preserving PDF extraction
- Deterministic chunk ID generation
- SHA-256 hash-based deduplication
- Idempotent ingestion pipeline

### Local AI Infrastructure

- Fully local LLM inference
- No external API dependencies
- Lower operational costs
- Improved privacy and data ownership

### Conversation Management

- JWT authentication
- Persistent chat sessions
- Conversation memory
- Multi-chat support

---

## Installation

```bash
git clone <repository-url>
cd <repository-name>

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Install Ollama and pull the required models:

```bash
ollama pull phi4-mini
ollama pull nomic-embed-text
```

---
