/**
 * FieldMapping Component
 * Map source fields to target fields with auto-mapping
 */

import React, { useEffect, useState } from 'react';
import { Sparkles, ArrowRight, CheckCircle, XCircle, AlertCircle, Info, Search, Plus, Wand2, X } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { useToast } from '../../contexts/ToastContext';
import { autoMap, validate } from '../../services/api';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ConnectionLines } from './ConnectionLines';
import type { Mapping } from '../../types';

export const FieldMapping: React.FC = () => {
  // Fix for setUploadedFile undefined error
  const {
    uploadedFile,
    setUploadedFile,
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

  const { addToast } = useToast();

  const [autoMapping, setAutoMapping] = useState(false);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [showOnlyMappedOptional, setShowOnlyMappedOptional] = useState(false);
  const [showTooltip, setShowTooltip] = useState<string | null>(null);
  const [sourceSearch, setSourceSearch] = useState('');
  const [optionalSearch, setOptionalSearch] = useState('');
  const [showCreateField, setShowCreateField] = useState(false);
  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldType, setNewFieldType] = useState('string');
  const [generatedFields, setGeneratedFields] = useState<Set<string>>(new Set());

  // Field explanations and examples
  const getFieldInfo = (fieldName: string) => {
    const fieldExamples: Record<string, { description: string; examples: string[] }> = {
      userId: {
        description: "Unique identifier for the employee, typically used in HR systems as the primary key",
        examples: ["EMP001", "12345", "john.doe", "employee_123"]
      },
      firstName: {
        description: "Employee's first/given name as it appears in official records",
        examples: ["John", "Mary", "Robert", "Sarah"]
      },
      lastName: {
        description: "Employee's last/family name as it appears in official records",
        examples: ["Smith", "Johnson", "Williams", "Brown"]
      },
      email: {
        description: "Primary email address for the employee, used for communication and system access",
        examples: ["john.smith@company.com", "mary.j@corp.org", "robert.williams@firm.net"]
      },
      hireDate: {
        description: "Date when the employee was hired or started working at the company",
        examples: ["2023-01-15", "01/15/2023", "15-Jan-2023", "2023/01/15"]
      },
      title: {
        description: "Employee's job title or position within the company",
        examples: ["Software Engineer", "Marketing Manager", "Sales Representative", "HR Specialist"]
      },
      division: {
        description: "Department or business unit where the employee works",
        examples: ["Engineering", "Marketing", "Sales", "Human Resources", "Finance"]
      },
      businessPhone: {
        description: "Work phone number for contacting the employee during business hours",
        examples: ["+1-555-123-4567", "(555) 123-4567", "555.123.4567", "15551234567"]
      },
      location: {
        description: "Physical work location, office, or city where the employee is based",
        examples: ["New York, NY", "San Francisco Office", "Remote", "London HQ", "Building A, Floor 3"]
      },
      reportsTo: {
        description: "Manager's name or ID that the employee reports to in the organizational hierarchy",
        examples: ["Jane Manager", "MGR001", "john.manager@company.com", "Manager, Jane"]
      }
    };

    // Check if this is a generated field
    if (fieldName.startsWith('generated_')) {
      const originalFieldName = fieldName.replace('generated_', '');
      const targetField = schema?.fields.find(f => f.name === originalFieldName);

      if (targetField) {
        // Generate intelligent examples based on the target field name and type
        const generateExamples = (fieldName: string): string[] => {
          const lowerName = fieldName.toLowerCase();

          if (lowerName.includes('date') || lowerName.includes('time') || lowerName.includes('_ts')) {
            return ["2023-12-15", "2024-01-20", "2023-11-30", "2024-02-14"];
          } else if (lowerName.includes('id') || lowerName.includes('identifier')) {
            return ["12345", "EMP001", "USER_456", "ID789"];
          } else if (lowerName.includes('email')) {
            return ["john.doe@company.com", "jane.smith@corp.org", "employee@firm.net"];
          } else if (lowerName.includes('phone')) {
            return ["+1-555-123-4567", "(555) 987-6543", "555.123.4567"];
          } else if (lowerName.includes('name')) {
            return ["John Smith", "Jane Doe", "Robert Johnson", "Sarah Wilson"];
          } else if (lowerName.includes('salary') || lowerName.includes('pay') || lowerName.includes('wage')) {
            return ["65000", "75000", "80000", "95000"];
          } else if (lowerName.includes('status')) {
            return ["Active", "Inactive", "Pending", "Approved"];
          } else {
            return ["Sample Value 1", "Sample Value 2", "Sample Value 3", "Sample Value 4"];
          }
        };

        return {
          description: `Generated field for ${targetField.display_name || targetField.name}. This field was created to provide sample data for mapping validation.`,
          examples: generateExamples(targetField.name)
        };
      }
    }

    return fieldExamples[fieldName] || {
      description: "Field information not available for this data type",
      examples: ["Contact support for more information"]
    };
  };

  // Function to generate sample data for a field
  const generateSampleData = (targetFieldName: string, fieldType: string = 'string') => {
    const lowerName = targetFieldName.toLowerCase();

    // Smart sample data generation based on field name patterns
    if (lowerName.includes('date') || lowerName.includes('time') || lowerName.includes('_ts')) {
      return new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    } else if (lowerName.includes('id') || lowerName.includes('identifier')) {
      return `EMP${Math.floor(Math.random() * 9000) + 1000}`;
    } else if (lowerName.includes('email')) {
      const names = ['john.doe', 'jane.smith', 'bob.wilson', 'sarah.johnson'];
      const domains = ['company.com', 'corp.org', 'firm.net'];
      return `${names[Math.floor(Math.random() * names.length)]}@${domains[Math.floor(Math.random() * domains.length)]}`;
    } else if (lowerName.includes('phone')) {
      return `+1-555-${Math.floor(Math.random() * 900) + 100}-${Math.floor(Math.random() * 9000) + 1000}`;
    } else if (lowerName.includes('name')) {
      const firstNames = ['John', 'Jane', 'Robert', 'Sarah', 'Michael', 'Emily'];
      const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller'];
      return `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`;
    } else if (lowerName.includes('salary') || lowerName.includes('pay') || lowerName.includes('wage')) {
      return (Math.floor(Math.random() * 50000) + 50000).toString();
    } else if (lowerName.includes('status')) {
      const statuses = ['Active', 'Inactive', 'Pending', 'Approved', 'On Leave'];
      return statuses[Math.floor(Math.random() * statuses.length)];
    } else {
      // Fallback: get examples from field info
      const fieldInfo = getFieldInfo(targetFieldName);
      return fieldInfo.examples[0] || 'sample_value';
    }
  };

  // Function to create a new field with sample data
  const handleCreateField = () => {
    if (!newFieldName.trim()) {
      addToast('error', 'Field Name Required', 'Please enter a name for the new field.');
      return;
    }

    if (uploadedFile?.columns.includes(newFieldName)) {
      addToast('error', 'Field Already Exists', 'A field with this name already exists.');
      return;
    }

    // Add the new field to the uploaded file data
    if (uploadedFile) {
      const sampleData = generateSampleData(newFieldName, newFieldType);

      // Create new columns array with the new field
      const newColumns = [...uploadedFile.columns, newFieldName];

      // Add sample data to all rows
      const newSampleData = uploadedFile.sample_data?.map(row => ({
        ...row,
        [newFieldName]: sampleData
      })) || [];

      // Update the uploaded file with new field
      setUploadedFile({
        ...uploadedFile,
        columns: newColumns,
        sample_data: newSampleData,
        data_types: {
          ...uploadedFile.data_types,
          [newFieldName]: newFieldType
        }
      });

      setGeneratedFields(prev => new Set([...prev, newFieldName]));

      addToast('success', 'Field Created', `Created new field "${newFieldName}" with sample data.`);

      // Reset form
      setNewFieldName('');
      setNewFieldType('string');
      setShowCreateField(false);
    }
  };

  // Function to auto-populate a field with sample data
  const handleAutoPopulateField = (targetFieldName: string) => {
    const sampleData = generateSampleData(targetFieldName);
    const fieldDisplayName = schema?.fields.find(f => f.name === targetFieldName)?.display_name || targetFieldName;

    // Create a virtual source field name
    const virtualSourceName = `generated_${targetFieldName}`;

    // Add to uploaded file if not already there
    if (uploadedFile && !uploadedFile.columns.includes(virtualSourceName)) {
      const newColumns = [...uploadedFile.columns, virtualSourceName];
      const newSampleData = uploadedFile.sample_data?.map(row => ({
        ...row,
        [virtualSourceName]: sampleData
      })) || [];

      setUploadedFile({
        ...uploadedFile,
        columns: newColumns,
        sample_data: newSampleData,
        data_types: {
          ...uploadedFile.data_types,
          [virtualSourceName]: 'string'
        }
      });

      setGeneratedFields(prev => new Set([...prev, virtualSourceName]));
    }

    // Auto-map the generated field
    const mapping = {
      source: virtualSourceName,
      target: targetFieldName,
      confidence: 1.0,
      method: 'manual',
    };

    addMapping(mapping);

    addToast('success', 'Field Auto-Populated', `Generated sample data for "${fieldDisplayName}" field.`);
  };

  // Function to create a new source field for a required field
  const handleCreateRequiredField = (targetFieldName: string) => {
    const sampleData = generateSampleData(targetFieldName);
    const fieldDisplayName = schema?.fields.find(f => f.name === targetFieldName)?.display_name || targetFieldName;

    // Create a descriptive source field name based on the target field
    let sourceFieldName: string;
    if (targetFieldName.includes('last_activity')) {
      sourceFieldName = 'last_activity_timestamp';
    } else if (targetFieldName.includes('employee_id')) {
      sourceFieldName = 'employee_id';
    } else if (targetFieldName.includes('email')) {
      sourceFieldName = 'email_address';
    } else if (targetFieldName.includes('first_name')) {
      sourceFieldName = 'first_name';
    } else if (targetFieldName.includes('last_name')) {
      sourceFieldName = 'last_name';
    } else {
      // Default naming convention
      sourceFieldName = targetFieldName.toLowerCase().replace(/[^a-z0-9]/g, '_');
    }

    // Ensure field name is unique
    let uniqueFieldName = sourceFieldName;
    let counter = 1;
    while (uploadedFile?.columns.includes(uniqueFieldName) || generatedFields.has(uniqueFieldName)) {
      uniqueFieldName = `${sourceFieldName}_${counter}`;
      counter++;
    }

    // Add to uploaded file
    if (uploadedFile) {
      const newColumns = [...uploadedFile.columns, uniqueFieldName];
      const newSampleData = uploadedFile.sample_data?.map(row => ({
        ...row,
        [uniqueFieldName]: sampleData
      })) || [];

      setUploadedFile({
        ...uploadedFile,
        columns: newColumns,
        sample_data: newSampleData,
        data_types: {
          ...uploadedFile.data_types,
          [uniqueFieldName]: 'string'
        }
      });

      // Track as generated field
      setGeneratedFields(prev => new Set([...prev, uniqueFieldName]));

      // Auto-map the created field
      const mapping = {
        source: uniqueFieldName,
        target: targetFieldName,
        confidence: 1.0,
        method: 'created' as const,
      };

      addMapping(mapping);

      addToast('success', 'Required Field Created', `Created "${uniqueFieldName}" field and mapped to "${fieldDisplayName}".`);
    }
  };

  // Auto-map on component mount
  useEffect(() => {
    if (uploadedFile && schema && mappings.length === 0) {
      handleAutoMap();
    }
  }, [uploadedFile, schema]);

  // Close tooltip when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowTooltip(null);
    };

    if (showTooltip) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showTooltip]);

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
        source_data: uploadedFile?.sample_data || []
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
    // Check if all required fields are mapped
    const unmappedRequired = requiredFields.filter(f => !mappedTargets.has(f.name));

    if (unmappedRequired.length > 0) {
      addToast(
        'error',
        'Missing Required Mappings',
        `Please map the following required fields: ${unmappedRequired.map(f => f.display_name).join(', ')}`,
        5000
      );
      return;
    }

    await handleValidate();

    if (validationResults?.is_valid) {
      addToast(
        'success',
        'Validation Successful',
        'All mappings are valid. Proceeding to preview.',
        3000
      );
      nextStep();
    } else if (validationResults) {
      const errorCount = validationResults.errors.length;
      const warningCount = validationResults.warnings.length;
      addToast(
        'error',
        'Validation Failed',
        `Found ${errorCount} errors and ${warningCount} warnings. Please fix them before continuing.`,
        5000
      );
    }
  };

  if (!uploadedFile || !schema) {
    return (
      <Card padding="lg">
        <p className="text-center text-gray-600">No data available</p>
      </Card>
    );
  }

  const getMappingForTarget = (targetField: string) => {
    return mappings.find(m => m.target === targetField);
  };

  const mappedSources = new Set(mappings.map(m => m.source));
  const mappedTargets = new Set(mappings.map(m => m.target));
  const unmappedSources = uploadedFile.columns.filter(c => !mappedSources.has(c));
  const requiredFields = schema.fields.filter(f => f.required);
  const allOptionalFields = schema.fields.filter(f => !f.required);

  // Filter source fields based on search
  const filteredSourceFields = uploadedFile.columns.filter(field =>
    field.toLowerCase().includes(sourceSearch.toLowerCase())
  );

  // Filter optional fields based on search and mapped toggle
  const baseOptionalFields = showOnlyMappedOptional
    ? allOptionalFields.filter(field => getMappingForTarget(field.name))
    : allOptionalFields;

  const optionalFields = baseOptionalFields.filter(field =>
    field.display_name.toLowerCase().includes(optionalSearch.toLowerCase()) ||
    field.name.toLowerCase().includes(optionalSearch.toLowerCase())
  );

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.95) return 'text-success-600 bg-success-100';
    if (confidence >= 0.80) return 'text-warning-600 bg-warning-100';
    return 'text-gray-600 bg-gray-100';
  };

  const progress = requiredFields.filter(f => mappedTargets.has(f.name)).length;
  const progressPercentage = (progress / requiredFields.length) * 100;

  return (
    <div className="space-y-6 relative">
      {/* Auto-Mapping Loading Overlay */}
      {autoMapping && (
        <div className="absolute inset-0 bg-white/80 dark:bg-gray-900/80 z-50 flex items-center justify-center rounded-lg backdrop-blur-sm">
          <div className="text-center p-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/30 mb-4">
              <Sparkles className="w-8 h-8 text-primary-600 dark:text-primary-400 animate-pulse" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Auto-Mapping Fields
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md">
              Using AI to semantically match your source fields to Eightfold target fields...
            </p>
            <div className="mt-4">
              <LoadingSpinner size="sm" />
            </div>
          </div>
        </div>
      )}
      
      {/* Header with Auto-Map Button */}
      <div className="flex items-center justify-between px-8 pt-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Field Mapping</h2>
          <p className="text-gray-600 dark:text-gray-300 mt-1">Map your source fields to Eightfold target fields</p>
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

      {/* Mapping Interface */}
      <div className="px-8">
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
              <div className="flex items-center justify-between gap-4">
                <CardTitle>Your Source Fields</CardTitle>
                <div className="flex items-center gap-2">
                  {/* Source Search */}
                  <div className="relative">
                    <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search source fields..."
                      value={sourceSearch}
                      onChange={(e) => setSourceSearch(e.target.value)}
                      className="pl-7 pr-3 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-48"
                    />
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowCreateField(true)}
                    leftIcon={<Plus className="w-3 h-3" />}
                  >
                    Create Field
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
            <div className="grid grid-cols-3 gap-1.5">
              {filteredSourceFields.map((field) => {
                const isMapped = mappedSources.has(field);
                const isSelected = selectedSource === field;
                const mapping = mappings.find(m => m.source === field);
                const isGenerated = generatedFields.has(field);

                return (
                  <div
                    key={field}
                    data-source-field={field}
                    onClick={() => !isMapped && setSelectedSource(field)}
                    className={`
                      p-2 rounded-md border cursor-pointer transition-all text-xs
                      ${isMapped
                        ? 'border-success-400 bg-success-50 cursor-not-allowed'
                        : isSelected
                        ? 'border-primary-500 bg-primary-50'
                        : isGenerated
                        ? 'border-purple-300 bg-purple-50 hover:border-purple-400'
                        : 'border-gray-200 hover:border-primary-300'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900 truncate text-xs">{field}</span>
                      <div className="flex items-center gap-1">
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setShowTooltip(showTooltip === field ? null : field);
                            }}
                            className="w-3 h-3 text-gray-400 hover:text-gray-600 flex-shrink-0"
                            title="Field information"
                          >
                            <Info className="w-3 h-3" />
                          </button>
                          {showTooltip === field && (
                            <div className="absolute bottom-full left-0 mb-2 w-64 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
                              <div className="text-xs">
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">{field}</h4>
                                <p className="text-gray-700 dark:text-gray-300 mb-2">{getFieldInfo(field).description}</p>
                                <div>
                                  <p className="font-medium text-gray-900 dark:text-white mb-1">Examples:</p>
                                  <ul className="text-gray-600 dark:text-gray-400 space-y-0.5">
                                    {getFieldInfo(field).examples.map((example, idx) => (
                                      <li key={idx} className="font-mono bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">
                                        {example}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                        {isMapped && (
                          <>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRemoveMapping(field);
                              }}
                              className="w-3 h-3 text-red-400 hover:text-red-600 flex-shrink-0"
                              title="Remove mapping"
                            >
                              <X className="w-3 h-3" />
                            </button>
                            <CheckCircle className="w-3 h-3 text-success-600 flex-shrink-0" />
                          </>
                        )}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 mb-1">
                      {uploadedFile.data_types[field] || 'string'}
                    </div>

                    {/* Show mapping destination and confidence */}
                    {mapping && (
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-1">
                          <ArrowRight className="w-2 h-2 text-success-600 flex-shrink-0" />
                          <span className="text-xs font-medium text-success-700 truncate">
                            {schema?.fields.find(f => f.name === mapping.target)?.display_name || mapping.target}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className={`text-xs px-1 py-0.5 rounded-full inline-block ${getConfidenceColor(mapping.confidence)}`}>
                            {(mapping.confidence * 100).toFixed(0)}%
                          </span>
                          <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium inline-block ${
                            mapping.method === 'semantic' || mapping.method === 'exact' || mapping.method === 'alias' || mapping.method === 'fuzzy'
                              ? 'bg-blue-100 text-blue-700 border border-blue-200'
                              : mapping.method === 'manual'
                              ? generatedFields.has(mapping.source)
                                ? 'bg-purple-100 text-purple-700 border border-purple-200'
                                : 'bg-yellow-100 text-yellow-700 border border-yellow-200'
                              : 'bg-gray-100 text-gray-700 border border-gray-200'
                          }`}>
                            {mapping.method === 'semantic' || mapping.method === 'exact' || mapping.method === 'alias' || mapping.method === 'fuzzy'
                              ? 'AUTO'
                              : mapping.method === 'manual'
                              ? generatedFields.has(mapping.source) ? 'GENERATED' : 'MANUAL'
                              : mapping.method.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    )}
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
                <div className="grid grid-cols-1 gap-2">
                  {requiredFields.map((field) => {
                    const mapping = getMappingForTarget(field.name);

                    return (
                      <div
                        key={field.name}
                        data-target-field={field.name}
                        onClick={() => selectedSource && handleManualMap(field.name)}
                        className={`
                          p-2.5 rounded-lg border-2 transition-all
                          ${mapping
                            ? 'border-success-300 bg-success-50'
                            : selectedSource
                            ? 'border-primary-300 hover:border-primary-500 cursor-pointer'
                            : 'border-gray-200'
                          }
                        `}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-gray-900 text-sm">
                                {field.display_name}
                                <span className="text-error-600 ml-1">*</span>
                              </p>
                              <span className="text-xs text-gray-500">({field.type})</span>
                            </div>

                            {mapping && (
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs text-gray-600">← {mapping.source}</span>
                                <span className={`text-xs px-1.5 py-0.5 rounded-full ${getConfidenceColor(mapping.confidence)}`}>
                                  {(mapping.confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                            )}
                          </div>

                          <div className="flex items-center gap-1">
                            {!mapping && (
                              <>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleAutoPopulateField(field.name);
                                  }}
                                  className="text-primary-600 hover:text-primary-800 flex-shrink-0 p-1 rounded hover:bg-primary-50"
                                  title="Generate sample data for this field"
                                >
                                  <Wand2 className="w-3 h-3" />
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleCreateRequiredField(field.name);
                                  }}
                                  className="text-green-600 hover:text-green-800 flex-shrink-0 p-1 rounded hover:bg-green-50"
                                  title="Create new source field for this requirement"
                                >
                                  <Plus className="w-3 h-3" />
                                </button>
                              </>
                            )}
                            {mapping && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRemoveMapping(mapping.source);
                                }}
                                className="text-error-600 hover:text-error-800 flex-shrink-0"
                              >
                                <XCircle className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Optional Fields */}
              <div>
                <div className="flex items-center justify-between mb-3 gap-4">
                  <p className="text-sm font-semibold text-gray-700">
                    Optional Fields ({showOnlyMappedOptional ? `${optionalFields.length}/${allOptionalFields.length}` : optionalFields.length})
                  </p>
                  <div className="flex items-center gap-2">
                    {/* Optional Fields Search */}
                    <div className="relative">
                      <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search optional fields..."
                        value={optionalSearch}
                        onChange={(e) => setOptionalSearch(e.target.value)}
                        className="pl-7 pr-3 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-48"
                      />
                    </div>
                    <label className="flex items-center space-x-2 text-xs text-gray-600 cursor-pointer hover:text-gray-800 transition-colors">
                      <input
                        type="checkbox"
                        checked={showOnlyMappedOptional}
                        onChange={(e) => setShowOnlyMappedOptional(e.target.checked)}
                        className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 cursor-pointer"
                      />
                      <span>Show only mapped</span>
                    </label>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 max-h-80 overflow-y-auto pr-2">
                  {optionalFields.map((field) => {
                    const mapping = getMappingForTarget(field.name);

                    return (
                      <div
                        key={field.name}
                        data-target-field={field.name}
                        onClick={() => selectedSource && handleManualMap(field.name)}
                        className={`
                          p-2 rounded-lg border-2 transition-all
                          ${mapping
                            ? 'border-gray-300 bg-gray-50'
                            : selectedSource
                            ? 'border-primary-300 hover:border-primary-500 cursor-pointer'
                            : 'border-gray-200'
                          }
                        `}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-1">
                              <p className="font-medium text-gray-700 text-sm truncate">{field.display_name}</p>
                              <span className="text-xs text-gray-500">({field.type})</span>
                            </div>

                            {mapping && (
                              <div className="mt-1">
                                <div className="flex items-center gap-1">
                                  <span className="text-xs text-gray-600 truncate">← {mapping.source}</span>
                                </div>
                                <span className={`text-xs px-1.5 py-0.5 rounded-full inline-block mt-0.5 ${getConfidenceColor(mapping.confidence)}`}>
                                  {(mapping.confidence * 100).toFixed(0)}%
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
                              className="text-gray-600 hover:text-gray-800 flex-shrink-0"
                            >
                              <XCircle className="w-4 h-4" />
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
      </div>

      {/* Modern Floating Actions Bar */}
      <div className="sticky bottom-0 left-0 right-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-lg border-t border-gray-200 dark:border-gray-700 shadow-lg mt-8">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            {/* Status Indicator */}
            <div className="flex items-center gap-3">
              {validationResults && (
                <div className="flex items-center gap-2">
                  {validationResults.is_valid ? (
                    <>
                      <CheckCircle className="w-5 h-5 text-success-600" />
                      <span className="text-sm font-medium text-success-700">All mappings valid</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-5 h-5 text-warning-600" />
                      <span className="text-sm font-medium text-warning-700">
                        {validationResults.errors.length} errors, {validationResults.warnings.length} warnings
                      </span>
                    </>
                  )}
                </div>
              )}

              {/* Progress Indicator */}
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span className="font-medium">{progress}</span>
                <span>/</span>
                <span>{requiredFields.length}</span>
                <span>required fields mapped</span>
                <div className="w-16 h-2 bg-gray-200 rounded-full ml-2">
                  <div
                    className="h-2 bg-primary-600 rounded-full transition-all duration-300"
                    style={{ width: `${progressPercentage}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              <Button variant="outline" size="md" onClick={() => window.location.reload()}>
                Start Over
              </Button>
              <Button
                variant="primary"
                size="md"
                onClick={handleContinue}
                disabled={!mappings.length || (validationResults && !validationResults.is_valid)}
                rightIcon={<ArrowRight className="w-4 h-4" />}
                className="shadow-lg"
              >
                Preview Transformation
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Create Field Modal */}
      {showCreateField && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Create New Field</h3>
              <button
                onClick={() => setShowCreateField(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Field Name
                </label>
                <input
                  type="text"
                  value={newFieldName}
                  onChange={(e) => setNewFieldName(e.target.value)}
                  placeholder="e.g., employee_id, last_activity"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Data Type
                </label>
                <select
                  value={newFieldType}
                  onChange={(e) => setNewFieldType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="string">String</option>
                  <option value="date">Date</option>
                  <option value="datetime">DateTime</option>
                  <option value="number">Number</option>
                  <option value="email">Email</option>
                </select>
              </div>

              <div className="text-sm text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-md">
                <p className="font-medium mb-1">💡 Smart Data Generation</p>
                <p>Sample data will be automatically generated based on the field name and type.</p>
              </div>

              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  onClick={() => setShowCreateField(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleCreateField}
                  className="flex-1"
                  leftIcon={<Plus className="w-4 h-4" />}
                >
                  Create Field
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FieldMapping;
