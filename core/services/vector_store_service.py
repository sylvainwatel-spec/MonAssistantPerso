"""
Vector Store Service for RAG Knowledge Base.
Manages ChromaDB collections for document storage and retrieval.
"""

from typing import List, Dict, Optional, Any
import uuid
import os
import logging
from utils.resource_handler import get_writable_path

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector databases using ChromaDB."""
    
    def __init__(self):
        """Initialize the vector store service."""
        # Lazy import chromadb only when needed
        import chromadb
        from chromadb.config import Settings
        
        # Base directory for all vector databases
        self.vector_db_root = get_writable_path("vector_databases")
        os.makedirs(self.vector_db_root, exist_ok=True)
        
        # ChromaDB client (persistent)
        # Use PersistentClient to ensure data is saved to disk
        self.client = chromadb.PersistentClient(
            path=self.vector_db_root,
            settings=Settings(anonymized_telemetry=False)
        )
        
        logger.info(f"VectorStoreService initialized with root: {self.vector_db_root}")
    
    def create_knowledge_base(self, kb_id: str, name: str, description: str) -> None:
        """
        Create a new knowledge base collection.
        
        Args:
            kb_id: Unique identifier for the knowledge base
            name: Human-readable name
            description: Description of the knowledge base
        """
        try:
            # Create collection with metadata
            collection = self.client.create_collection(
                name=f"kb_{kb_id}",
                metadata={
                    "name": name,
                    "description": description,
                    "kb_id": kb_id
                }
            )
            logger.info(f"Created knowledge base collection: {name} (ID: {kb_id})")
        except Exception as e:
            logger.error(f"Error creating knowledge base: {e}")
            raise
    
    def add_documents(
        self,
        kb_id: str,
        documents: List[Dict],
        embeddings: List[List[float]]
    ) -> None:
        """
        Add documents to a knowledge base.
        
        Args:
            kb_id: Knowledge base identifier
            documents: List of document dicts with 'id', 'text', and 'metadata'
            embeddings: List of embedding vectors corresponding to documents
        """
        try:
            collection = self.client.get_collection(name=f"kb_{kb_id}")
            
            # Prepare data for ChromaDB
            ids = [doc["id"] for doc in documents]
            texts = [doc["text"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            # Add to collection
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to KB {kb_id}")
        except Exception as e:
            logger.error(f"Error adding documents to KB {kb_id}: {e}")
            raise
    
    def search(
        self,
        kb_id: str,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for similar documents in a knowledge base.
        
        Args:
            kb_id: Knowledge base identifier
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'id', 'text', 'metadata', and 'distance'
        """
        try:
            collection = self.client.get_collection(name=f"kb_{kb_id}")
            
            # Query the collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results and results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query in KB {kb_id}")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching KB {kb_id}: {e}")
            raise
    
    def delete_knowledge_base(self, kb_id: str) -> None:
        """
        Delete a knowledge base collection.
        
        Args:
            kb_id: Knowledge base identifier
        """
        try:
            self.client.delete_collection(name=f"kb_{kb_id}")
            logger.info(f"Deleted knowledge base: {kb_id}")
        except Exception as e:
            if "does not exist" in str(e):
                logger.warning(f"KB {kb_id} not found in vector store during deletion. It may have been already deleted.")
            else:
                logger.error(f"Error deleting KB {kb_id}: {e}")
                raise

    def cleanup_orphan_files(self) -> Dict[str, Any]:
        """
        Identify and remove orphan directories in vector_databases.
        Orphans are directories that do not correspond to any active collection segment.
        
        Returns:
            Dict with 'deleted' (list of folder names) and 'failed' (list of folder names)
        """
        import shutil
        import sqlite3
        import gc
        
        results = {
            "deleted": [],
            "failed": []
        }
        
        db_path = os.path.join(self.vector_db_root, "chroma.sqlite3")
        if not os.path.exists(db_path):
            return results
            
        try:
            # Force GC to help release locks if possible
            gc.collect()
            
            # Connect to Chroma's SQLite DB to find active segments
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all segment IDs (these correspond to folder names)
            cursor.execute("SELECT id FROM segments")
            active_segments = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            # List all directories to delete
            for item in os.listdir(self.vector_db_root):
                item_path = os.path.join(self.vector_db_root, item)
                
                # Check if it's a directory and looks like a UUID (length 36)
                if os.path.isdir(item_path) and len(item) == 36:
                    if item not in active_segments:
                        try:
                            shutil.rmtree(item_path)
                            logger.info(f"Deleted orphan directory: {item}")
                            results["deleted"].append(item)
                        except Exception as e:
                            logger.warning(f"Failed to delete orphan directory {item}: {e}")
                            results["failed"].append(item)
                            
        except Exception as e:
            logger.error(f"Error during orphan cleanup: {e}")
            
        return results
    
    def get_stats(self, kb_id: str) -> Dict:
        """
        Get statistics for a knowledge base.
        
        Args:
            kb_id: Knowledge base identifier
            
        Returns:
            Dict with 'document_count' and 'chunk_count'
        """
        try:
            collection = self.client.get_collection(name=f"kb_{kb_id}")
            count = collection.count()
            
            return {
                "chunk_count": count,
                "document_count": count  # Will be updated by ingestion service
            }
        except Exception as e:
            logger.error(f"Error getting stats for KB {kb_id}: {e}")
            return {"chunk_count": 0, "document_count": 0}
    
    def knowledge_base_exists(self, kb_id: str) -> bool:
        """
        Check if a knowledge base exists.
        
        Args:
            kb_id: Knowledge base identifier
            
        Returns:
            True if exists, False otherwise
        """
        try:
            self.client.get_collection(name=f"kb_{kb_id}")
            return True
        except:
            return False
