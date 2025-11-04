/**
 * TransformPreview Component
 * Preview transformation and export
 */

import React, { useEffect, useState } from 'react';
import { Download, Check, FileDown, Loader2, Upload, Server } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { previewTransform, exportCSV, downloadBlob } from '../../services/api';
import { getSFTPCredentials, uploadToSFTP, type SFTPCredential } from '../../services/sftp-api';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import type { PreviewResponse } from '../../types';

export const TransformPreview: React.FC = () => {
  const { uploadedFile, mappings, selectedEntityType, isLoading, setIsLoading } = useApp();
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  // SFTP state
  const [showSFTPModal, setShowSFTPModal] = useState(false);
  const [sftpCredentials, setSftpCredentials] = useState<SFTPCredential[]>([]);
  const [uploadingSFTP, setUploadingSFTP] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  useEffect(() => {
    loadPreview();
  }, []);

  const loadPreview = async () => {
    if (!uploadedFile || mappings.length === 0) return;

    try {
      setIsLoading(true);
      const response = await previewTransform({
        mappings,
        source_data: uploadedFile.sample_data,
        sample_size: 5,
      });
      setPreviewData(response);
    } catch (error) {
      console.error('Preview error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async () => {
    if (!uploadedFile || mappings.length === 0) return;

    try {
      setExporting(true);
      setExportSuccess(false);

      // Export full data using file_id (backend retrieves full dataset)
      const outputFilename = `${selectedEntityType.toUpperCase()}-MAIN.csv`;
      const blob = await exportCSV({
        mappings,
        file_id: uploadedFile.file_id,
        output_filename: outputFilename,
        entity_name: selectedEntityType,
      });

      downloadBlob(blob, outputFilename);
      setExportSuccess(true);

      setTimeout(() => setExportSuccess(false), 3000);
    } catch (error) {
      console.error('Export error:', error);
    } finally {
      setExporting(false);
    }
  };

  const loadSFTPCredentials = async () => {
    try {
      const creds = await getSFTPCredentials();
      setSftpCredentials(creds);
    } catch (error) {
      console.error('Error loading SFTP credentials:', error);
    }
  };

  const handleSFTPUpload = async (credentialId: string) => {
    if (!uploadedFile || mappings.length === 0) return;

    try {
      setUploadingSFTP(true);
      setUploadSuccess(false);

      // First, export the transformed data to get the file
      const outputFilename = `${selectedEntityType.toUpperCase()}-MAIN.csv`;
      const blob = await exportCSV({
        mappings,
        file_id: uploadedFile.file_id,
        output_filename: outputFilename,
        entity_name: selectedEntityType,
      });

      // Upload the blob to SFTP
      const result = await uploadToSFTP(credentialId, blob, outputFilename);

      if (result.success) {
        setUploadSuccess(true);
        alert(`Successfully uploaded to SFTP server!\nPath: ${result.path}`);
        setTimeout(() => setUploadSuccess(false), 5000);
      } else {
        alert(`SFTP Upload failed: ${result.error}`);
      }
    } catch (error: any) {
      console.error('SFTP upload error:', error);
      alert(`SFTP Upload failed: ${error.message || 'Unknown error'}`);
    } finally {
      setUploadingSFTP(false);
      setShowSFTPModal(false);
    }
  };

  const handleShowSFTPModal = () => {
    loadSFTPCredentials();
    setShowSFTPModal(true);
  };

  if (isLoading) {
    return (
      <Card padding="lg">
        <LoadingSpinner size="lg" text="Loading preview..." />
      </Card>
    );
  }

  if (!previewData) {
    return (
      <Card padding="lg">
        <p className="text-center text-gray-600">No preview data available</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Transformation Preview</h2>
        <p className="text-gray-600 mt-1">Review the transformed data before exporting</p>
      </div>

      {/* Transformations Applied */}
      <Card>
        <CardHeader>
          <CardTitle>Transformations Applied</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {previewData.transformations_applied.map((transformation, index) => (
              <div key={index} className="flex items-start gap-2 text-sm">
                <Check className="w-4 h-4 text-success-600 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">{transformation}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Before & After Comparison */}
      <div className="grid grid-cols-2 gap-6">
        {/* Before */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Before (Your Data)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedFile?.sample_data.slice(0, 2).map((row, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg text-sm">
                  {Object.entries(row).slice(0, 5).map(([key, value]) => (
                    <div key={key} className="flex justify-between py-1">
                      <span className="text-gray-600 font-medium">{key}:</span>
                      <span className="text-gray-900">{String(value)}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* After */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">After (Eightfold Format)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {previewData.transformed_data.slice(0, 2).map((row, index) => (
                <div key={index} className="p-3 bg-success-50 rounded-lg text-sm">
                  {Object.entries(row).slice(0, 5).map(([key, value]) => (
                    <div key={key} className="flex justify-between py-1">
                      <span className="text-gray-600 font-medium">{key}:</span>
                      <span className="text-gray-900 font-semibold">
                        {value !== null && value !== undefined ? String(value) : '—'}
                      </span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Full Preview Table */}
      <Card>
        <CardHeader>
          <CardTitle>Transformed Data Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-success-50 border-b-2 border-success-200">
                  {previewData.transformed_data[0] && Object.keys(previewData.transformed_data[0]).map((column, index) => (
                    <th
                      key={index}
                      className="px-4 py-3 text-left text-sm font-semibold text-gray-900"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewData.transformed_data.map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                  >
                    {Object.values(row).map((value, colIndex) => (
                      <td
                        key={colIndex}
                        className="px-4 py-3 text-sm text-gray-700 border-b border-gray-200"
                      >
                        {value !== null && value !== undefined
                          ? String(value)
                          : <span className="text-gray-400 italic">—</span>
                        }
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="text-sm text-gray-500 mt-4">
            Showing preview of {previewData.transformed_data.length} rows. Full export will include all {uploadedFile?.row_count.toLocaleString()} rows.
          </p>
        </CardContent>
      </Card>

      {/* Summary */}
      <Card>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-600">Input Rows</p>
              <p className="text-2xl font-bold text-gray-900">{uploadedFile?.row_count.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Fields Mapped</p>
              <p className="text-2xl font-bold text-primary-600">{mappings.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Output Rows</p>
              <p className="text-2xl font-bold text-success-600">{previewData.row_count.toLocaleString()}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Export Buttons */}
      <div className="flex justify-center gap-4">
        <Button
          variant="primary"
          size="lg"
          onClick={handleExport}
          isLoading={exporting}
          leftIcon={exportSuccess ? <Check className="w-5 h-5" /> : <FileDown className="w-5 h-5" />}
          className={exportSuccess ? 'bg-success-600 hover:bg-success-700' : ''}
        >
          {exportSuccess ? 'Downloaded Successfully!' : 'Download CSV'}
        </Button>

        <Button
          variant="primary"
          size="lg"
          onClick={handleShowSFTPModal}
          isLoading={uploadingSFTP}
          leftIcon={uploadSuccess ? <Check className="w-5 h-5" /> : <Upload className="w-5 h-5" />}
          className={uploadSuccess ? 'bg-success-600 hover:bg-success-700' : 'bg-indigo-600 hover:bg-indigo-700'}
        >
          {uploadSuccess ? 'Uploaded to SFTP!' : 'Upload to SFTP'}
        </Button>
      </div>

      {exportSuccess && (
        <div className="text-center">
          <p className="text-success-700 font-medium">
            File downloaded! Check your Downloads folder for {selectedEntityType.toUpperCase()}-MAIN.csv
          </p>
        </div>
      )}

      {uploadSuccess && (
        <div className="text-center">
          <p className="text-success-700 font-medium">
            File uploaded to SFTP server successfully!
          </p>
        </div>
      )}

      {/* SFTP Credential Selection Modal */}
      {showSFTPModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-md w-full">
            <div className="p-6 border-b border-gray-200 dark:border-gray-800">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Select SFTP Server
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Choose which server to upload to
              </p>
            </div>

            <div className="p-6">
              {sftpCredentials.length === 0 ? (
                <div className="text-center py-8">
                  <Server className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    No SFTP connections configured
                  </p>
                  <Button
                    variant="primary"
                    onClick={() => {
                      setShowSFTPModal(false);
                      // Navigate to SFTP settings (step 5)
                      window.location.hash = '#sftp';
                    }}
                  >
                    Configure SFTP
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  {sftpCredentials.map((cred) => (
                    <button
                      key={cred.id}
                      onClick={() => handleSFTPUpload(cred.id)}
                      disabled={uploadingSFTP}
                      className="w-full p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-indigo-500 dark:hover:border-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center flex-shrink-0">
                          <Server className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-gray-900 dark:text-white truncate">
                            {cred.name}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                            {cred.username}@{cred.host}:{cred.port}
                          </p>
                          {cred.remote_path && (
                            <p className="text-xs text-gray-500 dark:text-gray-500 truncate">
                              → {cred.remote_path}
                            </p>
                          )}
                        </div>
                        {uploadingSFTP && (
                          <Loader2 className="w-5 h-5 animate-spin text-indigo-600" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-800 flex justify-end">
              <Button
                variant="outline"
                onClick={() => setShowSFTPModal(false)}
                disabled={uploadingSFTP}
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransformPreview;
