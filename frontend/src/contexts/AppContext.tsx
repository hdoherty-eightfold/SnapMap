/**
 * Application Context
 * Manages global state for the SnapMap application
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type {
  UploadResponse,
  EntitySchema,
  Mapping,
  ValidationResult,
} from '../types';

interface AppState {
  // Upload state
  uploadedFile: UploadResponse | null;
  setUploadedFile: (file: UploadResponse | null) => void;

  // Entity type state
  selectedEntityType: string;
  setSelectedEntityType: (entityType: string) => void;

  // Schema state
  schema: EntitySchema | null;
  setSchema: (schema: EntitySchema | null) => void;

  // Mapping state
  mappings: Mapping[];
  setMappings: (mappings: Mapping[]) => void;
  addMapping: (mapping: Mapping) => void;
  removeMapping: (sourceField: string) => void;

  // Validation state
  validationResults: ValidationResult | null;
  setValidationResults: (results: ValidationResult | null) => void;

  // Workflow state
  currentStep: number;
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  previousStep: () => void;

  // UI state
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
  isSidebarCollapsed: boolean;
  setIsSidebarCollapsed: (collapsed: boolean) => void;

  // Reset
  resetAll: () => void;
}

const AppContext = createContext<AppState | undefined>(undefined);

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  // Upload state
  const [uploadedFile, setUploadedFile] = useState<UploadResponse | null>(null);

  // Entity type state (default to employee)
  const [selectedEntityType, setSelectedEntityType] = useState<string>('employee');

  // Schema state
  const [schema, setSchema] = useState<EntitySchema | null>(null);

  // Mapping state
  const [mappings, setMappings] = useState<Mapping[]>([]);

  // Validation state
  const [validationResults, setValidationResults] = useState<ValidationResult | null>(null);

  // Workflow state (0: upload, 1: review, 2: mapping, 3: preview CSV, 4: preview XML, 5: SFTP, 6: settings)
  const [currentStep, setCurrentStep] = useState<number>(0);

  // UI state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);

  // Helper functions
  const addMapping = (mapping: Mapping) => {
    setMappings((prev) => {
      // Remove any existing mapping for the same source field
      const filtered = prev.filter((m) => m.source !== mapping.source);
      return [...filtered, mapping];
    });
  };

  const removeMapping = (sourceField: string) => {
    setMappings((prev) => prev.filter((m) => m.source !== sourceField));
  };

  const nextStep = () => {
    setCurrentStep((prev) => Math.min(prev + 1, 6));
  };

  const previousStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  };

  const resetAll = () => {
    setUploadedFile(null);
    setSelectedEntityType('employee');
    setSchema(null);
    setMappings([]);
    setValidationResults(null);
    setCurrentStep(0);
    setIsLoading(false);
    setError(null);
  };

  const value: AppState = {
    // Upload
    uploadedFile,
    setUploadedFile,

    // Entity type
    selectedEntityType,
    setSelectedEntityType,

    // Schema
    schema,
    setSchema,

    // Mappings
    mappings,
    setMappings,
    addMapping,
    removeMapping,

    // Validation
    validationResults,
    setValidationResults,

    // Workflow
    currentStep,
    setCurrentStep,
    nextStep,
    previousStep,

    // UI
    isLoading,
    setIsLoading,
    error,
    setError,
    isSidebarCollapsed,
    setIsSidebarCollapsed,

    // Reset
    resetAll,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

/**
 * Hook to use App Context
 * Must be used within AppProvider
 */
export const useApp = (): AppState => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

export default AppContext;
