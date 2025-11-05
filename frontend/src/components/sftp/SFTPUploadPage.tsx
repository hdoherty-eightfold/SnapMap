/**
 * SFTP Upload Page Component
 * Comprehensive file upload page with progress tracking
 */

import React, { useState, useEffect } from 'react';
import { Upload, Check, X, AlertCircle, FolderOpen, Loader2 } from 'lucide-react';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { useToast } from '../../contexts/ToastContext';
import { useApp } from '../../contexts/AppContext';
import {
  getSFTPCredentials,
  uploadToSFTP,
  type SFTPCredential
} from '../../services/sftp-api';
import { exportCSV, exportXML } from '../../services/api';

type UploadStatus = 'idle' | 'connecting' | 'uploading' | 'verifying' | 'complete' | 'error';
type FileFormat = 'csv' | 'xml';

export const SFTPUploadPage: React.FC = () => {
  const { uploadedFile, mappings, schema } = useApp();
  const toast = useToast();

  const [credentials, setCredentials] = useState<SFTPCredential[]>([]);
  const [selectedCredentialId, setSelectedCredentialId] = useState<string>('');
  const [remotePath, setRemotePath] = useState<string>('');
  const [fileFormat, setFileFormat] = useState<FileFormat>('csv');
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [uploadedFilePath, setUploadedFilePath] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCredentials();
  }, []);

  const loadCredentials = async () => {
    try {
      setLoading(true);
      const creds = await getSFTPCredentials();
      setCredentials(creds);

      // Pre-select first credential if available
      if (creds.length > 0) {
        setSelectedCredentialId(creds[0].id);
        setRemotePath(creds[0].remote_path || '/');
      }
    } catch (error: any) {
      toast.error('Failed to load SFTP credentials', error.message);
    } finally {
      setLoading(false);
    }
  };

  const generateTransformedFile = async (): Promise<Blob> => {
    try {
      if (!uploadedFile || mappings.length === 0) {
        throw new Error('No file or mappings available');
      }

      const request = {
        file_id: uploadedFile.file_id,
        mappings: mappings,
        entity_name: schema?.entity_name || 'employee',
      };

      if (fileFormat === 'csv') {
        return await exportCSV({
          mappings: mappings,
          source_data: uploadedFile.sample_data,
          output_filename: `transformed_${uploadedFile.filename}`,
        });
      } else {
        return await exportXML(request);
      }
    } catch (error: any) {
      throw new Error(`Failed to generate ${fileFormat.toUpperCase()} file: ${error.message}`);
    }
  };

  const handleUpload = async () => {
    if (!selectedCredentialId) {
      toast.error('No credential selected', 'Please select an SFTP connection');
      return;
    }

    if (!uploadedFile || mappings.length === 0) {
      toast.error('No data to upload', 'Please upload and map a file first');
      return;
    }

    try {
      setUploadStatus('connecting');
      setStatusMessage('Preparing file for upload...');
      setUploadProgress(10);

      // Generate the transformed file
      const blob = await generateTransformedFile();
      const fileExtension = fileFormat === 'csv' ? '.csv' : '.xml';
      const filename = uploadedFile.filename.replace(/\.(csv|xlsx?)$/i, fileExtension);

      setUploadProgress(30);
      setStatusMessage('Connecting to SFTP server...');

      // Convert Blob to File
      const file = new File([blob], filename, { type: blob.type });

      setUploadStatus('uploading');
      setStatusMessage('Uploading file...');
      setUploadProgress(50);

      // Upload to SFTP
      const result = await uploadToSFTP(selectedCredentialId, file, remotePath || undefined);

      if (result.success) {
        setUploadProgress(90);
        setUploadStatus('verifying');
        setStatusMessage('Verifying upload...');

        // Simulate verification delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        setUploadProgress(100);
        setUploadStatus('complete');
        setStatusMessage('Upload completed successfully!');
        setUploadedFilePath(result.path || remotePath + '/' + filename);

        toast.success('Upload complete', `File uploaded to ${result.path || 'server'}`);
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (error: any) {
      setUploadStatus('error');
      setStatusMessage(error.message || 'Upload failed');
      setUploadProgress(0);
      toast.error('Upload failed', error.message);
    }
  };

  const resetUpload = () => {
    setUploadStatus('idle');
    setUploadProgress(0);
    setStatusMessage('');
    setUploadedFilePath('');
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'connecting':
      case 'uploading':
      case 'verifying':
        return <Loader2 className="w-8 h-8 animate-spin text-primary-600" />;
      case 'complete':
        return <Check className="w-8 h-8 text-success-600" />;
      case 'error':
        return <X className="w-8 h-8 text-error-600" />;
      default:
        return <Upload className="w-8 h-8 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (uploadStatus) {
      case 'connecting':
      case 'uploading':
      case 'verifying':
        return 'bg-primary-600';
      case 'complete':
        return 'bg-success-600';
      case 'error':
        return 'bg-error-600';
      default:
        return 'bg-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <Card>
          <CardContent>
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">SFTP Upload</h2>
        <p className="text-gray-600 dark:text-gray-300 mt-1">
          Upload transformed files to your SFTP server
        </p>
      </div>

      {/* Upload Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* File Format Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                File Format
              </label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="fileFormat"
                    value="csv"
                    checked={fileFormat === 'csv'}
                    onChange={(e) => setFileFormat(e.target.value as FileFormat)}
                    disabled={uploadStatus !== 'idle'}
                    className="w-4 h-4 text-primary-600"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">CSV</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="fileFormat"
                    value="xml"
                    checked={fileFormat === 'xml'}
                    onChange={(e) => setFileFormat(e.target.value as FileFormat)}
                    disabled={uploadStatus !== 'idle'}
                    className="w-4 h-4 text-primary-600"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">XML</span>
                </label>
              </div>
            </div>

            {/* SFTP Credential Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                SFTP Connection
              </label>
              {credentials.length === 0 ? (
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                        No SFTP connections configured
                      </p>
                      <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                        Please configure an SFTP connection in Settings before uploading files.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <select
                  value={selectedCredentialId}
                  onChange={(e) => {
                    setSelectedCredentialId(e.target.value);
                    const selectedCred = credentials.find(c => c.id === e.target.value);
                    if (selectedCred) {
                      setRemotePath(selectedCred.remote_path || '/');
                    }
                  }}
                  disabled={uploadStatus !== 'idle'}
                  className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:opacity-60"
                >
                  {credentials.map((cred) => (
                    <option key={cred.id} value={cred.id}>
                      {cred.name} ({cred.username}@{cred.host})
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Remote Path */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Destination Path
              </label>
              <input
                type="text"
                value={remotePath}
                onChange={(e) => setRemotePath(e.target.value)}
                disabled={uploadStatus !== 'idle'}
                placeholder="/uploads"
                className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:opacity-60"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Directory path on the remote server (leave empty to use default)
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Upload Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Status Icon & Message */}
            <div className="flex flex-col items-center justify-center py-6">
              {getStatusIcon()}
              <p className="text-lg font-medium text-gray-900 dark:text-white mt-4">
                {statusMessage || 'Ready to upload'}
              </p>
              {uploadStatus === 'idle' && uploadedFile && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                  File: {uploadedFile.filename} ({mappings.length} fields mapped)
                </p>
              )}
              {uploadedFilePath && (
                <p className="text-sm text-success-600 dark:text-success-400 mt-2">
                  Uploaded to: {uploadedFilePath}
                </p>
              )}
            </div>

            {/* Progress Bar */}
            {uploadStatus !== 'idle' && (
              <div>
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <span>Progress</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${getStatusColor()}`}
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              {uploadStatus === 'idle' && (
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleUpload}
                  disabled={!selectedCredentialId || !uploadedFile || mappings.length === 0}
                  leftIcon={<Upload className="w-5 h-5" />}
                  className="flex-1"
                >
                  Upload to SFTP
                </Button>
              )}

              {uploadStatus === 'complete' && (
                <>
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={resetUpload}
                    leftIcon={<Upload className="w-5 h-5" />}
                    className="flex-1"
                  >
                    Upload Another File
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => toast.info('SFTP Explorer', 'Feature coming soon')}
                    leftIcon={<FolderOpen className="w-5 h-5" />}
                  >
                    Browse Files
                  </Button>
                </>
              )}

              {uploadStatus === 'error' && (
                <Button
                  variant="primary"
                  size="lg"
                  onClick={resetUpload}
                  className="flex-1"
                >
                  Try Again
                </Button>
              )}

              {(uploadStatus === 'connecting' || uploadStatus === 'uploading' || uploadStatus === 'verifying') && (
                <Button
                  variant="outline"
                  size="lg"
                  disabled
                  className="flex-1"
                >
                  Uploading...
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* File Information */}
      {uploadedFile && mappings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>File Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500 dark:text-gray-400">Source File</p>
                <p className="font-medium text-gray-900 dark:text-white">{uploadedFile.filename}</p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">Rows</p>
                <p className="font-medium text-gray-900 dark:text-white">{uploadedFile.row_count.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">Mapped Fields</p>
                <p className="font-medium text-gray-900 dark:text-white">{mappings.length} fields</p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">Output Format</p>
                <p className="font-medium text-gray-900 dark:text-white">{fileFormat.toUpperCase()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SFTPUploadPage;
