/**
 * PreviewCSV Component
 * Preview CSV transformation and export
 */

import React, { useEffect, useState, useRef } from 'react';
import { Download, Check, FileDown, Loader2, Upload, Server, FileCode } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { useToast } from '../../contexts/ToastContext';
import { previewTransform, exportCSV, downloadBlob } from '../../services/api';
import { getSFTPCredentials, uploadToSFTP, type SFTPCredential } from '../../services/sftp-api';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import type { PreviewResponse } from '../../types';

export const PreviewCSV: React.FC = () => {
  const { uploadedFile, mappings, selectedEntityType, isLoading, setIsLoading, nextStep, setCurrentStep } = useApp();
  const toast = useToast();
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);

  // SFTP state
  const [showSFTPModal, setShowSFTPModal] = useState(false);
  const [sftpCredentials, setSftpCredentials] = useState<SFTPCredential[]>([]);
  const [uploadingSFTP, setUploadingSFTP] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Calculate dynamic column widths based on content
  const calculateColumnWidths = (data: any[]): Record<string, number> => {
    if (!data || data.length === 0) return {};

    const columns = Object.keys(data[0]);
    const columnWidths: Record<string, number> = {};

    columns.forEach((column) => {
      // Start with header width (8px per character + padding)
      let maxWidth = column.length * 8 + 32;

      // Check data content widths (sample first 50 rows for performance)
      data.slice(0, 50).forEach((row) => {
        const value = row[column];
        const valueStr = value !== null && value !== undefined ? String(value) : '—';
        const contentWidth = valueStr.length * 7.5 + 32; // 7.5px per char (approximation for monospace) + padding
        maxWidth = Math.max(maxWidth, contentWidth);
      });

      // Apply min/max constraints: min 100px, max 400px
      columnWidths[column] = Math.min(Math.max(maxWidth, 100), 400);
    });

    return columnWidths;
  };

  useEffect(() => {
    loadPreview();
  }, []);

  const loadPreview = async () => {
    if (!uploadedFile || mappings.length === 0) return;

    try {
      setIsLoading(true);
      console.log('[PreviewCSV] Loading preview with:', {
        file_id: uploadedFile.file_id,
        entity_name: selectedEntityType,
        mappings_count: mappings.length,
        sample_size: 50
      });

      const response = await previewTransform({
        mappings,
        file_id: uploadedFile.file_id,
        entity_name: selectedEntityType, // CRITICAL FIX: Added missing entity_name parameter
        sample_size: 50,
      });

      console.log('[PreviewCSV] Received response:', {
        transformed_data_length: response.transformed_data?.length || 0,
        row_count: response.row_count,
        transformations_count: response.transformations_applied?.length || 0
      });

      setPreviewData(response);
    } catch (error: any) {
      console.error('[PreviewCSV] Preview error:', error);
      console.error('[PreviewCSV] Error details:', error.response?.data);
      toast.error('Failed to load preview', error.response?.data?.error?.message || error.message);
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
        toast.error('SFTP Upload Failed', result.error);
      }
    } catch (error: any) {
      console.error('SFTP upload error:', error);
      toast.error('SFTP Upload Failed', error.message || 'Unknown error');
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
      <div className="p-6">
        <Card padding="lg">
          <LoadingSpinner size="lg" text="Loading preview..." />
        </Card>
      </div>
    );
  }

  if (!previewData) {
    return (
      <div className="p-6">
        <Card padding="lg">
          <p className="text-center text-gray-600 dark:text-gray-400">No preview data available</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Sticky Header with fade effect */}
      <div className="sticky top-0 z-10 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm -mx-6 px-6 pt-6 pb-4 mb-6 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Transformation Preview</h2>
        <p className="text-gray-600 dark:text-gray-400">Review the transformed data before exporting</p>
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
                <Check className="w-4 h-4 text-success-600 dark:text-success-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">{transformation}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Before & After Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Before */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Before (Your Data)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedFile?.sample_data && uploadedFile.sample_data.length > 0 ? (
                uploadedFile.sample_data.slice(0, 2).map((row, index) => (
                  <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg text-sm">
                    {Object.entries(row).slice(0, 5).map(([key, value]) => (
                      <div key={key} className="flex justify-between py-1">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">{key}:</span>
                        <span className="text-gray-900 dark:text-white">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                ))
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-sm">No sample data available</p>
              )}
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
              {previewData.transformed_data && previewData.transformed_data.length > 0 ? (
                previewData.transformed_data.slice(0, 2).map((row, index) => (
                  <div key={index} className="p-3 bg-success-50 dark:bg-success-900/20 rounded-lg text-sm">
                    {Object.entries(row).slice(0, 5).map(([key, value]) => (
                      <div key={key} className="flex justify-between py-1">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">{key}:</span>
                        <span className="text-gray-900 dark:text-white font-semibold">
                          {value !== null && value !== undefined ? String(value) : '—'}
                        </span>
                      </div>
                    ))}
                  </div>
                ))
              ) : (
                <p className="text-red-600 dark:text-red-400 text-sm">No transformed data - check mappings</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Full Preview Table */}
      {previewData.transformed_data && previewData.transformed_data.length > 0 && (() => {
        const columnWidths = calculateColumnWidths(previewData.transformed_data);
        const columns = Object.keys(previewData.transformed_data[0]);

        return (
          <Card>
            <CardHeader>
              <CardTitle>Transformed Data Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div ref={tableRef} className="overflow-x-auto -mx-6 px-6">
                <table className="border-collapse">
                  <thead>
                    <tr className="bg-success-50 dark:bg-success-900/20 border-b-2 border-success-200 dark:border-success-800">
                      {columns.map((column, index) => (
                        <th
                          key={index}
                          className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white whitespace-nowrap"
                          style={{ width: `${columnWidths[column]}px`, minWidth: `${columnWidths[column]}px` }}
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
                        className={rowIndex % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800'}
                      >
                        {columns.map((column, colIndex) => {
                          const value = row[column];
                          return (
                            <td
                              key={colIndex}
                              className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-700"
                              style={{ maxWidth: `${columnWidths[column]}px` }}
                            >
                              <div className="truncate" title={value !== null && value !== undefined ? String(value) : ''}>
                                {value !== null && value !== undefined
                                  ? String(value)
                                  : <span className="text-gray-400 dark:text-gray-500 italic">—</span>
                                }
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        );
      })()}

      {/* Summary */}
      <Card>
        <CardContent>
          <div className="grid grid-cols-3 gap-6 text-center py-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Input Rows</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{uploadedFile?.row_count.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Fields Mapped</p>
              <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{mappings.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Output Rows</p>
              <p className="text-2xl font-bold text-success-600 dark:text-success-400">{previewData.row_count.toLocaleString()}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Export Buttons */}
      <div className="flex justify-center gap-6 pt-4">
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
          onClick={nextStep}
          leftIcon={<FileCode className="w-5 h-5" />}
          className="bg-purple-600 hover:bg-purple-700"
        >
          Transform to XML
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
        <div className="text-center mt-4">
          <p className="text-success-700 dark:text-success-400 font-medium">
            File downloaded! Check your Downloads folder for {selectedEntityType.toUpperCase()}-MAIN.csv
          </p>
        </div>
      )}

      {uploadSuccess && (
        <div className="text-center mt-4">
          <p className="text-success-700 dark:text-success-400 font-medium">
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
                      setCurrentStep(6);
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

export default PreviewCSV;
