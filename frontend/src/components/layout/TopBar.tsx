/**
 * Modern Top Bar Component
 * Provides context and actions for the current view
 * With Dark Mode Support
 */

import React from 'react';
import { useApp } from '../../contexts/AppContext';

const stepTitles = [
  'Upload Your Data',
  'Map Your Fields',
  'Preview Transformation',
  'Export Results'
];

const stepDescriptions = [
  'Upload CSV or Excel files from any HR system or flat file source',
  'Automatically map fields to Eightfold format with AI-powered suggestions',
  'Review transformations and validate data quality before export',
  'Download your standardized Eightfold integration file'
];

export const TopBar: React.FC = () => {
  const { currentStep, uploadedFile, mappings } = useApp();

  const getStepStats = () => {
    switch (currentStep) {
      case 0:
        return uploadedFile
          ? `${uploadedFile.row_count.toLocaleString()} rows loaded`
          : 'No file uploaded';
      case 1:
        return mappings.length > 0
          ? `${mappings.length} fields mapped`
          : 'No mappings yet';
      case 2:
      case 3:
        return mappings.length > 0
          ? `${mappings.length} fields ready`
          : 'Waiting for mappings';
      default:
        return '';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10 transition-colors">
      <div className="px-8 py-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
              <span>Workflow</span>
              <span>›</span>
              <span className="text-gray-900 dark:text-white font-medium">
                Step {currentStep + 1} of 4
              </span>
            </div>

            {/* Title */}
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {stepTitles[currentStep]}
            </h2>

            {/* Description */}
            <p className="text-gray-600 dark:text-gray-300 max-w-2xl">
              {stepDescriptions[currentStep]}
            </p>
          </div>

          {/* Stats Badge */}
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Status</div>
              <div className="text-sm font-semibold text-gray-900 dark:text-white">
                {getStepStats()}
              </div>
            </div>

            {/* Help Button */}
            <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-500 transition-all duration-500"
                style={{ width: `${((currentStep + 1) / 4) * 100}%` }}
              />
            </div>
            <span className="text-xs font-medium text-gray-600 dark:text-gray-300 min-w-[3rem] text-right">
              {Math.round(((currentStep + 1) / 4) * 100)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
