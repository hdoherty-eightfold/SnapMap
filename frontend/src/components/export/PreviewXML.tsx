/**
 * PreviewXML Component
 * Preview XML transformation and download
 */

import React, { useEffect, useState } from 'react';
import { Download, Check, FileDown, ArrowLeft, Upload, Code } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { previewXML, exportXML, downloadBlob } from '../../services/api';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface XMLPreviewResponse {
  xml_preview: string;
  preview_row_count: number;
  total_row_count: number;
}

export const PreviewXML: React.FC = () => {
  const { uploadedFile, mappings, selectedEntityType, isLoading, setIsLoading, previousStep, nextStep } = useApp();
  const [xmlPreview, setXmlPreview] = useState<XMLPreviewResponse | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  useEffect(() => {
    loadXMLPreview();
  }, []);

  const loadXMLPreview = async () => {
    if (!uploadedFile || mappings.length === 0) return;

    try {
      setIsLoading(true);
      const response = await previewXML({
        file_id: uploadedFile.file_id,
        mappings,
        entity_name: selectedEntityType,
      });
      setXmlPreview(response);
    } catch (error) {
      console.error('XML Preview error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportXML = async () => {
    if (!uploadedFile || mappings.length === 0) return;

    try {
      setExporting(true);
      setExportSuccess(false);

      const outputFilename = `${selectedEntityType.toUpperCase()}-MAIN.xml`;
      const blob = await exportXML({
        file_id: uploadedFile.file_id,
        mappings,
        entity_name: selectedEntityType,
      });

      downloadBlob(blob, outputFilename);
      setExportSuccess(true);

      setTimeout(() => setExportSuccess(false), 3000);
    } catch (error) {
      console.error('XML Export error:', error);
    } finally {
      setExporting(false);
    }
  };

  if (isLoading) {
    return (
      <Card padding="lg">
        <LoadingSpinner size="lg" text="Loading XML preview..." />
      </Card>
    );
  }

  if (!xmlPreview) {
    return (
      <Card padding="lg">
        <p className="text-center text-gray-600">No XML preview data available</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">XML Preview</h2>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Review the XML format before downloading</p>
      </div>

      {/* Row Count Info */}
      <Card>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                <Code className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Preview Sample</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {xmlPreview.preview_row_count} of {xmlPreview.total_row_count.toLocaleString()} records
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600 dark:text-gray-400">Entity Type</p>
              <p className="text-lg font-semibold text-purple-600 dark:text-purple-400 uppercase">
                {selectedEntityType}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* XML Preview */}
      <Card>
        <CardHeader>
          <CardTitle>XML Structure Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-900 dark:bg-gray-950 rounded-lg p-4 overflow-auto max-h-[600px]">
            <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap break-words">
              {xmlPreview.xml_preview}
            </pre>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-4">
            Showing preview of {xmlPreview.preview_row_count} records. Full export will include all {xmlPreview.total_row_count.toLocaleString()} records.
          </p>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardContent>
          <div className="flex items-start gap-3">
            <span className="text-blue-600 dark:text-blue-400 text-lg">ℹ️</span>
            <div>
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">About XML Export</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                The XML format contains the same data as CSV but in a structured XML format.
                Each employee record is represented as an XML element with nested fields.
                This format is useful for systems that require XML-based data interchange.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          size="lg"
          onClick={previousStep}
          leftIcon={<ArrowLeft className="w-5 h-5" />}
        >
          Back to CSV
        </Button>

        <div className="flex gap-4">
          <Button
            variant="primary"
            size="lg"
            onClick={handleExportXML}
            isLoading={exporting}
            leftIcon={exportSuccess ? <Check className="w-5 h-5" /> : <FileDown className="w-5 h-5" />}
            className={exportSuccess ? 'bg-success-600 hover:bg-success-700' : 'bg-purple-600 hover:bg-purple-700'}
          >
            {exportSuccess ? 'Downloaded Successfully!' : 'Download Full XML'}
          </Button>

          <Button
            variant="primary"
            size="lg"
            onClick={nextStep}
            leftIcon={<Upload className="w-5 h-5" />}
            className="bg-indigo-600 hover:bg-indigo-700"
          >
            Upload to SFTP
          </Button>
        </div>
      </div>

      {exportSuccess && (
        <div className="text-center">
          <p className="text-success-700 dark:text-success-400 font-medium">
            File downloaded! Check your Downloads folder for {selectedEntityType.toUpperCase()}-MAIN.xml
          </p>
        </div>
      )}
    </div>
  );
};

export default PreviewXML;
