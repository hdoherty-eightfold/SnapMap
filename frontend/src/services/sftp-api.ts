/**
 * SFTP API Service
 * Handles SFTP credential management and file uploads
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SFTPCredential {
  id: string;
  name: string;
  host: string;
  port: number;
  username: string;
  remote_path?: string;
  connection_status?: 'connected' | 'failed' | 'unknown';
  last_tested?: string;
  created_at: string;
  updated_at: string;
}

export interface SFTPCredentialInput {
  name: string;
  host: string;
  port: number;
  username: string;
  password: string;
  remote_path?: string;
}

export interface ConnectionTestResult {
  success: boolean;
  message?: string;
  error?: string;
}

/**
 * Get all SFTP credentials
 */
export const getSFTPCredentials = async (): Promise<SFTPCredential[]> => {
  const response = await axios.get(`${API_URL}/api/sftp/credentials`);
  return response.data.credentials;
};

/**
 * Add new SFTP credential
 */
export const addSFTPCredential = async (input: SFTPCredentialInput): Promise<SFTPCredential> => {
  const response = await axios.post(`${API_URL}/api/sftp/credentials`, input);
  return response.data;
};

/**
 * Update existing SFTP credential
 */
export const updateSFTPCredential = async (
  id: string,
  input: SFTPCredentialInput
): Promise<SFTPCredential> => {
  const response = await axios.put(`${API_URL}/api/sftp/credentials/${id}`, input);
  return response.data;
};

/**
 * Delete SFTP credential
 */
export const deleteSFTPCredential = async (id: string): Promise<void> => {
  await axios.delete(`${API_URL}/api/sftp/credentials/${id}`);
};

/**
 * Test SFTP connection
 */
export const testSFTPConnection = async (id: string): Promise<ConnectionTestResult> => {
  const response = await axios.post(`${API_URL}/api/sftp/test-connection/${id}`);
  return response.data;
};

/**
 * Upload file to SFTP server
 */
export const uploadToSFTP = async (
  credentialId: string,
  file: File,
  remotePath?: string
): Promise<{ success: boolean; path?: string; error?: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  if (remotePath) {
    formData.append('remote_path', remotePath);
  }

  const response = await axios.post(
    `${API_URL}/api/sftp/upload/${credentialId}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
};
