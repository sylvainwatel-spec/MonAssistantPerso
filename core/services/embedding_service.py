"""
Embedding Service for RAG Knowledge Base.
Generates vector embeddings using local Sentence-Transformers model.
"""

from typing import List

import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using local models."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern to avoid reloading the model."""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the embedding service."""
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the Sentence-Transformers model."""
        try:
            logger.info("Loading embedding model 'all-MiniLM-L6-v2'...")
            # This model is lightweight (~90MB) and multilingual
            # Produces 384-dimensional embeddings
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of 384 floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * 384  # Return zero vector for empty text
        
        try:
            # Encode returns numpy array, convert to list
            embedding = self._model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batch processing).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            # Batch encoding is more efficient
            embeddings = self._model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        return 384
