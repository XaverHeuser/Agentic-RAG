# Agentic-RAG

- *NOTE: This Readme is work in progress*

## AgentStore: The Knowledge Engine

File: *database.py*

The AgentStore class serves as the central hub for document processing and semantic retrieval. It bridges the gap between raw unstructured data (PDFs, Word docs, Text) and the AI’s reasoning capabilities.

- *ingest_path*
  - Crawls directories, parses multi-format documents (PDFs, Word docs, Text) and segments text into optimized chunks using RecursiveCharacterTextSplitter.
  - Vectorized Memory: Leverages Google Gemini Embeddings to convert text into high-dimensional vectors stored in a local ChromaDB instance.
- *search*
  - Provides a context-aware search interface that retrieves the most relevant document snippets using similarity search and returns context attributes (filename and page numbers).

