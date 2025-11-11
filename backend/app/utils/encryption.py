"""
Encryption utilities for secure credential storage

Uses Fernet symmetric encryption (AES-128 in CBC mode with HMAC-SHA256)
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os


class CredentialEncryption:
    """
    Secure credential encryption using Fernet

    Key derivation using PBKDF2 from a master password.
    For production: Store master key in environment variable or secrets manager
    """

    def __init__(self, master_key: str = None):
        """
        Initialize encryption with master key

        Args:
            master_key: Master encryption key (base64-encoded Fernet key)
                       If None, generates a new key (NOT recommended for production)
        """
        if master_key:
            self.key = master_key.encode()
        else:
            # Generate a new key (for development only)
            # In production, load from environment variable or secrets manager
            self.key = Fernet.generate_key()

        self.fernet = Fernet(self.key)

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key

        Returns:
            Base64-encoded Fernet key (store this securely!)
        """
        return Fernet.generate_key().decode()

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
        """
        Derive a Fernet key from a password using PBKDF2

        Args:
            password: Master password
            salt: Optional salt (generated if not provided)

        Returns:
            (base64_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP recommendation (2023)
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        return key.decode(), salt

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        encrypted = self.fernet.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt a string

        Args:
            encrypted: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string

        Raises:
            InvalidToken: If decryption fails (wrong key or tampered data)
        """
        decrypted = self.fernet.decrypt(encrypted.encode())
        return decrypted.decode()

    def encrypt_dict(self, data: dict, sensitive_keys: list[str]) -> dict:
        """
        Encrypt specific keys in a dictionary

        Args:
            data: Dictionary to encrypt
            sensitive_keys: List of keys to encrypt

        Returns:
            Dictionary with encrypted values
        """
        result = data.copy()
        for key in sensitive_keys:
            if key in result and result[key]:
                result[key] = self.encrypt(str(result[key]))
        return result

    def decrypt_dict(self, data: dict, sensitive_keys: list[str]) -> dict:
        """
        Decrypt specific keys in a dictionary

        Args:
            data: Dictionary with encrypted values
            sensitive_keys: List of keys to decrypt

        Returns:
            Dictionary with decrypted values
        """
        result = data.copy()
        for key in sensitive_keys:
            if key in result and result[key]:
                try:
                    result[key] = self.decrypt(result[key])
                except Exception as e:
                    # If decryption fails, might be old base64 encoding
                    # Leave as-is but log warning
                    print(f"Warning: Failed to decrypt {key}: {e}")
        return result


# Singleton instance
_credential_encryption = None


def get_credential_encryption() -> CredentialEncryption:
    """
    Get or create credential encryption instance

    Loads encryption key from environment variable ENCRYPTION_KEY
    If not set, generates a new key (development only)
    """
    global _credential_encryption

    if _credential_encryption is None:
        # Try to load key from environment
        encryption_key = os.environ.get("ENCRYPTION_KEY")

        if not encryption_key:
            # Development mode: generate new key
            print("WARNING: ENCRYPTION_KEY not set in environment")
            print("Generating a new encryption key (development mode)")
            new_key = CredentialEncryption.generate_key()
            print(f"Generated key: {new_key}")
            print("Store this in your .env file as ENCRYPTION_KEY={key}")
            encryption_key = new_key

        _credential_encryption = CredentialEncryption(encryption_key)

    return _credential_encryption


def initialize_encryption_key():
    """
    Initialize or generate encryption key

    Run this once during setup to generate a key
    """
    env_file = ".env"

    # Check if key already exists
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            if "ENCRYPTION_KEY=" in content:
                print("Encryption key already exists in .env")
                return

    # Generate new key
    key = CredentialEncryption.generate_key()

    # Append to .env
    with open(env_file, 'a') as f:
        f.write(f"\n# Encryption key for credential storage\n")
        f.write(f"ENCRYPTION_KEY={key}\n")

    print(f"Generated and saved encryption key to {env_file}")
    print("Keep this file secure and never commit it to version control!")


if __name__ == "__main__":
    # Test encryption
    encryptor = CredentialEncryption()

    # Test basic encryption
    plaintext = "my_secret_password"
    encrypted = encryptor.encrypt(plaintext)
    decrypted = encryptor.decrypt(encrypted)

    print(f"Plaintext: {plaintext}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    assert plaintext == decrypted, "Encryption/decryption failed"
    print("Encryption test passed!")
