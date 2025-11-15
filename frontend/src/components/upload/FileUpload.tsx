/**
 * FileUpload Component
 * Drag-and-drop file upload for CSV/XML files
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Upload, File, Check, X, AlertCircle, Sparkles, ChevronDown, FileText } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { uploadFile, getSchema, getAvailableEntities, detectEntityType } from '../../services/api';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { CustomDropdown } from '../common/CustomDropdown';
import { SchemaViewer } from '../common/SchemaViewer';
import { cn } from '../../utils/cn';
import type { EntitySchema } from '../../types';

export const FileUpload: React.FC = () => {
  const {
    setUploadedFile,
    setSchema,
    selectedEntityType,
    setSelectedEntityType,
    nextStep,
    setIsLoading,
    setError,
    isLoading,
    error
  } = useApp();

  const [isDragging, setIsDragging] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [availableEntities, setAvailableEntities] = useState<any[]>([]);
  const [entitiesLoading, setEntitiesLoading] = useState(true);
  const [showAutoDetect, setShowAutoDetect] = useState(false);
  const [detectedEntity, setDetectedEntity] = useState<string | null>(null);
  const [detectedVariant, setDetectedVariant] = useState<string | null>(null);
  const [variantDisplayName, setVariantDisplayName] = useState<string | null>(null);
  const [detectionConfidence, setDetectionConfidence] = useState<number>(0);
  const [showSampleDropdown, setShowSampleDropdown] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'complete' | 'error'>('idle');
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [pendingFileData, setPendingFileData] = useState<any>(null);
  const [isManualSelection, setIsManualSelection] = useState(false);
  const [showSchemaViewer, setShowSchemaViewer] = useState(false);
  const [schemaToView, setSchemaToView] = useState<EntitySchema | null>(null);

  const sampleFiles = [
    { name: 'Employee Sample 1 (10 records)', path: '/samples/employee_sample_1.csv' },
    { name: 'Employee Sample 2 (5 records)', path: '/samples/employee_sample_2.csv' },
  ];

  // Load available entities on mount
  useEffect(() => {
    const loadEntities = async () => {
      try {
        setEntitiesLoading(true);
        const response = await getAvailableEntities();
        // Show all available entities
        setAvailableEntities(response.entities || []);
      } catch (err) {
        console.error('Error loading entities:', err);
        // Set fallback to employee only if API fails
        setAvailableEntities([
          { id: 'employee', name: 'Employee', description: 'Employee master data' }
        ]);
      } finally {
        setEntitiesLoading(false);
      }
    };
    loadEntities();
  }, []);

  const handleFileSelect = useCallback(async (file: File) => {
    // Validate file type
    const validTypes = ['.csv', '.xml'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!validTypes.includes(fileExtension)) {
      setError('Invalid file type. Please upload CSV or XML files (.csv, .xml)');
      return;
    }

    // Validate file size (100 MB)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`File is too large (${(file.size / 1024 / 1024).toFixed(2)} MB). Maximum size is 100 MB.`);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setUploadStatus('uploading');
      setUploadProgress(0);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);

      // Upload file
      const response = await uploadFile(file);
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('processing');
      setUploadedFile(response);

      // Try to auto-detect entity type from columns
      if (response.columns && response.columns.length > 0) {
        try {
          const detection = await detectEntityType(response.columns, file.name);
          if (detection.confidence > 0.5) {
            setDetectedEntity(detection.detected_entity);
            setDetectedVariant(detection.detected_variant || null);
            setVariantDisplayName(detection.variant_display_name || null);
            setDetectionConfidence(detection.confidence);
            setShowAutoDetect(true);

            // Store pending data and show confirmation instead of auto-proceeding
            setPendingFileData(response);
            setUploadStatus('complete');
            setShowConfirmation(true);

            // Auto-select detected entity but require confirmation
            setSelectedEntityType(detection.detected_entity);
            return; // Don't proceed automatically
          }
        } catch (err) {
          console.warn('Entity detection failed, using manual selection');
        }
      }

      // If no detection or low confidence, proceed with manual flow
      await proceedWithUpload(response);

    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Error uploading file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [setUploadedFile, setSchema, selectedEntityType, setSelectedEntityType, nextStep, setIsLoading, setError]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleLoadSample = useCallback(async (samplePath: string) => {
    try {
      setIsLoading(true);
      setError(null);
      setShowSampleDropdown(false);

      // Fetch sample file from public folder
      console.log('Fetching sample file from:', samplePath);
      const response = await fetch(samplePath);

      if (!response.ok) {
        throw new Error(`Failed to fetch sample file: ${response.status} ${response.statusText}`);
      }

      const blob = await response.blob();
      console.log('Sample file loaded, size:', blob.size, 'bytes');

      const filename = samplePath.split('/').pop() || 'sample.csv';

      // Create File object from Blob
      const file = new (window as any).File([blob], filename, {
        type: 'text/csv',
        lastModified: Date.now()
      });

      console.log('Created file object:', file.name, file.size, file.type);
      await handleFileSelect(file);
    } catch (err: any) {
      console.error('Error loading sample file:', err);
      setError(`Error loading sample file: ${err.message || 'Please try uploading your own file.'}`);
      setIsLoading(false);
    }
  }, [handleFileSelect, setIsLoading, setError]);

  const proceedWithUpload = useCallback(async (response: any) => {
    try {
      // Load schema for selected entity type
      const schemaData = await getSchema(selectedEntityType);
      setSchema(schemaData);
      setUploadedFile(response);
      setUploadSuccess(true);

      // Auto-advance to next step after 1 second
      setTimeout(() => {
        nextStep();
      }, 1000);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Error loading schema. Please try again.');
      setIsLoading(false);
    }
  }, [selectedEntityType, setSchema, setUploadedFile, nextStep, setError]);

  const handleConfirmDetection = useCallback(async (confirmed: boolean) => {
    setShowConfirmation(false);

    if (confirmed && pendingFileData) {
      // User confirmed the detection, proceed with detected entity
      await proceedWithUpload(pendingFileData);
      setPendingFileData(null);
    } else {
      // User wants to manually select, show entity selector and reset to upload state
      setShowAutoDetect(false);
      setDetectedEntity(null);
      setDetectedVariant(null);
      setVariantDisplayName(null);
      setUploadStatus('complete');
      setIsManualSelection(true);
      // Don't proceed with upload yet - wait for manual entity selection
      // pendingFileData stays available for when user makes manual selection
    }
  }, [pendingFileData, proceedWithUpload]);

  const handleManualProceed = useCallback(async () => {
    if (pendingFileData && selectedEntityType) {
      setIsManualSelection(false);
      await proceedWithUpload(pendingFileData);
      setPendingFileData(null);
    }
  }, [pendingFileData, selectedEntityType, proceedWithUpload]);

  const handleViewSchema = useCallback(async (entityType: string) => {
    try {
      const schemaData = await getSchema(entityType);
      setSchemaToView(schemaData);
      setShowSchemaViewer(true);
    } catch (err: any) {
      console.error('Error loading schema:', err);
      setError(err.response?.data?.error?.message || 'Error loading schema');
    }
  }, [setError]);

  const resetUploadState = useCallback(() => {
    setShowConfirmation(false);
    setUploadSuccess(false);
    setShowAutoDetect(false);
    setDetectedEntity(null);
    setDetectedVariant(null);
    setVariantDisplayName(null);
    setDetectionConfidence(0);
    setPendingFileData(null);
    setUploadProgress(0);
    setUploadStatus('idle');
    setIsManualSelection(false);
    setShowSchemaViewer(false);
    setSchemaToView(null);
    setError(null);
  }, [setError]);

  return (
    <div className="max-w-2xl mx-auto">
      <Card padding="lg">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Upload Your Data
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            Upload your data from any HR system or flat file source
          </p>
        </div>

        {/* Manual Selection Message */}
        {isManualSelection && (
          <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0">
                <File className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                  File Uploaded Successfully
                </h3>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  Please select the correct entity type and click continue to proceed.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Entity Type Selector */}
        {!uploadSuccess && !showConfirmation && (
          <div className="mb-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
              📋 Select Entity Type
            </label>
            <CustomDropdown
              value={selectedEntityType}
              onChange={setSelectedEntityType}
              options={entitiesLoading ?
                [{ value: "", label: "Loading entity types..." }] :
                availableEntities.length === 0 ?
                  [{ value: "employee", label: "Employee (default)" }] :
                  availableEntities.map(entity => ({
                    value: entity.id,
                    label: `${entity.name} - ${entity.description}`
                  }))
              }
              disabled={isLoading || entitiesLoading}
              placeholder="Select Entity Type"
            />
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              {isManualSelection ?
                "Please select the correct entity type for your file" :
                "AI will auto-detect the entity type after you upload your file"
              }
            </p>
            {showAutoDetect && detectedEntity && (
              <div className="mt-2 flex items-center gap-2 text-sm">
                <Sparkles className="w-4 h-4 text-primary-600" />
                <span className="text-gray-700 dark:text-gray-300">
                  AI detected: <strong>{variantDisplayName || detectedEntity}</strong> ({Math.round(detectionConfidence * 100)}% confidence)
                </span>
              </div>
            )}

            {/* Manual Selection Continue Button */}
            {isManualSelection && selectedEntityType && uploadStatus === 'complete' && (
              <div className="mt-4">
                <Button
                  onClick={handleManualProceed}
                  variant="primary"
                  size="md"
                  className="w-full"
                >
                  Continue with {availableEntities.find(e => e.id === selectedEntityType)?.name || selectedEntityType}
                </Button>
                <p className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                  Your file is ready. Click continue to proceed with the selected entity type.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Sample Files Loader */}
        {!uploadSuccess && !showConfirmation && !isManualSelection && (
          <div className="mb-6 relative">
            <Button
              variant="outline"
              size="md"
              onClick={() => setShowSampleDropdown(!showSampleDropdown)}
              disabled={isLoading}
              className="w-full"
            >
              <File className="w-4 h-4 mr-2" />
              Try with Sample Data
            </Button>

            {showSampleDropdown && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg shadow-lg z-10">
                {sampleFiles.map((sample, index) => (
                  <button
                    key={index}
                    onClick={() => handleLoadSample(sample.path)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors first:rounded-t-lg last:rounded-b-lg"
                  >
                    <p className="font-medium text-gray-900 dark:text-white">{sample.name}</p>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Upload Area */}
        {!showConfirmation && !isManualSelection && (
          <div
            className={cn(
              'relative border-2 border-dashed rounded-lg p-12 text-center transition-all duration-200',
              isDragging && 'border-primary-500 bg-primary-50',
              !isDragging && 'border-gray-300 dark:border-gray-600 hover:border-primary-400',
              uploadSuccess && 'border-success-500 bg-success-50',
              error && 'border-error-500 bg-error-50'
            )}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
          {isLoading ? (
            <LoadingSpinner size="lg" text="Uploading and parsing file..." />
          ) : uploadSuccess ? (
            <div className="flex flex-col items-center gap-3">
              <div className="w-16 h-16 rounded-full bg-success-100 flex items-center justify-center">
                <Check className="w-8 h-8 text-success-600" />
              </div>
              <p className="text-lg font-semibold text-success-700">File uploaded successfully!</p>
              <p className="text-sm text-gray-600">Proceeding to field mapping...</p>
            </div>
          ) : (
            <>
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".csv,.xml"
                onChange={handleInputChange}
                disabled={isLoading}
              />

              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center gap-4"
              >
                <div className={cn(
                  'w-16 h-16 rounded-full flex items-center justify-center transition-colors',
                  error ? 'bg-error-100' : 'bg-primary-100'
                )}>
                  {error ? (
                    <AlertCircle className="w-8 h-8 text-error-600" />
                  ) : (
                    <Upload className="w-8 h-8 text-primary-600" />
                  )}
                </div>

                <div>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                    Drop your file here, or <span className="text-primary-600 dark:text-primary-400">browse</span>
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Supports CSV and XML (.csv, .xml)
                  </p>
                </div>

                <div onClick={() => document.getElementById('file-upload')?.click()}>
                  <Button variant="primary" size="lg" type="button">
                    <File className="w-4 h-4" />
                    Browse Files
                  </Button>
                </div>
              </label>
            </>
          )}
          </div>
        )}

        {/* Confirmation Dialog for AI Detection */}
        {showConfirmation && detectedEntity && (
          <div className="mt-4">
            <Card padding="md">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Please Confirm File Detection
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 mb-4">
                    I detected this is a <strong className="text-blue-600 dark:text-blue-400">
                      {variantDisplayName || detectedEntity}
                    </strong> file with <strong>{Math.round(detectionConfidence * 100)}% confidence</strong>.
                  </p>
                  {variantDisplayName && (
                    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mb-4">
                      <p className="text-sm text-blue-800 dark:text-blue-200 font-medium mb-1">
                        Specific Format Detected
                      </p>
                      <p className="text-sm text-blue-700 dark:text-blue-300">
                        This appears to be <strong>{variantDisplayName}</strong> based on the field patterns found in your file.
                      </p>
                    </div>
                  )}
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mb-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      <strong>What this means:</strong>
                    </p>
                    <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <li>• Your file will be processed as <strong>{variantDisplayName || detectedEntity}</strong> data</li>
                      <li>• Field mapping will be optimized for {variantDisplayName ? 'this specific' : detectedEntity} schema{variantDisplayName ? '' : 's'}</li>
                      <li>• You can change this selection if it's incorrect</li>
                    </ul>
                  </div>
                  <div className="flex gap-3 flex-wrap">
                    <Button
                      onClick={() => handleConfirmDetection(true)}
                      variant="primary"
                      size="md"
                      className="flex items-center gap-2"
                    >
                      <Check className="w-4 h-4" />
                      Yes, this is {variantDisplayName || detectedEntity} data
                    </Button>
                    <Button
                      onClick={() => handleViewSchema(detectedEntity!)}
                      variant="ghost"
                      size="md"
                      className="flex items-center gap-2"
                    >
                      <FileText className="w-4 h-4" />
                      View Schema
                    </Button>
                    <Button
                      onClick={() => handleConfirmDetection(false)}
                      variant="outline"
                      size="md"
                      className="flex items-center gap-2"
                    >
                      <X className="w-4 h-4" />
                      No, let me choose manually
                    </Button>
                    <Button
                      onClick={resetUploadState}
                      variant="ghost"
                      size="sm"
                      className="flex items-center gap-2 text-gray-500"
                    >
                      <Upload className="w-4 h-4" />
                      Start Over
                    </Button>
                  </div>
                  {detectionConfidence < 0.7 && (
                    <div className="mt-3 p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded text-sm">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-500" />
                        <span className="text-yellow-800 dark:text-yellow-300">
                          Low confidence detection - please verify this is correct
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-error-50 border border-error-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-error-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold text-error-900">Upload Error</p>
              <p className="text-sm text-error-700 mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-error-600 hover:text-error-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Info */}
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <p className="text-sm text-gray-700 dark:text-gray-200 font-semibold mb-2">Supported formats:</p>
          <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
            <li>• CSV files (.csv)</li>
            <li>• XML files (.xml)</li>
            <li>• Maximum file size: 100 MB</li>
          </ul>
        </div>
      </Card>

      {/* Schema Viewer Modal */}
      {showSchemaViewer && schemaToView && (
        <SchemaViewer
          schema={schemaToView}
          onClose={() => {
            setShowSchemaViewer(false);
            setSchemaToView(null);
          }}
        />
      )}
    </div>
  );
};

export default FileUpload;
