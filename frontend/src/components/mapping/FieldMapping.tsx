/**
 * FieldMapping Component
 * Map source fields to target fields with auto-mapping
 */

import React, { useEffect, useState } from 'react';
import { Sparkles, ArrowRight, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { autoMap, validate } from '../../services/api';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ConnectionLines } from './ConnectionLines';
import type { Mapping } from '../../types';

export const FieldMapping: React.FC = () => {
  const {
    uploadedFile,
    schema,
    mappings,
    setMappings,
    addMapping,
    removeMapping,
    validationResults,
    setValidationResults,
    nextStep,
    setIsLoading,
    isLoading,
  } = useApp();

  const [autoMapping, setAutoMapping] = useState(false);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);

  // Auto-map on component mount
  useEffect(() => {
    if (uploadedFile && schema && mappings.length === 0) {
      handleAutoMap();
    }
  }, [uploadedFile, schema]);

  const handleAutoMap = async () => {
    if (!uploadedFile || !schema) return;

    try {
      setAutoMapping(true);
      const response = await autoMap({
        source_fields: uploadedFile.columns,
        target_schema: 'employee',
        min_confidence: 0.70,
      });

      setMappings(response.mappings);

      // Validate after auto-mapping
      await handleValidate(response.mappings);
    } catch (error) {
      console.error('Auto-map error:', error);
    } finally {
      setAutoMapping(false);
    }
  };

  const handleValidate = async (currentMappings?: Mapping[]) => {
    const mappingsToValidate = currentMappings || mappings;

    if (!schema || mappingsToValidate.length === 0) return;

    try {
      const result = await validate({
        mappings: mappingsToValidate,
        schema_name: 'employee',
      });

      setValidationResults(result);
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  const handleManualMap = (targetField: string) => {
    if (!selectedSource) return;

    const mapping: Mapping = {
      source: selectedSource,
      target: targetField,
      confidence: 1.0,
      method: 'manual',
    };

    addMapping(mapping);
    setSelectedSource(null);

    // Re-validate
    handleValidate([...mappings.filter(m => m.source !== selectedSource), mapping]);
  };

  const handleRemoveMapping = (sourceField: string) => {
    removeMapping(sourceField);
    handleValidate(mappings.filter(m => m.source !== sourceField));
  };

  const handleContinue = async () => {
    await handleValidate();

    if (validationResults?.is_valid) {
      nextStep();
    }
  };

  if (!uploadedFile || !schema) {
    return (
      <Card padding="lg">
        <p className="text-center text-gray-600">No data available</p>
      </Card>
    );
  }

  const mappedSources = new Set(mappings.map(m => m.source));
  const mappedTargets = new Set(mappings.map(m => m.target));
  const unmappedSources = uploadedFile.columns.filter(c => !mappedSources.has(c));
  const requiredFields = schema.fields.filter(f => f.required);
  const optionalFields = schema.fields.filter(f => !f.required);

  const getMappingForTarget = (targetField: string) => {
    return mappings.find(m => m.target === targetField);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.95) return 'text-success-600 bg-success-100';
    if (confidence >= 0.80) return 'text-warning-600 bg-warning-100';
    return 'text-gray-600 bg-gray-100';
  };

  const progress = requiredFields.filter(f => mappedTargets.has(f.name) || f.name === 'LAST_ACTIVITY_TS').length;
  const progressPercentage = (progress / requiredFields.length) * 100;

  return (
    <div className="space-y-6">
      {/* Header with Auto-Map Button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Field Mapping</h2>
          <p className="text-gray-600 mt-1">Map your source fields to Eightfold target fields</p>
        </div>
        <Button
          variant="primary"
          size="lg"
          onClick={handleAutoMap}
          isLoading={autoMapping}
          leftIcon={<Sparkles className="w-4 h-4" />}
        >
          Auto-Map Fields
        </Button>
      </div>

      {/* Progress Bar */}
      <Card>
        <CardContent>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Required Fields Mapped: {progress} / {requiredFields.length}
            </span>
            <span className="text-sm font-semibold text-primary-600">
              {progressPercentage.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-primary-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Mapping Interface */}
      <div className="relative">
        {/* Connection Lines Overlay */}
        <ConnectionLines
          mappings={mappings}
          sourceFields={uploadedFile.columns}
          targetFields={schema.fields.map((f) => f.name)}
        />

        <div className="grid grid-cols-2 gap-6">
          {/* Source Fields */}
          <Card>
          <CardHeader>
            <CardTitle>Your Source Fields</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {uploadedFile.columns.map((field) => {
                const isMapped = mappedSources.has(field);
                const isSelected = selectedSource === field;

                return (
                  <div
                    key={field}
                    data-source-field={field}
                    onClick={() => !isMapped && setSelectedSource(field)}
                    className={`
                      p-3 rounded-lg border-2 cursor-pointer transition-all
                      ${isMapped
                        ? 'border-success-300 bg-success-50 cursor-not-allowed'
                        : isSelected
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-primary-300'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{field}</p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {uploadedFile.data_types[field] || 'string'}
                        </p>
                      </div>
                      {isMapped && (
                        <CheckCircle className="w-5 h-5 text-success-600" />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Target Fields */}
        <Card>
          <CardHeader>
            <CardTitle>Eightfold Target Fields</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Required Fields */}
              <div>
                <p className="text-sm font-semibold text-gray-700 mb-2">Required Fields</p>
                <div className="space-y-2">
                  {requiredFields.map((field) => {
                    const mapping = getMappingForTarget(field.name);

                    return (
                      <div
                        key={field.name}
                        data-target-field={field.name}
                        onClick={() => selectedSource && handleManualMap(field.name)}
                        className={`
                          p-3 rounded-lg border-2 transition-all
                          ${mapping
                            ? 'border-success-300 bg-success-50'
                            : selectedSource
                            ? 'border-primary-300 hover:border-primary-500 cursor-pointer'
                            : 'border-gray-200'
                          }
                        `}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">
                              {field.display_name}
                              <span className="text-error-600 ml-1">*</span>
                            </p>
                            <p className="text-xs text-gray-500 mt-0.5">{field.type}</p>

                            {mapping && (
                              <div className="flex items-center gap-2 mt-2">
                                <span className="text-xs text-gray-600">← {mapping.source}</span>
                                <span className={`text-xs px-2 py-0.5 rounded-full ${getConfidenceColor(mapping.confidence)}`}>
                                  {(mapping.confidence * 100).toFixed(0)}% {mapping.method}
                                </span>
                              </div>
                            )}
                          </div>

                          {mapping ? (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRemoveMapping(mapping.source);
                              }}
                              className="ml-2 text-error-600 hover:text-error-800"
                            >
                              <XCircle className="w-5 h-5" />
                            </button>
                          ) : (
                            <div className="w-5" />
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Optional Fields */}
              <div>
                <p className="text-sm font-semibold text-gray-700 mb-2">Optional Fields</p>
                <div className="space-y-2">
                  {optionalFields.slice(0, 5).map((field) => {
                    const mapping = getMappingForTarget(field.name);

                    return (
                      <div
                        key={field.name}
                        data-target-field={field.name}
                        onClick={() => selectedSource && handleManualMap(field.name)}
                        className={`
                          p-3 rounded-lg border-2 transition-all
                          ${mapping
                            ? 'border-gray-300 bg-gray-50'
                            : selectedSource
                            ? 'border-primary-300 hover:border-primary-500 cursor-pointer'
                            : 'border-gray-200'
                          }
                        `}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-700">{field.display_name}</p>
                            <p className="text-xs text-gray-500 mt-0.5">{field.type}</p>

                            {mapping && (
                              <div className="flex items-center gap-2 mt-2">
                                <span className="text-xs text-gray-600">← {mapping.source}</span>
                                <span className={`text-xs px-2 py-0.5 rounded-full ${getConfidenceColor(mapping.confidence)}`}>
                                  {(mapping.confidence * 100).toFixed(0)}% {mapping.method}
                                </span>
                              </div>
                            )}
                          </div>

                          {mapping && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRemoveMapping(mapping.source);
                              }}
                              className="ml-2 text-gray-600 hover:text-gray-800"
                            >
                              <XCircle className="w-5 h-5" />
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      </div>

      {/* Validation Results */}
      {validationResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {validationResults.is_valid ? (
                <>
                  <CheckCircle className="w-5 h-5 text-success-600" />
                  <span className="text-success-700">Validation Passed</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-5 h-5 text-warning-600" />
                  <span className="text-warning-700">Validation Issues</span>
                </>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {validationResults.errors.map((error, index) => (
                <div key={index} className="flex items-start gap-2 text-sm text-error-700">
                  <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-medium">{error.field}:</span> {error.message}
                  </div>
                </div>
              ))}
              {validationResults.warnings.map((warning, index) => (
                <div key={index} className="flex items-start gap-2 text-sm text-warning-700">
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-medium">{warning.field}:</span> {warning.message}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => window.location.reload()}>
          Start Over
        </Button>
        <Button
          variant="primary"
          size="lg"
          onClick={handleContinue}
          disabled={!validationResults?.is_valid}
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          Preview Transformation
        </Button>
      </div>
    </div>
  );
};

export default FieldMapping;
