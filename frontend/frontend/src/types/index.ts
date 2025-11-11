/**
 * Type definitions for SnapMap Frontend
 * Based on API_CONTRACTS.md
 */

// Common types
export type DataType = "string" | "number" | "date" | "email" | "datetime" | "boolean";
export type MatchMethod = "exact" | "alias" | "fuzzy";
export type Severity = "error" | "warning" | "info";

// Field Definition
export interface FieldDefinition {
  name: string;
  display_name: string;
  type: DataType;
  required: boolean;
  max_length?: number;
  min_length?: number;
  pattern?: string;
  format?: string;
  example: string;
  description: string;
  default_value?: any;
}

// Mapping
export interface Mapping {
  source: string;
  target: string;
  confidence: number;
  method: MatchMethod;
  alternatives?: Alternative[];
}

export interface Alternative {
  target: string;
  confidence: number;
}

// Schema
export interface EntitySchema {
  entity_name: string;
  display_name: string;
  description: string;
  fields: FieldDefinition[];
}

// Validation
export interface ValidationMessage {
  field: string;
  message: string;
  severity: Severity;
  row_number?: number;
  suggestion?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: ValidationMessage[];
  warnings: ValidationMessage[];
  info: ValidationMessage[];
  summary: ValidationSummary;
}

export interface ValidationSummary {
  total_errors: number;
  total_warnings: number;
  required_fields_mapped: number;
  required_fields_total: number;
  mapping_completeness: number;
}

// Upload
export interface UploadResponse {
  filename: string;
  file_id: string;
  row_count: number;
  column_count: number;
  columns: string[];
  sample_data: Record<string, any>[];
  data_types: Record<string, string>;
  file_size: number;
}

// Auto-map
export interface AutoMapRequest {
  source_fields: string[];
  target_schema?: string;
  min_confidence?: number;
}

export interface AutoMapResponse {
  mappings: Mapping[];
  total_mapped: number;
  total_source: number;
  total_target: number;
  mapping_percentage: number;
  unmapped_source: string[];
  unmapped_target: string[];
}

// Transform
export interface PreviewRequest {
  mappings: Mapping[];
  source_data: Record<string, any>[];
  sample_size?: number;
}

export interface PreviewResponse {
  transformed_data: Record<string, any>[];
  transformations_applied: string[];
  row_count: number;
  warnings: string[];
}

// Export
export interface ExportRequest {
  mappings: Mapping[];
  source_data: Record<string, any>[];
  output_filename?: string;
}

// Error Response
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
  };
  status: number;
}

// App Context State
export interface AppState {
  uploadedFile: UploadResponse | null;
  schema: EntitySchema | null;
  mappings: Mapping[];
  transformedData: Record<string, any>[];
  validationResults: ValidationResult | null;
  currentStep: number;
}
