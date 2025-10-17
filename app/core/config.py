import os

# Qdrant Configuration
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
COLLECTION_NAME = "my_collection"

# Ollama Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Embedding Model Configuration
# Using a model from Ollama. `nomic-embed-text` is a good default for embedding tasks.
# If you change the model, make sure to update EMBEDDING_DIMENSION accordingly.
# Common dimensions: nomic-embed-text (768), mistral (4096), llama2 (4096)
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_DIMENSION", 768))
CHAT_MODEL = os.environ.get("CHAT_MODEL", "llama3")  # Example chat model
