"""
SFTP API Endpoints
Manage SFTP credentials and file uploads
"""

from fastapi import APIRouter, HTTPException, UploadFile, File as FastAPIFile, Form
from typing import Optional
import tempfile
import os

from app.models.sftp import (
    SFTPCredential,
    SFTPCredentialInput,
    ConnectionTestResult,
    UploadResult
)
from app.services.sftp_manager import get_sftp_manager

router = APIRouter()


@router.get("/credentials")
async def get_credentials():
    """
    Get all SFTP credentials

    Returns:
        Dictionary with list of credentials
    """
    try:
        sftp_manager = get_sftp_manager()
        credentials = sftp_manager.get_all_credentials()

        return {
            "credentials": credentials,
            "count": len(credentials)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "CREDENTIALS_LOAD_ERROR",
                    "message": f"Error loading credentials: {str(e)}",
                },
                "status": 500
            }
        )


@router.post("/credentials", response_model=SFTPCredential)
async def create_credential(input_data: SFTPCredentialInput):
    """
    Create new SFTP credential

    Args:
        input_data: SFTP credential information

    Returns:
        Created credential (without password)
    """
    try:
        sftp_manager = get_sftp_manager()
        credential = sftp_manager.add_credential(
            name=input_data.name,
            host=input_data.host,
            port=input_data.port,
            username=input_data.username,
            password=input_data.password,
            remote_path=input_data.remote_path or "/"
        )

        return credential
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "CREDENTIAL_CREATE_ERROR",
                    "message": f"Error creating credential: {str(e)}",
                },
                "status": 500
            }
        )


@router.put("/credentials/{credential_id}", response_model=SFTPCredential)
async def update_credential(credential_id: str, input_data: SFTPCredentialInput):
    """
    Update existing SFTP credential

    Args:
        credential_id: Credential ID
        input_data: Updated credential information

    Returns:
        Updated credential (without password)
    """
    try:
        sftp_manager = get_sftp_manager()

        # Only update password if provided
        password = input_data.password if input_data.password else None

        credential = sftp_manager.update_credential(
            credential_id=credential_id,
            name=input_data.name,
            host=input_data.host,
            port=input_data.port,
            username=input_data.username,
            password=password,
            remote_path=input_data.remote_path
        )

        if not credential:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "CREDENTIAL_NOT_FOUND",
                        "message": f"Credential '{credential_id}' not found",
                    },
                    "status": 404
                }
            )

        return credential
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "CREDENTIAL_UPDATE_ERROR",
                    "message": f"Error updating credential: {str(e)}",
                },
                "status": 500
            }
        )


@router.delete("/credentials/{credential_id}")
async def delete_credential(credential_id: str):
    """
    Delete SFTP credential

    Args:
        credential_id: Credential ID

    Returns:
        Success message
    """
    try:
        sftp_manager = get_sftp_manager()
        success = sftp_manager.delete_credential(credential_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "CREDENTIAL_NOT_FOUND",
                        "message": f"Credential '{credential_id}' not found",
                    },
                    "status": 404
                }
            )

        return {"message": "Credential deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "CREDENTIAL_DELETE_ERROR",
                    "message": f"Error deleting credential: {str(e)}",
                },
                "status": 500
            }
        )


@router.post("/test-connection/{credential_id}", response_model=ConnectionTestResult)
async def test_connection(credential_id: str):
    """
    Test SFTP connection

    Args:
        credential_id: Credential ID

    Returns:
        Connection test result
    """
    try:
        sftp_manager = get_sftp_manager()
        result = sftp_manager.test_connection(credential_id)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "CONNECTION_TEST_ERROR",
                    "message": f"Error testing connection: {str(e)}",
                },
                "status": 500
            }
        )


@router.post("/upload/{credential_id}", response_model=UploadResult)
async def upload_file(
    credential_id: str,
    file: UploadFile = FastAPIFile(...),
    remote_path: Optional[str] = Form(None)
):
    """
    Upload file to SFTP server

    Args:
        credential_id: Credential ID
        file: File to upload
        remote_path: Optional remote path (overrides credential default)

    Returns:
        Upload result
    """
    temp_file = None
    try:
        sftp_manager = get_sftp_manager()

        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Upload to SFTP
        result = sftp_manager.upload_file(
            credential_id=credential_id,
            local_path=temp_file_path,
            remote_filename=file.filename,
            remote_path=remote_path
        )

        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass

        return result

    except Exception as e:
        # Clean up temp file on error
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass

        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "UPLOAD_ERROR",
                    "message": f"Error uploading file: {str(e)}",
                },
                "status": 500
            }
        )
