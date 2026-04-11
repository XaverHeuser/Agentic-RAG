# Agentic-RAG

- *NOTE: This Readme is work in progress*

## AgentStore: The Knowledge Engine

File: *database.py*

The AgentStore class serves as the central hub for document processing and semantic retrieval. It bridges the gap between raw unstructured data (PDFs, Word docs, Text) and the AI’s reasoning capabilities.

- *ingest_path*
  - Crawls directories, [loads documents](https://reference.langchain.com/python/langchain-community/document_loaders) (PDFs, Word docs, Text) and segments text into optimized chunks using [RecursiveCharacterTextSplitter](https://docs.langchain.com/oss/python/integrations/splitters).
  - Vectorized Memory: Leverages [Google Gemini Embeddings](https://reference.langchain.com/python/langchain-google-genai/embeddings/GoogleGenerativeAIEmbeddings) ([Google Embedding Models](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings)) to convert text into high-dimensional vectors stored in a local [ChromaDB](https://reference.langchain.com/python/langchain-chroma/vectorstores/Chroma) instance.
- *search*
  - Provides a context-aware search interface that retrieves the most relevant document snippets using similarity search and returns context attributes (filename and page numbers).
