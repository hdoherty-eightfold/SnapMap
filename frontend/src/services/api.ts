/**
 * API Client Service
 * Handles all HTTP requests to backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  UploadResponse,
  EntitySchema,
  AutoMapRequest,
  AutoMapResponse,
  PreviewRequest,
  PreviewResponse,
  ValidationResult,
  ExportRequest,
  ErrorResponse,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add any request modifications here (e.g., auth tokens)
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ErrorResponse>) => {
        // Handle errors globally
        const errorMessage = error.response?.data?.error?.message || error.message;
        console.error('API Error:', errorMessage);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Upload CSV/Excel file
   */
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  /**
   * Get list of available entities
   */
  async getAvailableEntities(): Promise<{ entities: any[]; total: number }> {
    const response = await this.client.get('/entities');
    return response.data;
  }

  /**
   * Get entity schema
   */
  async getSchema(entityName: string = 'employee'): Promise<EntitySchema> {
    const response = await this.client.get<EntitySchema>(`/schema/${entityName}`);
    return response.data;
  }

  /**
   * Auto-detect entity type from source fields
   */
  async detectEntityType(sourceFields: string[]): Promise<{
    detected_entity: string;
    confidence: number;
    all_scores: Record<string, number>;
  }> {
    const response = await this.client.post('/ai/detect-entity', {
      source_fields: sourceFields,
    });
    return response.data;
  }

  /**
   * Get AI suggestions for field corrections
   */
  async getFieldSuggestions(
    sourceField: string,
    entityName: string
  ): Promise<{
    source_field: string;
    entity_name: string;
    suggestions: any[];
    total_suggestions: number;
  }> {
    const response = await this.client.post('/ai/infer-corrections', {
      source_field: sourceField,
      entity_name: entityName,
    });
    return response.data;
  }

  /**
   * Auto-map source fields to target fields
   */
  async autoMap(request: AutoMapRequest): Promise<AutoMapResponse> {
    const response = await this.client.post<AutoMapResponse>('/auto-map', request);
    return response.data;
  }

  /**
   * Preview transformation
   */
  async previewTransform(request: PreviewRequest): Promise<PreviewResponse> {
    const response = await this.client.post<PreviewResponse>('/transform/preview', request);
    return response.data;
  }

  /**
   * Validate mappings and data
   */
  async validate(request: {
    mappings: any[];
    source_data?: Record<string, any>[];
    schema_name?: string;
  }): Promise<ValidationResult> {
    const response = await this.client.post<ValidationResult>('/validate', request);
    return response.data;
  }

  /**
   * Export transformed CSV
   */
  async exportCSV(request: ExportRequest): Promise<Blob> {
    const response = await this.client.post('/transform/export', request, {
      responseType: 'blob',
    });

    return response.data;
  }

  /**
   * Download blob as file
   */
  downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export individual functions for convenience (with proper binding)
export const uploadFile = apiClient.uploadFile.bind(apiClient);
export const getAvailableEntities = apiClient.getAvailableEntities.bind(apiClient);
export const getSchema = apiClient.getSchema.bind(apiClient);
export const detectEntityType = apiClient.detectEntityType.bind(apiClient);
export const getFieldSuggestions = apiClient.getFieldSuggestions.bind(apiClient);
export const autoMap = apiClient.autoMap.bind(apiClient);
export const previewTransform = apiClient.previewTransform.bind(apiClient);
export const validate = apiClient.validate.bind(apiClient);
export const exportCSV = apiClient.exportCSV.bind(apiClient);
export const downloadBlob = apiClient.downloadBlob.bind(apiClient);
