"""
Document Ingestion Service for RAG Knowledge Base.
Handles extraction, chunking, embedding, and storage of documents.
"""

from typing import List, Dict, Callable, Optional
import os
import uuid
import logging
from pathlib import Path

# Document extraction
from pypdf import PdfReader
from docx import Document as DocxDocument

# Our services
from core.services.embedding_service import EmbeddingService
from core.services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """Service for ingesting documents into knowledge bases."""
    
    def __init__(self):
        """Initialize the ingestion service."""
        # Lazy import langchain only when needed
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
        
        # Text splitter configuration
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # ~500 characters per chunk
            chunk_overlap=50,  # 50 characters overlap
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def ingest_file(
        self,
        kb_id: str,
        file_path: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict:
        """
        Ingest a single file into a knowledge base.
        
        Args:
            kb_id: Knowledge base identifier
            file_path: Path to the file to ingest
            progress_callback: Optional callback(status_message, progress_percent)
            
        Returns:
            Dict with 'success', 'chunks_created', 'errors'
        """
        try:
            if progress_callback:
                progress_callback(f"Reading {os.path.basename(file_path)}...", 0.1)
            
            # Extract text based on file type
            text = self._extract_text(file_path)
            
            if not text or not text.strip():
                logger.warning(f"No text extracted from {file_path}")
                return {
                    "success": False,
                    "chunks_created": 0,
                    "errors": [f"No text content in {file_path}"]
                }
            
            if progress_callback:
                progress_callback(f"Chunking {os.path.basename(file_path)}...", 0.3)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(text)
            
            if progress_callback:
                progress_callback(f"Generating embeddings for {len(chunks)} chunks...", 0.5)
            
            # Generate embeddings
            embeddings = self.embedding_service.embed_texts(chunks)
            
            if progress_callback:
                progress_callback(f"Storing {len(chunks)} chunks...", 0.8)
            
            # Prepare documents for storage
            documents = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_id = str(uuid.uuid4())
                documents.append({
                    "id": doc_id,
                    "text": chunk,
                    "metadata": {
                        "source_file": os.path.basename(file_path),
                        "file_path": file_path,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                })
            
            # Store in vector database
            self.vector_store.add_documents(kb_id, documents, embeddings)
            
            if progress_callback:
                progress_callback(f"Completed {os.path.basename(file_path)}", 1.0)
            
            logger.info(f"Successfully ingested {file_path}: {len(chunks)} chunks")
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "errors": []
            }
            
        except Exception as e:
            error_msg = f"Error ingesting {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "chunks_created": 0,
                "errors": [error_msg]
            }
    
    def ingest_folder(
        self,
        kb_id: str,
        folder_path: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict:
        """
        Ingest all supported files in a folder recursively.
        
        Args:
            kb_id: Knowledge base identifier
            folder_path: Path to the folder
            progress_callback: Optional callback(status_message, progress_percent)
            
        Returns:
            Dict with 'success', 'files_processed', 'chunks_created', 'errors'
        """
        supported_extensions = {'.pdf', '.docx', '.txt'}
        
        # Find all supported files
        files_to_process = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if Path(file).suffix.lower() in supported_extensions:
                    files_to_process.append(os.path.join(root, file))
        
        if not files_to_process:
            return {
                "success": False,
                "files_processed": 0,
                "chunks_created": 0,
                "errors": ["No supported files found in folder"]
            }
        
        logger.info(f"Found {len(files_to_process)} files to process in {folder_path}")
        
        total_chunks = 0
        errors = []
        
        for i, file_path in enumerate(files_to_process):
            # Update progress
            file_progress = i / len(files_to_process)
            if progress_callback:
                progress_callback(
                    f"Processing file {i+1}/{len(files_to_process)}: {os.path.basename(file_path)}",
                    file_progress
                )
            
            # Ingest file
            result = self.ingest_file(kb_id, file_path)
            
            if result["success"]:
                total_chunks += result["chunks_created"]
            else:
                errors.extend(result["errors"])
        
        if progress_callback:
            progress_callback("Folder ingestion complete", 1.0)
        
        return {
            "success": len(errors) == 0,
            "files_processed": len(files_to_process),
            "chunks_created": total_chunks,
            "errors": errors
        }
    
    def _extract_text(self, file_path: str) -> str:
        """
        Extract text from a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text
        """
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext == '.pdf':
                return self._extract_from_pdf(file_path)
            elif ext == '.docx':
                return self._extract_from_docx(file_path)
            elif ext == '.txt':
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        reader = PdfReader(file_path)
        text_parts = []
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = DocxDocument(file_path)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n\n".join(text_parts)
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
