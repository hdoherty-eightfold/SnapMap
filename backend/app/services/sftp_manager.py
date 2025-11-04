"""
SFTP Manager Service
Manages SFTP credentials and operations
"""

import os
import uuid
import json
import base64
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import tempfile


class SFTPManager:
    """
    Manages SFTP credentials and connections

    Credentials are persisted to disk with basic password encoding.
    Note: For production, use proper encryption (e.g., Fernet, AWS KMS, etc.)
    """

    def __init__(self):
        self.credentials_dir = Path(tempfile.gettempdir()) / "snapmap_sftp"
        self.credentials_dir.mkdir(exist_ok=True)
        self.credentials_file = self.credentials_dir / "credentials.json"
        self._credentials: Dict[str, Dict] = {}
        self._load_credentials()

    def _encode_password(self, password: str) -> str:
        """Basic password encoding (base64). Use proper encryption in production."""
        return base64.b64encode(password.encode()).decode()

    def _decode_password(self, encoded: str) -> str:
        """Decode password from base64"""
        return base64.b64decode(encoded.encode()).decode()

    def _load_credentials(self):
        """Load credentials from disk"""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                    # Convert timestamps back to datetime and decode passwords
                    for cred_id, cred in data.items():
                        cred['created_at'] = datetime.fromisoformat(cred['created_at'])
                        cred['updated_at'] = datetime.fromisoformat(cred['updated_at'])
                        if cred.get('last_tested'):
                            cred['last_tested'] = datetime.fromisoformat(cred['last_tested'])
                        # Decode password
                        if 'password' in cred:
                            cred['password'] = self._decode_password(cred['password'])
                    self._credentials = data
                    print(f"[SFTPManager] Loaded {len(self._credentials)} credentials from disk")
            except Exception as e:
                print(f"[SFTPManager] Error loading credentials: {e}")
                self._credentials = {}
        else:
            print(f"[SFTPManager] No existing credentials file")

    def _save_credentials(self):
        """Save credentials to disk"""
        try:
            # Convert datetime to ISO format and encode passwords for JSON
            data = {}
            for cred_id, cred in self._credentials.items():
                data[cred_id] = {
                    **cred,
                    'created_at': cred['created_at'].isoformat(),
                    'updated_at': cred['updated_at'].isoformat(),
                    'last_tested': cred['last_tested'].isoformat() if cred.get('last_tested') else None,
                    'password': self._encode_password(cred['password'])
                }
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[SFTPManager] Saved {len(self._credentials)} credentials to disk")
        except Exception as e:
            print(f"[SFTPManager] Error saving credentials: {e}")

    def add_credential(
        self,
        name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        remote_path: str = "/"
    ) -> Dict:
        """Add new SFTP credential"""
        credential_id = str(uuid.uuid4())
        now = datetime.utcnow()

        credential = {
            "id": credential_id,
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "password": password,  # In production: encrypt this!
            "remote_path": remote_path,
            "connection_status": "unknown",
            "last_tested": None,
            "created_at": now,
            "updated_at": now
        }

        self._credentials[credential_id] = credential
        self._save_credentials()
        return self._sanitize_credential(credential)

    def get_credential(self, credential_id: str) -> Optional[Dict]:
        """Get credential by ID"""
        credential = self._credentials.get(credential_id)
        if credential:
            return credential.copy()  # Return copy with password
        return None

    def get_all_credentials(self) -> List[Dict]:
        """Get all credentials (without passwords)"""
        return [self._sanitize_credential(cred) for cred in self._credentials.values()]

    def update_credential(
        self,
        credential_id: str,
        name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remote_path: Optional[str] = None
    ) -> Optional[Dict]:
        """Update existing credential"""
        credential = self._credentials.get(credential_id)
        if not credential:
            return None

        if name is not None:
            credential["name"] = name
        if host is not None:
            credential["host"] = host
        if port is not None:
            credential["port"] = port
        if username is not None:
            credential["username"] = username
        if password is not None and password:  # Only update if provided
            credential["password"] = password
        if remote_path is not None:
            credential["remote_path"] = remote_path

        credential["updated_at"] = datetime.utcnow()
        self._save_credentials()
        return self._sanitize_credential(credential)

    def delete_credential(self, credential_id: str) -> bool:
        """Delete credential"""
        if credential_id in self._credentials:
            del self._credentials[credential_id]
            self._save_credentials()
            return True
        return False

    def test_connection(self, credential_id: str) -> Dict:
        """Test SFTP connection"""
        credential = self._credentials.get(credential_id)
        if not credential:
            return {
                "success": False,
                "error": "Credential not found"
            }

        try:
            # Try to import paramiko
            import paramiko

            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect
            ssh.connect(
                hostname=credential["host"],
                port=credential["port"],
                username=credential["username"],
                password=credential["password"],
                timeout=10
            )

            # Open SFTP session
            sftp = ssh.open_sftp()

            # Test by listing directory
            remote_path = credential.get("remote_path", "/")
            try:
                sftp.listdir(remote_path)
            except:
                # Path might not exist, try root
                sftp.listdir("/")

            sftp.close()
            ssh.close()

            # Update connection status
            credential["connection_status"] = "connected"
            credential["last_tested"] = datetime.utcnow()
            self._save_credentials()

            return {
                "success": True,
                "message": f"Successfully connected to {credential['host']}"
            }

        except ImportError:
            return {
                "success": False,
                "error": "paramiko library not installed. Install with: pip install paramiko"
            }
        except Exception as e:
            # Update connection status
            credential["connection_status"] = "failed"
            credential["last_tested"] = datetime.utcnow()
            self._save_credentials()

            return {
                "success": False,
                "error": str(e)
            }

    def upload_file(
        self,
        credential_id: str,
        local_path: str,
        remote_filename: Optional[str] = None,
        remote_path: Optional[str] = None
    ) -> Dict:
        """Upload file to SFTP server"""
        credential = self._credentials.get(credential_id)
        if not credential:
            return {
                "success": False,
                "error": "Credential not found"
            }

        if not os.path.exists(local_path):
            return {
                "success": False,
                "error": f"Local file not found: {local_path}"
            }

        try:
            import paramiko

            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect
            ssh.connect(
                hostname=credential["host"],
                port=credential["port"],
                username=credential["username"],
                password=credential["password"],
                timeout=10
            )

            # Open SFTP session
            sftp = ssh.open_sftp()

            # Determine remote path
            if remote_path is None:
                remote_path = credential.get("remote_path", "/")

            # Determine remote filename
            if remote_filename is None:
                remote_filename = Path(local_path).name

            # Construct full remote path
            if remote_path.endswith("/"):
                full_remote_path = f"{remote_path}{remote_filename}"
            else:
                full_remote_path = f"{remote_path}/{remote_filename}"

            # Upload file
            sftp.put(local_path, full_remote_path)

            sftp.close()
            ssh.close()

            return {
                "success": True,
                "path": full_remote_path
            }

        except ImportError:
            return {
                "success": False,
                "error": "paramiko library not installed. Install with: pip install paramiko"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _sanitize_credential(self, credential: Dict) -> Dict:
        """Remove password from credential dict"""
        sanitized = credential.copy()
        sanitized.pop("password", None)
        return sanitized


# Global instance
_sftp_manager = None


def get_sftp_manager() -> SFTPManager:
    """Get global SFTP manager instance"""
    global _sftp_manager
    if _sftp_manager is None:
        _sftp_manager = SFTPManager()
    return _sftp_manager
