# Agentic-RAG

- *NOTE: This Readme is work in progress*

## AgentStore: The Knowledge Engine

File: *database.py*

The **AgentStore class** serves as the central hub for document processing and semantic retrieval. It bridges the gap between raw unstructured data (PDFs, Word docs, Text) and the AI’s reasoning capabilities.

- *ingest_path*
  - Crawls directories, [loads documents](https://reference.langchain.com/python/langchain-community/document_loaders) (PDFs, Word docs, Text) and segments text into optimized chunks using [RecursiveCharacterTextSplitter](https://docs.langchain.com/oss/python/integrations/splitters).
  - Vectorized Memory: Leverages [Google Gemini Embeddings](https://reference.langchain.com/python/langchain-google-genai/embeddings/GoogleGenerativeAIEmbeddings) to convert text into high-dimensional vectors stored in a local [ChromaDB](https://reference.langchain.com/python/langchain-chroma/vectorstores/Chroma) instance.
- *search*
  - Provides a context-aware search interface that retrieves the most relevant document snippets using similarity search and returns context attributes (filename and page numbers).

## Config

File: *config.py*

- *Embedding Model*
  - Currently, the embedding model *models/gemini-embedding-001* from [GoogleGenerativeAIEmbeddings](https://reference.langchain.com/python/langchain-google-genai/embeddings/GoogleGenerativeAIEmbeddings) from [langchain-google-genai](https://reference.langchain.com/python/langchain-google-genai) is used
  - The embedding model acts as a semantic translator that converts text chunks into high-dimensional vectors (long lists of numbers). It captures the contextual meaning of words rather than just their spelling, placing similar concepts close together in a mathematical "vector space." This allows the system to find relevant information even if the search query uses different synonyms than the source document.
