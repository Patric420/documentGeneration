"""
Batch processing module for handling multiple document generation requests.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import concurrent.futures
from threading import Lock

from app import generate_document
from utils.output_manager import OutputManager
from exceptions import DocumentGenerationError

logger = logging.getLogger(__name__)


@dataclass
class BatchJob:
    """Represents a single batch job."""
    job_id: str
    input_path: str
    fields: Dict[str, str]
    status: str = "pending"  # pending, processing, completed, failed
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    doc_type: Optional[str] = None
    created_at: str = ""
    completed_at: Optional[str] = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'BatchJob':
        """Create from dictionary."""
        return BatchJob(**data)


class BatchProcessor:
    """Processes multiple document generation requests."""
    
    def __init__(self, max_workers: int = 4, output_manager: Optional[OutputManager] = None):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Maximum number of concurrent workers
            output_manager: OutputManager instance (creates new if None)
        """
        self.max_workers = max_workers
        self.output_manager = output_manager or OutputManager()
        self.jobs: Dict[str, BatchJob] = {}
        self.jobs_lock = Lock()
        self.session_dir = self.output_manager.get_session_dir()
        logger.info(f"Batch processor initialized with {max_workers} workers")
    
    def create_job(self, job_id: str, input_path: str, fields: Dict[str, str]) -> BatchJob:
        """
        Create a batch job.
        
        Args:
            job_id: Unique job identifier
            input_path: Path to input document
            fields: Field values for generation
            
        Returns:
            BatchJob instance
        """
        job = BatchJob(job_id=job_id, input_path=input_path, fields=fields)
        with self.jobs_lock:
            self.jobs[job_id] = job
        logger.info(f"Created batch job: {job_id}")
        return job
    
    def _process_job(self, job: BatchJob, progress_callback: Optional[Callable] = None) -> BatchJob:
        """
        Process a single batch job.
        
        Args:
            job: Job to process
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Updated job with result
        """
        logger.info(f"Processing job: {job.job_id}")
        job.status = "processing"
        
        if progress_callback:
            progress_callback(job)
        
        try:
            # Generate document
            doc_type, output_pdf = generate_document(job.input_path, job.fields)
            
            # Save to organized structure
            saved_path = self.output_manager.save_generated_document(
                Path(output_pdf), doc_type, self.session_dir
            )
            
            job.status = "completed"
            job.output_path = str(saved_path)
            job.doc_type = doc_type
            job.completed_at = datetime.now().isoformat()
            
            logger.info(f"Job completed successfully: {job.job_id}")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now().isoformat()
            logger.error(f"Job failed: {job.job_id} - {str(e)}", exc_info=True)
        
        if progress_callback:
            progress_callback(job)
        
        return job
    
    def process_batch(self, jobs: List[Tuple[str, str, Dict]], 
                     progress_callback: Optional[Callable] = None,
                     timeout: Optional[int] = None) -> Dict[str, BatchJob]:
        """
        Process multiple jobs concurrently.
        
        Args:
            jobs: List of (job_id, input_path, fields) tuples
            progress_callback: Optional callback for progress updates
            timeout: Timeout in seconds for each job
            
        Returns:
            Dictionary of job_id -> BatchJob
        """
        logger.info(f"Starting batch processing of {len(jobs)} jobs")
        
        # Create job objects
        batch_jobs = {}
        for job_id, input_path, fields in jobs:
            job = self.create_job(job_id, input_path, fields)
            batch_jobs[job_id] = job
        
        # Process in parallel
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_job, job, progress_callback): job_id
                for job_id, job in batch_jobs.items()
            }
            
            for future in concurrent.futures.as_completed(futures, timeout=timeout):
                job_id = futures[future]
                try:
                    completed_job = future.result()
                    results[job_id] = completed_job
                    with self.jobs_lock:
                        self.jobs[job_id] = completed_job
                except Exception as e:
                    logger.error(f"Error processing job {job_id}: {str(e)}")
                    results[job_id] = batch_jobs[job_id]
                    batch_jobs[job_id].status = "failed"
                    batch_jobs[job_id].error_message = str(e)
        
        logger.info(f"Batch processing completed. Results saved in {self.session_dir}")
        return results
    
    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get status of a job."""
        with self.jobs_lock:
            return self.jobs.get(job_id)
    
    def get_batch_summary(self) -> dict:
        """
        Get summary of all jobs in current session.
        
        Returns:
            Summary with counts by status
        """
        with self.jobs_lock:
            summary = {
                'total': len(self.jobs),
                'completed': sum(1 for j in self.jobs.values() if j.status == 'completed'),
                'failed': sum(1 for j in self.jobs.values() if j.status == 'failed'),
                'processing': sum(1 for j in self.jobs.values() if j.status == 'processing'),
                'pending': sum(1 for j in self.jobs.values() if j.status == 'pending'),
                'by_type': {}
            }
            
            for job in self.jobs.values():
                if job.doc_type:
                    summary['by_type'][job.doc_type] = summary['by_type'].get(job.doc_type, 0) + 1
        
        return summary
    
    def save_batch_report(self, output_file: Optional[str] = None) -> Path:
        """
        Save batch processing report to JSON file.
        
        Args:
            output_file: Output file path (default: session_dir/batch_report.json)
            
        Returns:
            Path to report file
        """
        if output_file is None:
            output_file = self.session_dir / "batch_report.json"
        else:
            output_file = Path(output_file)
        
        with self.jobs_lock:
            report = {
                'session_dir': str(self.session_dir),
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_batch_summary(),
                'jobs': [job.to_dict() for job in self.jobs.values()]
            }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Batch report saved: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving batch report: {str(e)}")
            raise
    
    def load_batch_from_json(self, json_file: str) -> List[Tuple[str, str, Dict]]:
        """
        Load batch jobs from JSON file.
        
        Expected format:
        {
            "jobs": [
                {
                    "job_id": "job1",
                    "input_path": "path/to/document.pdf",
                    "fields": {"Name": "John", "Date": "2024-02-16"}
                },
                ...
            ]
        }
        
        Args:
            json_file: Path to JSON file
            
        Returns:
            List of (job_id, input_path, fields) tuples
        """
        logger.info(f"Loading batch jobs from: {json_file}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            jobs = []
            for job_data in data.get('jobs', []):
                jobs.append((
                    job_data['job_id'],
                    job_data['input_path'],
                    job_data['fields']
                ))
            
            logger.info(f"Loaded {len(jobs)} jobs from batch file")
            return jobs
        except Exception as e:
            logger.error(f"Error loading batch file: {str(e)}")
            raise


def create_batch_file(output_path: str, jobs: List[Dict]) -> Path:
    """
    Create a batch input JSON file.
    
    Args:
        output_path: Path to output file
        jobs: List of job dictionaries with 'job_id', 'input_path', 'fields'
        
    Returns:
        Path to created file
    """
    batch_data = {'jobs': jobs}
    
    output_file = Path(output_path)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, indent=2)
    
    logger.info(f"Batch file created: {output_file}")
    return output_file
