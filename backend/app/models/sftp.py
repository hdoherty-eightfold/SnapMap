"""
SFTP Models
Pydantic models for SFTP credential management
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class SFTPCredentialInput(BaseModel):
    """Input model for creating/updating SFTP credentials"""
    name: str = Field(..., description="Friendly name for this connection")
    host: str = Field(..., description="SFTP server hostname or IP")
    port: int = Field(22, description="SFTP server port")
    username: str = Field(..., description="SFTP username")
    password: str = Field(..., description="SFTP password")
    remote_path: Optional[str] = Field("/", description="Default remote path for uploads")


class SFTPCredential(BaseModel):
    """SFTP credential with metadata"""
    id: str
    name: str
    host: str
    port: int
    username: str
    remote_path: Optional[str] = "/"
    connection_status: Optional[Literal['connected', 'failed', 'unknown']] = 'unknown'
    last_tested: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ConnectionTestResult(BaseModel):
    """Result of testing SFTP connection"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class UploadResult(BaseModel):
    """Result of SFTP file upload"""
    success: bool
    path: Optional[str] = None
    error: Optional[str] = None
