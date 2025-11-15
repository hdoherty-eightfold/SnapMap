/**
 * Schema Viewer Component
 * Displays detailed field information for a schema
 */

import React, { useState } from 'react';
import { X, FileText, Info, CheckCircle, AlertCircle, Hash, Calendar, Mail, Type, ToggleLeft } from 'lucide-react';
import type { EntitySchema, FieldDefinition, DataType } from '../../types';
import { Button } from './Button';
import { Card } from './Card';

interface SchemaViewerProps {
  schema: EntitySchema;
  onClose: () => void;
}

const getTypeIcon = (type: DataType) => {
  switch (type) {
    case 'string':
      return <Type className="w-4 h-4" />;
    case 'number':
      return <Hash className="w-4 h-4" />;
    case 'date':
    case 'datetime':
      return <Calendar className="w-4 h-4" />;
    case 'email':
      return <Mail className="w-4 h-4" />;
    case 'boolean':
      return <ToggleLeft className="w-4 h-4" />;
    default:
      return <Type className="w-4 h-4" />;
  }
};

const getTypeColor = (type: DataType) => {
  switch (type) {
    case 'string':
      return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
    case 'number':
      return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
    case 'date':
    case 'datetime':
      return 'text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/20';
    case 'email':
      return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/20';
    case 'boolean':
      return 'text-indigo-600 bg-indigo-100 dark:text-indigo-400 dark:bg-indigo-900/20';
    default:
      return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
  }
};

export const SchemaViewer: React.FC<SchemaViewerProps> = ({ schema, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'required' | 'optional'>('all');

  const filteredFields = schema.fields.filter(field => {
    const matchesSearch = field.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         field.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         field.description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilter = filterType === 'all' ||
                         (filterType === 'required' && field.required) ||
                         (filterType === 'optional' && !field.required);

    return matchesSearch && matchesFilter;
  });

  const requiredCount = schema.fields.filter(f => f.required).length;
  const optionalCount = schema.fields.length - requiredCount;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-primary-600" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {schema.display_name}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {schema.description}
              </p>
            </div>
          </div>
          <Button
            onClick={onClose}
            variant="ghost"
            size="sm"
            className="p-2"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Stats and Controls */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <span className="font-medium">{schema.fields.length}</span> total fields
              </div>
              <div className="flex items-center gap-1 text-sm text-red-600 dark:text-red-400">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium">{requiredCount}</span> required
              </div>
              <div className="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-500">
                <AlertCircle className="w-4 h-4" />
                <span className="font-medium">{optionalCount}</span> optional
              </div>
            </div>

            <div className="flex gap-2">
              {/* Filter buttons */}
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as 'all' | 'required' | 'optional')}
                className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Fields</option>
                <option value="required">Required Only</option>
                <option value="optional">Optional Only</option>
              </select>

              {/* Search */}
              <input
                type="text"
                placeholder="Search fields..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 w-48"
              />
            </div>
          </div>
        </div>

        {/* Fields List */}
        <div className="overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
          {filteredFields.length === 0 ? (
            <div className="p-6 text-center text-gray-500 dark:text-gray-400">
              No fields found matching your criteria
            </div>
          ) : (
            <div className="p-6 space-y-4">
              {filteredFields.map((field, index) => (
                <Card key={field.name} padding="md" className="border-l-4 border-l-gray-200 dark:border-l-gray-600">
                  <div className="flex items-start gap-4">
                    {/* Field icon and basic info */}
                    <div className="flex-shrink-0 mt-1">
                      <div className={`p-2 rounded-lg ${getTypeColor(field.type)}`}>
                        {getTypeIcon(field.type)}
                      </div>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                          <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                            {field.display_name}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                            {field.name}
                          </p>
                        </div>

                        <div className="flex items-center gap-2 flex-shrink-0">
                          {field.required ? (
                            <span className="px-2 py-1 text-xs bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400 rounded">
                              Required
                            </span>
                          ) : (
                            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 rounded">
                              Optional
                            </span>
                          )}

                          <span className={`px-2 py-1 text-xs rounded font-medium ${getTypeColor(field.type)}`}>
                            {field.type}
                          </span>
                        </div>
                      </div>

                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                        {field.description}
                      </p>

                      {/* Additional field details */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400">
                        {field.example && (
                          <div>
                            <span className="font-medium">Example: </span>
                            <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">
                              {field.example}
                            </code>
                          </div>
                        )}

                        {field.format && (
                          <div>
                            <span className="font-medium">Format: </span>
                            <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">
                              {field.format}
                            </code>
                          </div>
                        )}

                        {field.max_length && (
                          <div>
                            <span className="font-medium">Max Length: </span>
                            {field.max_length}
                          </div>
                        )}

                        {field.min_length && (
                          <div>
                            <span className="font-medium">Min Length: </span>
                            {field.min_length}
                          </div>
                        )}

                        {field.pattern && (
                          <div className="md:col-span-2">
                            <span className="font-medium">Pattern: </span>
                            <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">
                              {field.pattern}
                            </code>
                          </div>
                        )}

                        {field.default_value !== undefined && (
                          <div>
                            <span className="font-medium">Default: </span>
                            <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">
                              {String(field.default_value)}
                            </code>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Showing {filteredFields.length} of {schema.fields.length} fields
            </p>
            <Button onClick={onClose} variant="outline">
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchemaViewer;