/**
 * DataPreview Component
 * Display uploaded data in a table
 */

import React from 'react';
import { FileText, ArrowRight } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';

export const DataPreview: React.FC = () => {
  const { uploadedFile, nextStep } = useApp();

  if (!uploadedFile) {
    return (
      <Card padding="lg">
        <p className="text-center text-gray-600">No file uploaded</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* File Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary-600" />
            {uploadedFile.filename}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Rows</p>
              <p className="text-2xl font-bold text-gray-900">{uploadedFile.row_count.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Columns</p>
              <p className="text-2xl font-bold text-gray-900">{uploadedFile.column_count}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">File Size</p>
              <p className="text-2xl font-bold text-gray-900">
                {(uploadedFile.file_size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Data Preview (First 10 Rows)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b-2 border-gray-200">
                  {uploadedFile.columns.map((column, index) => (
                    <th
                      key={index}
                      className="px-4 py-3 text-left text-sm font-semibold text-gray-900"
                    >
                      <div>
                        <div>{column}</div>
                        <div className="text-xs font-normal text-gray-500 mt-1">
                          {uploadedFile.data_types[column] || 'string'}
                        </div>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {uploadedFile.sample_data.map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                  >
                    {uploadedFile.columns.map((column, colIndex) => (
                      <td
                        key={colIndex}
                        className="px-4 py-3 text-sm text-gray-700 border-b border-gray-200"
                      >
                        {row[column] !== null && row[column] !== undefined
                          ? String(row[column])
                          : <span className="text-gray-400 italic">null</span>
                        }
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {uploadedFile.row_count > 10 && (
            <p className="text-sm text-gray-500 mt-4">
              Showing 10 of {uploadedFile.row_count.toLocaleString()} total rows
            </p>
          )}
        </CardContent>
      </Card>

      {/* Detected Columns */}
      <Card>
        <CardHeader>
          <CardTitle>Detected Columns</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {uploadedFile.columns.map((column, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium"
              >
                {column}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Continue Button */}
      <div className="flex justify-end">
        <Button
          variant="primary"
          size="lg"
          onClick={nextStep}
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          Continue to Field Mapping
        </Button>
      </div>
    </div>
  );
};

export default DataPreview;
