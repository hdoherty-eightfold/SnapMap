"""
File Storage Service
Temporarily stores uploaded files for later retrieval during export
"""

import uuid
import tempfile
import json
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
import os


class FileStorage:
    """
    Temporary file storage for uploaded data files

    Stores uploaded files temporarily so the full dataset
    can be retrieved during export without keeping everything in memory.

    Auto-cleanup removes files older than 1 hour.
    """

    def __init__(self):
        self.storage_dir = Path(tempfile.gettempdir()) / "snapmap_uploads"
        self.storage_dir.mkdir(exist_ok=True)
        self.metadata_file = self.storage_dir / "metadata.json"
        self._metadata: Dict[str, dict] = {}
        self._load_metadata()

    def _load_metadata(self):
        """Load metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    # Convert stored_at back to datetime
                    for file_id, meta in data.items():
                        meta['stored_at'] = datetime.fromisoformat(meta['stored_at'])
                    self._metadata = data
                    print(f"[FileStorage] Loaded {len(self._metadata)} files from metadata")
            except Exception as e:
                print(f"[FileStorage] Error loading metadata: {e}")
                self._metadata = {}
        else:
            print(f"[FileStorage] No existing metadata file")

    def _save_metadata(self):
        """Save metadata to disk"""
        try:
            # Convert datetime to ISO format for JSON
            data = {}
            for file_id, meta in self._metadata.items():
                data[file_id] = {
                    **meta,
                    'stored_at': meta['stored_at'].isoformat()
                }
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[FileStorage] Saved metadata for {len(self._metadata)} files")
        except Exception as e:
            print(f"[FileStorage] Error saving metadata: {e}")

    def store_dataframe(self, df: pd.DataFrame, original_filename: str) -> str:
        """
        Store a DataFrame temporarily and return a unique file ID

        Args:
            df: pandas DataFrame to store
            original_filename: Original uploaded filename

        Returns:
            Unique file ID for later retrieval
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())

        # Save to parquet for efficient storage
        file_path = self.storage_dir / f"{file_id}.parquet"
        df.to_parquet(file_path, index=False)

        # Store metadata
        self._metadata[file_id] = {
            "original_filename": original_filename,
            "stored_at": datetime.now(),
            "file_path": str(file_path),
            "row_count": len(df),
            "column_count": len(df.columns)
        }

        # Save metadata to disk
        self._save_metadata()

        # Cleanup old files
        self._cleanup_old_files()

        return file_id

    def retrieve_dataframe(self, file_id: str) -> Optional[pd.DataFrame]:
        """
        Retrieve a stored DataFrame by file ID

        Args:
            file_id: Unique file identifier

        Returns:
            pandas DataFrame or None if not found
        """
        if file_id not in self._metadata:
            return None

        metadata = self._metadata[file_id]
        file_path = Path(metadata["file_path"])

        if not file_path.exists():
            # File was deleted, remove metadata
            del self._metadata[file_id]
            return None

        try:
            df = pd.read_parquet(file_path)
            return df
        except Exception as e:
            print(f"Error reading stored file {file_id}: {e}")
            return None

    def get_dataframe(self, file_id: str) -> Optional[pd.DataFrame]:
        """Alias for retrieve_dataframe for backward compatibility"""
        return self.retrieve_dataframe(file_id)

    def get_metadata(self, file_id: str) -> Optional[dict]:
        """Get metadata for a stored file"""
        return self._metadata.get(file_id)

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a stored file

        Args:
            file_id: Unique file identifier

        Returns:
            True if deleted, False if not found
        """
        if file_id not in self._metadata:
            return False

        metadata = self._metadata[file_id]
        file_path = Path(metadata["file_path"])

        # Delete file
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Error deleting file {file_id}: {e}")

        # Remove metadata
        del self._metadata[file_id]
        self._save_metadata()
        return True

    def _cleanup_old_files(self, max_age_hours: int = 1):
        """
        Remove files older than max_age_hours

        Args:
            max_age_hours: Maximum age in hours (default 1 hour)
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_ids = []

        for file_id, metadata in self._metadata.items():
            if metadata["stored_at"] < cutoff_time:
                expired_ids.append(file_id)

        for file_id in expired_ids:
            self.delete_file(file_id)
            print(f"[CLEANUP] Removed expired file: {file_id}")

    def get_stats(self) -> dict:
        """Get storage statistics"""
        total_files = len(self._metadata)
        total_size = 0

        for metadata in self._metadata.values():
            file_path = Path(metadata["file_path"])
            if file_path.exists():
                total_size += file_path.stat().st_size

        return {
            "total_files": total_files,
            "total_size_mb": total_size / (1024 * 1024),
            "storage_dir": str(self.storage_dir)
        }


# Singleton instance
_file_storage = None


def get_file_storage() -> FileStorage:
    """Get singleton FileStorage instance"""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorage()
    return _file_storage
