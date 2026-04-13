# Agentic-RAG

- *NOTE: This Readme is work in progress*

## Architecture

The project is built as a Decoupled Monorepo, separating the AI reasoning logic from the user interface.

- **Backend (FastAPI):** Orchestrates the Agentic RAG loop. It uses **Vertex AI (Gemini)** for reasoning and **ChromaDB** for semantic document retrieval.
- **Frontend (Next.js):** A TypeScript-based chat interface with **Tailwind CSS** and **React** and **NextJS**

## Components

### AgentStore: The Knowledge Engine

File: *database.py*

#### AgentStore Class

The **AgentStore class** serves as the central hub for document processing and semantic retrieval. It bridges the gap between raw unstructured data (PDFs, Word docs, Text) and the AI’s reasoning capabilities.

- *ingest_path*
  - Crawls directories, [loads documents](https://reference.langchain.com/python/langchain-community/document_loaders) (PDFs, Word docs, Text) and segments text into optimized chunks using [RecursiveCharacterTextSplitter](https://docs.langchain.com/oss/python/integrations/splitters).
  - Vectorized Memory: Leverages [Google Gemini Embeddings](https://reference.langchain.com/python/langchain-google-genai/embeddings/GoogleGenerativeAIEmbeddings) to convert text into high-dimensional vectors stored in a local [ChromaDB](https://reference.langchain.com/python/langchain-chroma/vectorstores/Chroma) instance.
- *search*
  - Provides a context-aware search interface that retrieves the most relevant document snippets using similarity search and returns context attributes (filename and page numbers).

### Vector DB

In this project, [ChromaDB](https://reference.langchain.com/python/langchain-chroma/vectorstores/Chroma) with langchain is utilized as the core vector store to manage document embeddings and perform semantic retrieval.

- A Vector Database stores data as high-dimensional mathematical representations called embeddings
- When a query is made, the database doesn't look for keyword matches; instead, it calculates the "distance" between the query's vector and the stored document vectors. This enables semantic search, where the system understands the meaning and context of the query, allowing it to find relevant information even if the exact words are different.
- **Advantages:**
  - *Lightweight & Embeddable:* It is designed to be easily integrated into Python applications without the overhead of a massive external server.
  - *Developer-First:* It offers a simple, intuitive API that integrates seamlessly with LangChain and Google’s Generative AI models.
  - *In-Memory & Persistent:* Chroma can run entirely in memory for fast testing or persist data to disk for long-term storage, which is ideal for this agent's document storage.
  - *Fast Similarity Search:* It utilizes optimized algorithms (like HNSW) to perform incredibly fast "Nearest Neighbor" searches, even as the number of documents grows.
- **Alternatives:**
  - Pinecone, Weaviate/Milvus, FAISS, PGVector

### Config

File: *config.py*

- *Embedding Model*
  - Currently, the embedding model *models/gemini-embedding-001* from [GoogleGenerativeAIEmbeddings](https://reference.langchain.com/python/langchain-google-genai/embeddings/GoogleGenerativeAIEmbeddings) from [langchain-google-genai](https://reference.langchain.com/python/langchain-google-genai) is used
  - The embedding model acts as a semantic translator that converts text chunks into high-dimensional vectors (long lists of numbers). It captures the contextual meaning of words rather than just their spelling, placing similar concepts close together in a mathematical "vector space." This allows the system to find relevant information even if the search query uses different synonyms than the source document.

- *Agent Model*
  - Currently, the agent model *gemini-2.5-flash* from [GenAI on VertexAI](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash) is used
  - It functions as the "reasoning engine" of the agent, processing the context retrieved from the vector database to generate human-like responses. The "Flash" variant is specifically optimized for efficiency at scale, featuring a massive context window that allows it to analyze large amounts of data (such as multiple lecture PDFs) simultaneously while maintaining rapid response times.

## Testing & Quality

A "Full-Stack" quality pipeline integrated via **GitHub Actions**

Level       | Tool                    | Purpose
------      | ------                  | -----------
Linting     | Ruff (PY) / ESLint (TS) | Code style and static analysis
Security    | Bandit / pip-audit      | Vulnerability scanning for Python dependencies
Unit        | Pytest / Vitest         | Isolated testing of Agent tools and React components
End-to-End  | Playwright              | Full flow validation (User -> API -> Agent -> UI)
