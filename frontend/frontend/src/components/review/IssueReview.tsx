/**
 * Issue Review Component
 * AI-powered file analysis showing all detected issues and suggested fixes
 */

import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Info, XCircle, RefreshCw, FileSearch, ArrowRight, ArrowLeft } from 'lucide-react';
import axios from 'axios';
import { useApp } from '../../contexts/AppContext';
import { useToast } from '../../contexts/ToastContext';

interface Issue {
  type: string;
  severity: 'critical' | 'warning' | 'info';
  field: string;
  description: string;
  affected_rows: number | string;
}

interface Suggestion {
  issue_type: string;
  field: string;
  suggestion: string;
  target_field: string;
  confidence: number;
  auto_fixable: boolean;
}

interface ReviewData {
  file_id: string;
  entity_name: string;
  issues_found: Issue[];
  suggestions: Suggestion[];
  can_auto_fix: boolean;
  summary: string;
  total_issues: number;
  critical_issues: number;
  warnings: number;
}

const IssueReview: React.FC = () => {
  const { uploadedFile, selectedEntityType, previousStep, nextStep } = useApp();
  const toast = useToast();
  const [review, setReview] = useState<ReviewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [applyingFixes, setApplyingFixes] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (uploadedFile && selectedEntityType) {
      analyzeFile();
    }
  }, [uploadedFile, selectedEntityType]);

  const analyzeFile = async () => {
    if (!uploadedFile || !selectedEntityType) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/api/review/file', {
        file_id: uploadedFile.file_id,
        entity_name: selectedEntityType,
        include_suggestions: true
      });

      setReview(response.data);
    } catch (err: any) {
      console.error('Error analyzing file:', err);
      setError(err.response?.data?.error?.message || 'Failed to analyze file');
    } finally {
      setLoading(false);
    }
  };

  const applyAutoFixes = async () => {
    if (!uploadedFile || !selectedEntityType || !review?.can_auto_fix) return;

    setApplyingFixes(true);

    try {
      const response = await axios.post('http://localhost:8000/api/review/apply-fixes', {
        file_id: uploadedFile.file_id,
        entity_name: selectedEntityType
      });

      if (response.data.success) {
        // Show success message
        toast.success('Auto-Fixes Applied', `Successfully applied ${response.data.fixes_count} fixes!`);
        // Re-analyze the fixed file
        analyzeFile();
      }
    } catch (err: any) {
      console.error('Error applying fixes:', err);
      toast.error('Failed to Apply Fixes', err.response?.data?.error?.message || 'Unknown error');
    } finally {
      setApplyingFixes(false);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-600 dark:text-blue-400" />;
      default:
        return <Info className="w-5 h-5 text-gray-600 dark:text-gray-400" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      case 'info':
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
      default:
        return 'bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex flex-col items-center justify-center h-64 gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            <p className="text-gray-600 dark:text-gray-400">Analyzing file with AI...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="max-w-5xl mx-auto">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <XCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
              <div>
                <h3 className="font-semibold text-red-900 dark:text-red-100">Analysis Failed</h3>
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
                <button
                  onClick={analyzeFile}
                  className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!review) {
    return (
      <div className="p-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex flex-col items-center justify-center h-64 gap-4">
            <FileSearch className="w-16 h-16 text-gray-400" />
            <p className="text-gray-600 dark:text-gray-400">No file to review</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">File Review</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                AI-powered analysis of your uploaded file
              </p>
            </div>
            <button
              onClick={analyzeFile}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Re-analyze
            </button>
          </div>
        </div>

        {/* Summary Card */}
        <div className={`p-6 rounded-xl border mb-6 ${
          review.total_issues === 0
            ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
            : review.critical_issues > 0
            ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
            : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
        }`}>
          <div className="flex items-start gap-4">
            {review.total_issues === 0 ? (
              <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
            ) : (
              <AlertTriangle className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
            )}
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {review.total_issues === 0 ? 'No Issues Found!' : 'Issues Detected'}
              </h2>
              <p className="text-gray-700 dark:text-gray-300">{review.summary}</p>

              {review.total_issues > 0 && (
                <div className="mt-4 flex items-center gap-4 text-sm">
                  <span className="flex items-center gap-1">
                    <span className="font-semibold text-red-600 dark:text-red-400">{review.critical_issues}</span>
                    <span className="text-gray-600 dark:text-gray-400">Critical</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="font-semibold text-yellow-600 dark:text-yellow-400">{review.warnings}</span>
                    <span className="text-gray-600 dark:text-gray-400">Warnings</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="font-semibold text-gray-900 dark:text-white">{review.total_issues}</span>
                    <span className="text-gray-600 dark:text-gray-400">Total</span>
                  </span>
                </div>
              )}

              {review.can_auto_fix && (
                <button
                  onClick={applyAutoFixes}
                  disabled={applyingFixes}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {applyingFixes ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Applying Fixes...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Auto-Fix All Issues
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Issues List */}
        {review.issues_found.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Issues Found</h2>
            <div className="space-y-3">
              {review.issues_found.map((issue, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)}`}
                >
                  <div className="flex items-start gap-3">
                    {getSeverityIcon(issue.severity)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-gray-900 dark:text-white capitalize">
                          {issue.type.replace(/_/g, ' ')}
                        </span>
                        <span className="px-2 py-0.5 bg-gray-200 dark:bg-gray-700 text-xs rounded-full text-gray-700 dark:text-gray-300">
                          {issue.field}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{issue.description}</p>
                      {typeof issue.affected_rows === 'number' && (
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          Affects {issue.affected_rows} rows
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Suggestions */}
        {review.suggestions.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Suggested Fixes</h2>
            <div className="space-y-3">
              {review.suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900"
                >
                  <div className="flex items-start gap-3">
                    {suggestion.auto_fixable ? (
                      <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                    ) : (
                      <Info className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    )}
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {suggestion.field} → {suggestion.target_field}
                        </span>
                        <div className="flex items-center gap-2">
                          {suggestion.confidence != null && !isNaN(suggestion.confidence) && (
                            <span className="text-xs text-gray-600 dark:text-gray-400">
                              {Math.round(suggestion.confidence * 100)}% confidence
                            </span>
                          )}
                          {suggestion.auto_fixable && (
                            <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                              Auto-fixable
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{suggestion.suggestion}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center gap-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={previousStep}
            className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center gap-2 font-medium transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Upload
          </button>
          <button
            onClick={nextStep}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 font-medium transition-colors"
          >
            Continue to Field Mapping
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default IssueReview;
