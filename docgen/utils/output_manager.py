"""
Output management utilities for organized document storage.
"""

import logging
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple
from exceptions import DocumentGenerationError

logger = logging.getLogger(__name__)


class OutputManager:
    """Manages output directory structure and file organization."""
    
    DEFAULT_OUTPUT_DIR = "generated_documents"
    
    def __init__(self, base_dir: str = DEFAULT_OUTPUT_DIR):
        """
        Initialize output manager.
        
        Args:
            base_dir: Base directory for all outputs
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output manager initialized with base directory: {self.base_dir}")
    
    def get_session_dir(self) -> Path:
        """
        Get or create a session-specific directory with timestamp.
        
        Returns:
            Path to session directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.base_dir / f"session_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created session directory: {session_dir}")
        return session_dir
    
    def get_document_dir(self, doc_type: str, session_dir: Path = None) -> Path:
        """
        Get or create a document-type-specific directory.
        
        Args:
            doc_type: Document type (e.g., 'NDA', 'Offer_Letter')
            session_dir: Parent session directory (if None, creates new session)
            
        Returns:
            Path to document directory
        """
        if session_dir is None:
            session_dir = self.get_session_dir()
        
        doc_dir = session_dir / doc_type
        doc_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created document directory: {doc_dir}")
        return doc_dir
    
    def save_generated_document(self, source_pdf: Path, doc_type: str, 
                               session_dir: Path = None) -> Path:
        """
        Save a generated PDF document to organized structure.
        
        Args:
            source_pdf: Source PDF file path
            doc_type: Document type
            session_dir: Parent session directory
            
        Returns:
            Path to saved document
        """
        if session_dir is None:
            session_dir = self.get_session_dir()
        
        doc_dir = self.get_document_dir(doc_type, session_dir)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{doc_type}_{timestamp}.pdf"
        dest_pdf = doc_dir / filename
        
        try:
            shutil.copy2(source_pdf, dest_pdf)
            logger.info(f"Saved document: {dest_pdf}")
            return dest_pdf
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise DocumentGenerationError(f"Failed to save document: {str(e)}")
    
    def save_metadata(self, session_dir: Path, metadata: dict) -> Path:
        """
        Save session metadata as JSON.
        
        Args:
            session_dir: Session directory
            metadata: Metadata dictionary
            
        Returns:
            Path to metadata file
        """
        import json
        
        metadata_file = session_dir / "metadata.json"
        metadata['timestamp'] = datetime.now().isoformat()
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Saved metadata: {metadata_file}")
            return metadata_file
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
            raise
    
    def cleanup_old_sessions(self, keep_days: int = 7) -> int:
        """
        Remove old session directories.
        
        Args:
            keep_days: Keep sessions from last N days
            
        Returns:
            Number of directories removed
        """
        import time
        
        cutoff_time = time.time() - (keep_days * 86400)
        removed_count = 0
        
        for session_dir in self.base_dir.glob("session_*"):
            if session_dir.is_dir():
                if os.path.getmtime(session_dir) < cutoff_time:
                    try:
                        shutil.rmtree(session_dir)
                        removed_count += 1
                        logger.info(f"Removed old session: {session_dir}")
                    except Exception as e:
                        logger.error(f"Error removing session {session_dir}: {str(e)}")
        
        logger.info(f"Cleanup complete. Removed {removed_count} old sessions")
        return removed_count
    
    def list_sessions(self, limit: int = 10) -> list:
        """
        List recent sessions.
        
        Args:
            limit: Maximum number of sessions to list
            
        Returns:
            List of session paths sorted by creation time (newest first)
        """
        sessions = sorted(
            self.base_dir.glob("session_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]
        
        logger.debug(f"Found {len(sessions)} sessions")
        return sessions
    
    def get_session_summary(self, session_dir: Path) -> dict:
        """
        Get summary of a session's generated documents.
        
        Args:
            session_dir: Path to session directory
            
        Returns:
            Dictionary with session statistics
        """
        summary = {
            'path': str(session_dir),
            'created': datetime.fromtimestamp(session_dir.stat().st_mtime).isoformat(),
            'documents': {}
        }
        
        # Count documents by type
        for doc_type_dir in session_dir.glob("*"):
            if doc_type_dir.is_dir():
                pdf_count = len(list(doc_type_dir.glob("*.pdf")))
                if pdf_count > 0:
                    summary['documents'][doc_type_dir.name] = pdf_count
        
        logger.debug(f"Session summary: {summary}")
        return summary
