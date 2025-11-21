/**
 * Extract Skills Component - Step 2
 * Extracts skills from chosen data source (CSV, API, SFTP)
 */

import React, { useState, useEffect } from 'react';
import {
  Search, FileText, Server, HardDrive, CheckCircle, AlertCircle,
  Download, Clock, Users, RefreshCw, Filter, Eye, ArrowRight,
  Database, Zap, Activity, X, Code, Trash2, Save, Upload,
  ChevronLeft, ChevronRight
} from 'lucide-react';
import { useApp, type Skill } from '../../contexts/AppContext';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../../contexts/ToastContext';
import { cn } from '../../utils/cn';
import api from '../../utils/api';

interface RoleInfo {
  id: string;
  title: string;
  description?: string;
}

interface ExtractedSkillsResponse {
  skills: Skill[];
  total_count: number;
  extraction_source: 'csv' | 'api' | 'sftp';
  extraction_time: string;
  source_info: {
    filename?: string;
    endpoint?: string;
    environment?: string;
    total_roles?: number;
    unique_skills?: number;
  };
  roles?: RoleInfo[];
}

interface RequestResponseLog {
  request: {
    endpoint: string;
    method: string;
    payload: any;
    timestamp: string;
  };
  response?: {
    status: number;
    data: any;
    timestamp: string;
  };
  error?: {
    message: string;
    details: any;
    timestamp: string;
  };
}

export const ExtractSkills: React.FC = () => {
  const {
    skillsState,
    updateSkillsState,
    nextStep,
    setIsLoading,
    setError,
    isLoading,
    error,
    autoAdvanceEnabled,
    currentStep,
    getStepName
  } = useApp();
  const { success } = useToast();

  // Clear global error when component mounts (entering this page)
  useEffect(() => {
    setError(null);
  }, [setError]);

  // Local state
  const [searchTerm, setSearchTerm] = useState('');
  const [showSkillsList, setShowSkillsList] = useState(false);
  const [filteredSkills, setFilteredSkills] = useState<Skill[]>([]);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Request/Response debugging
  const [showDebugModal, setShowDebugModal] = useState(false);
  const [requestResponseLog, setRequestResponseLog] = useState<RequestResponseLog | null>(null);
  const [loadedFromCache, setLoadedFromCache] = useState(false);

  // Skills configuration management
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [configName, setConfigName] = useState('');
  const [configDescription, setConfigDescription] = useState('');
  const [savedConfigs, setSavedConfigs] = useState<any[]>([]);

  // Integration source info from Step 1
  const [sourceType, setSourceType] = useState<'csv' | 'api' | 'sftp' | null>(null);
  const [sourceInfo, setSourceInfo] = useState<any>(null);

  // Load integration source from localStorage
  useEffect(() => {
    const integrationType = localStorage.getItem('profstudio_integration_type') as 'csv' | 'api' | 'sftp';
    setSourceType(integrationType);

    // Load source-specific info
    if (integrationType === 'csv') {
      setSourceInfo({
        filename: localStorage.getItem('profstudio_csv_filename'),
        fileId: localStorage.getItem('profstudio_csv_file_id'),
      });
    } else if (integrationType === 'api') {
      setSourceInfo({
        environmentId: localStorage.getItem('profstudio_env_id'),
        environmentKey: localStorage.getItem('profstudio_env_key'),
        username: localStorage.getItem('profstudio_username'),
        authToken: localStorage.getItem('profstudio_auth_token'),
        sessionId: localStorage.getItem('profstudio_session_id'),
      });
      
      // Check for cached API results for this environment
      const cacheKey = `profstudio_skills_cache_${localStorage.getItem('profstudio_env_id')}`;
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        try {
          const cachedData = JSON.parse(cached);
          const cacheAge = Date.now() - new Date(cachedData.cached_at).getTime();
          const cacheValidFor = 24 * 60 * 60 * 1000; // 24 hours
          
          if (cacheAge < cacheValidFor) {
            // Load from cache
            updateSkillsState({
              skills: cachedData.skills,
              totalCount: cachedData.total_count,
              extractionStatus: 'success',
              extractionSource: 'api',
              extractionError: null,
              extractedAt: cachedData.extraction_time,
            });
            localStorage.setItem('extractedSkills', JSON.stringify(cachedData.skills));
            localStorage.setItem('skillsExtractionComplete', 'true');

            // Also restore roles if available in cache
            if (cachedData.roles && cachedData.roles.length > 0) {
              const skillsExtractionData = {
                skills: cachedData.skills,
                roles: cachedData.roles,
                source_info: cachedData.source_info,
                extraction_time: cachedData.extraction_time
              };
              localStorage.setItem('skillsExtractionData', JSON.stringify(skillsExtractionData));
            }

            setLoadedFromCache(true);
          }
        } catch (err) {
          console.error('Failed to load cached skills:', err);
        }
      }
    } else if (integrationType === 'sftp') {
      setSourceInfo({
        filename: localStorage.getItem('profstudio_sftp_filename'),
        fileId: localStorage.getItem('profstudio_sftp_file_id'),
        host: localStorage.getItem('profstudio_sftp_host'),
      });
    }
  }, []);

  // Filter skills based on search term
  useEffect(() => {
    if (!searchTerm) {
      setFilteredSkills(skillsState.skills);
    } else {
      const filtered = skillsState.skills.filter(skill =>
        skill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        skill.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        skill.category?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredSkills(filtered);
    }
    // Reset to page 1 when search term changes
    setCurrentPage(1);
  }, [searchTerm, skillsState.skills]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredSkills.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedSkills = filteredSkills.slice(startIndex, endIndex);

  // Pagination handlers
  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const handleExtractSkills = async () => {
    if (!sourceType) {
      setError('No data source selected. Please go back to Step 1.');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      updateSkillsState({
        extractionStatus: 'extracting',
        extractionError: null
      });

      let endpoint = '';
      let payload = {};

      switch (sourceType) {
        case 'csv':
          endpoint = '/api/skills/extract/csv';
          payload = {
            file_id: sourceInfo?.fileId,
            filename: sourceInfo?.filename,
          };
          break;
        case 'api':
          endpoint = '/api/skills/extract/api';
          payload = {
            environment_id: sourceInfo?.environmentId,
            session_id: sourceInfo?.sessionId,
            auth_token: sourceInfo?.authToken,
          };
          break;
        case 'sftp':
          endpoint = '/api/skills/extract/sftp';
          payload = {
            file_id: sourceInfo?.fileId,
            filename: sourceInfo?.filename,
            host: sourceInfo?.host,
          };
          break;
      }

      // Log request
      const requestLog = {
        endpoint,
        method: 'POST',
        payload,
        timestamp: new Date().toISOString()
      };

      setRequestResponseLog({
        request: requestLog
      });

      const response = await api.post(endpoint, payload);
      const data: ExtractedSkillsResponse = response.data;

      // Log successful response
      setRequestResponseLog(prev => ({
        ...prev!,
        response: {
          status: response.status,
          data: response.data,
          timestamp: new Date().toISOString()
        }
      }));

      // Update skills state
      updateSkillsState({
        skills: data.skills,
        totalCount: data.total_count,
        extractionStatus: 'success',
        extractionSource: data.extraction_source,
        extractionError: null,
        extractedAt: data.extraction_time,
      });

      // Store skills for next step
      localStorage.setItem('extractedSkills', JSON.stringify(data.skills));
      localStorage.setItem('skillsExtractionComplete', 'true');

      // Store roles if available (for export modal in Review page)
      if (data.roles && data.roles.length > 0) {
        const skillsExtractionData = {
          skills: data.skills,
          roles: data.roles,
          source_info: data.source_info,
          extraction_time: data.extraction_time
        };
        localStorage.setItem('skillsExtractionData', JSON.stringify(skillsExtractionData));
      }

      // Cache API results for this environment (if API extraction)
      if (sourceType === 'api' && sourceInfo?.environmentId) {
        const cacheKey = `profstudio_skills_cache_${sourceInfo.environmentId}`;
        const cacheData = {
          skills: data.skills,
          total_count: data.total_count,
          extraction_source: data.extraction_source,
          extraction_time: data.extraction_time,
          source_info: data.source_info,
          roles: data.roles,
          cached_at: new Date().toISOString()
        };
        localStorage.setItem(cacheKey, JSON.stringify(cacheData));
      }

      // Auto-advance is DISABLED for Configure step (step 3)
      // Users need to review and configure proficiency levels, LLM settings, and prompts
      // This is a critical configuration step that requires user attention
      // Auto-advance would skip over important configuration options
      const shouldAutoAdvance = false; // Disabled to prevent skipping Configure page

      if (autoAdvanceEnabled && shouldAutoAdvance) {
        // Show completion notification
        success(
          `${getStepName(currentStep)} Completed!`,
          `Successfully extracted ${data.total_count} skills. Proceeding to ${getStepName(currentStep + 1)}...`
        );

        setTimeout(() => {
          nextStep();
        }, 2000);
      }

    } catch (err: any) {
      console.error('Skills extraction error:', err);
      
      // Log error response
      setRequestResponseLog(prev => ({
        ...prev!,
        error: {
          message: err.response?.data?.detail || err.message || 'Unknown error',
          details: {
            status: err.response?.status,
            statusText: err.response?.statusText,
            data: err.response?.data,
            headers: err.response?.headers
          },
          timestamp: new Date().toISOString()
        }
      }));
      
      updateSkillsState({
        extractionStatus: 'error',
        extractionError: err.response?.data?.detail || 'Failed to extract skills'
      });
      setError(err.response?.data?.detail || 'Error extracting skills. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const exportSkills = async () => {
    try {
      setIsLoading(true);
      const response = await api.post('/api/skills/export', {
        skills: skillsState.skills,
        format: 'csv',
      });

      // Download the file
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `extracted_skills_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError('Error exporting skills: ' + (err.response?.data?.detail || 'Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  // Save skills configuration to localStorage
  const saveSkillsConfig = () => {
    if (!configName.trim()) {
      setError('Please provide a configuration name');
      return;
    }

    const config = {
      id: Date.now().toString(),
      name: configName,
      description: configDescription,
      skills: skillsState.skills,
      sourceType,
      sourceInfo,
      totalCount: skillsState.totalCount,
      extractedAt: new Date().toISOString(),
    };

    // Get existing configs
    const existing = localStorage.getItem('profstudio_skills_configs');
    const configs = existing ? JSON.parse(existing) : [];

    // Add new config
    configs.push(config);
    localStorage.setItem('profstudio_skills_configs', JSON.stringify(configs));

    success(`Skills configuration "${configName}" saved successfully`);
    setShowSaveModal(false);
    setConfigName('');
    setConfigDescription('');
    loadSavedConfigs();
  };

  // Load saved configurations
  const loadSavedConfigs = () => {
    const existing = localStorage.getItem('profstudio_skills_configs');
    if (existing) {
      setSavedConfigs(JSON.parse(existing));
    }
  };

  // Load a specific configuration
  const loadSkillsConfig = (config: any) => {
    updateSkillsState({
      skills: config.skills,
      totalCount: config.totalCount,
      extractionStatus: 'completed',
      extractionSource: config.sourceType,
      extractionError: null,
      extractedAt: config.extractedAt,
    });

    // Store in localStorage for persistence
    localStorage.setItem('extractedSkills', JSON.stringify(config.skills));
    localStorage.setItem('skillsExtractionComplete', 'true');

    success(`Loaded "${config.name}" configuration with ${config.totalCount} skills`);
    setShowLoadModal(false);
  };

  // Delete a configuration
  const deleteSkillsConfig = (configId: string) => {
    const existing = localStorage.getItem('profstudio_skills_configs');
    if (existing) {
      const configs = JSON.parse(existing);
      const filtered = configs.filter((c: any) => c.id !== configId);
      localStorage.setItem('profstudio_skills_configs', JSON.stringify(filtered));
      setSavedConfigs(filtered);
      success('Configuration deleted');
    }
  };

  // Load saved configs on mount
  useEffect(() => {
    loadSavedConfigs();
  }, []);

  const getSourceIcon = () => {
    switch (sourceType) {
      case 'csv': return <FileText className="w-5 h-5" />;
      case 'api': return <Server className="w-5 h-5" />;
      case 'sftp': return <HardDrive className="w-5 h-5" />;
      default: return <Database className="w-5 h-5" />;
    }
  };

  const getSourceLabel = () => {
    switch (sourceType) {
      case 'csv': return 'CSV Upload';
      case 'api': return 'API Connection';
      case 'sftp': return 'SFTP Server';
      default: return 'Unknown Source';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-8">
      <Card padding="lg">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-green-100 to-teal-100 dark:from-green-900/30 dark:to-teal-900/30 mb-4">
            <Zap className="w-8 h-8 text-green-600 dark:text-green-400" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Extract Skills
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            Extract unique skills from your selected data source
          </p>
        </div>

        {/* Data Source Info */}
        <div className="mb-8 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getSourceIcon()}
              <div>
                <p className="font-semibold text-gray-900 dark:text-white">
                  Data Source: {getSourceLabel()}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {sourceType === 'csv' && sourceInfo?.filename && `File: ${sourceInfo.filename}`}
                  {sourceType === 'api' && sourceInfo?.environmentKey && `Environment: ${sourceInfo.environmentKey}`}
                  {sourceType === 'sftp' && sourceInfo?.filename && `File: ${sourceInfo.filename} from ${sourceInfo.host}`}
                </p>
              </div>
            </div>
            {skillsState.extractionStatus === 'success' && (
              <div className="flex items-center gap-2 text-sm text-success-600 dark:text-success-400">
                <CheckCircle className="w-4 h-4" />
                <span>Extracted {skillsState.totalCount} skills</span>
              </div>
            )}
          </div>
        </div>

        {/* Skills Count Display */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800">
            <div className="p-6 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 mb-3">
                <Database className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                {skillsState.totalCount}
              </p>
              <p className="text-sm text-blue-700 dark:text-blue-300">Total Skills</p>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 border-orange-200 dark:border-orange-800">
            <div className="p-6 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-900/30 mb-3">
                <Users className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
              <p className="text-2xl font-bold text-orange-900 dark:text-orange-100">
                {(() => {
                  const skillsExtractionData = localStorage.getItem('skillsExtractionData');
                  if (skillsExtractionData) {
                    try {
                      const data = JSON.parse(skillsExtractionData);
                      return data.roles?.length || 0;
                    } catch {
                      return 0;
                    }
                  }
                  return 0;
                })()}
              </p>
              <p className="text-sm text-orange-700 dark:text-orange-300">Roles</p>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 border-green-200 dark:border-green-800">
            <div className="p-6 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 mb-3">
                {isLoading || skillsState.extractionStatus === 'extracting' ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <Activity className="w-6 h-6 text-green-600 dark:text-green-400" />
                )}
              </div>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                {skillsState.extractionStatus === 'success' ? 'Ready' :
                 skillsState.extractionStatus === 'extracting' || isLoading ? 'Processing' :
                 skillsState.extractionStatus === 'error' ? 'Error' : 'Pending'}
              </p>
              <p className="text-sm text-green-700 dark:text-green-300">Status</p>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200 dark:border-purple-800">
            <div className="p-6 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 mb-3">
                <Clock className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                {skillsState.extractedAt ? new Date(skillsState.extractedAt).toLocaleDateString() : '--'}
              </p>
              <p className="text-sm text-purple-700 dark:text-purple-300">Last Extracted</p>
            </div>
          </Card>
        </div>

        {/* Action Buttons */}
        {skillsState.extractionStatus !== 'success' && (
          <div className="flex justify-center mb-8">
            <Button
              variant="primary"
              size="lg"
              onClick={handleExtractSkills}
              disabled={isLoading || !sourceType}
              className="bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 px-8"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Extracting Skills...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Extract Skills
                </>
              )}
            </Button>
          </div>
        )}

        {/* Success State */}
        {skillsState.extractionStatus === 'success' && (
          <div className="space-y-6 relative">
            {/* Loading overlay when re-extracting */}
            {isLoading && (
              <div className="absolute inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-10 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <LoadingSpinner size="lg" />
                  <p className="mt-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Re-extracting skills...
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Please wait while we fetch the latest data
                  </p>
                </div>
              </div>
            )}

            {/* Success Message */}
            <div className="p-4 bg-success-50 dark:bg-success-900/20 border-2 border-success-200 dark:border-success-800 rounded-lg">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-success-600 dark:text-success-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <p className="font-semibold text-success-900 dark:text-success-100">
                      Skills Extracted Successfully!
                    </p>
                    {loadedFromCache && (
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-xs font-semibold flex items-center gap-1">
                        <Zap className="w-3 h-3" />
                        Loaded from cache
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-success-700 dark:text-success-300">
                    Found {skillsState.totalCount} unique skills from {getSourceLabel()}.
                    {loadedFromCache 
                      ? ' No API call was needed - using cached results from your last extraction.' 
                      : ' You can review them below or proceed to configure proficiency levels.'}
                  </p>
                </div>
              </div>
            </div>

            {/* Skills Actions */}
            <div className="flex flex-wrap items-center gap-3">
              <Button
                variant="outline"
                size="md"
                onClick={() => setShowSkillsList(!showSkillsList)}
                className="border-gray-300 dark:border-gray-600"
              >
                <Eye className="w-4 h-4" />
                {showSkillsList ? 'Hide' : 'View'} Skills List
              </Button>

              <Button
                variant="outline"
                size="md"
                onClick={exportSkills}
                disabled={isLoading}
                className="border-gray-300 dark:border-gray-600"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </Button>

              <Button
                variant="outline"
                size="md"
                onClick={() => setShowSaveModal(true)}
                disabled={isLoading}
                className="border-blue-300 dark:border-blue-600 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20"
              >
                <Save className="w-4 h-4" />
                Save Config
              </Button>

              <Button
                variant="outline"
                size="md"
                onClick={() => {
                  loadSavedConfigs();
                  setShowLoadModal(true);
                }}
                disabled={isLoading}
                className="border-purple-300 dark:border-purple-600 text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20"
              >
                <Upload className="w-4 h-4" />
                Load Config
              </Button>

              <Button
                variant="outline"
                size="md"
                onClick={() => {
                  // Clear cache before re-extracting to force fresh API call
                  if (sourceType === 'api' && sourceInfo?.environmentId) {
                    const cacheKey = `profstudio_skills_cache_${sourceInfo.environmentId}`;
                    localStorage.removeItem(cacheKey);
                    setLoadedFromCache(false);
                  }
                  handleExtractSkills();
                }}
                disabled={isLoading}
                className="border-gray-300 dark:border-gray-600"
              >
                {isLoading ? (
                  <>
                    <LoadingSpinner size="sm" />
                    Re-extracting...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4" />
                    Re-extract
                  </>
                )}
              </Button>

              <Button
                variant="outline"
                size="md"
                onClick={() => setShowDebugModal(true)}
                className="border-blue-300 dark:border-blue-600 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20"
              >
                <Code className="w-4 h-4" />
                View Roles & Skills Data
              </Button>
              
              {loadedFromCache && sourceType === 'api' && (
                <Button
                  variant="outline"
                  size="md"
                  onClick={() => {
                    const cacheKey = `profstudio_skills_cache_${sourceInfo?.environmentId}`;
                    localStorage.removeItem(cacheKey);
                    setLoadedFromCache(false);
                    // Clear current skills to force re-extraction
                    updateSkillsState({
                      skills: [],
                      totalCount: 0,
                      extractionStatus: 'idle',
                      extractionSource: null,
                      extractionError: null,
                      extractedAt: null,
                    });
                    localStorage.removeItem('extractedSkills');
                    localStorage.removeItem('skillsExtractionComplete');
                  }}
                  className="border-orange-300 dark:border-orange-700 text-orange-600 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear Cache
                </Button>
              )}

              <div className="ml-auto">
                <Button
                  variant="primary"
                  size="md"
                  onClick={nextStep}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg"
                >
                  Configure Proficiency Levels
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Skills List */}
            {showSkillsList && (
              <Card className="bg-gray-50 dark:bg-gray-800">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Extracted Skills ({filteredSkills.length}{searchTerm && ` of ${skillsState.skills.length}`})
                    </h4>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search skills..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      />
                    </div>
                  </div>

                  <div className="min-h-[16rem]">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 mb-4">
                      {paginatedSkills.map((skill, index) => (
                        <div
                          key={index}
                          className="p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600 transition-colors"
                        >
                          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {skill.name}
                          </p>
                          {skill.category && (
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {skill.category}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>

                    {filteredSkills.length === 0 && searchTerm && (
                      <div className="text-center py-8">
                        <Search className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400">
                          No skills found matching "{searchTerm}"
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Pagination Controls */}
                  {filteredSkills.length > 0 && totalPages > 1 && (
                    <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        Showing {startIndex + 1}-{Math.min(endIndex, filteredSkills.length)} of {filteredSkills.length}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => goToPage(currentPage - 1)}
                          disabled={currentPage === 1}
                          className="p-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          aria-label="Previous page"
                        >
                          <ChevronLeft className="w-4 h-4" />
                        </button>
                        <div className="flex items-center gap-1">
                          {Array.from({ length: totalPages }, (_, i) => i + 1)
                            .filter(page => {
                              // Show first page, last page, current page, and pages around current
                              return page === 1 ||
                                     page === totalPages ||
                                     Math.abs(page - currentPage) <= 1;
                            })
                            .map((page, idx, array) => (
                              <React.Fragment key={page}>
                                {idx > 0 && array[idx - 1] !== page - 1 && (
                                  <span className="px-2 text-gray-400">...</span>
                                )}
                                <button
                                  onClick={() => goToPage(page)}
                                  className={`min-w-[2rem] px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                                    currentPage === page
                                      ? 'bg-purple-600 text-white'
                                      : 'border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                  }`}
                                >
                                  {page}
                                </button>
                              </React.Fragment>
                            ))}
                        </div>
                        <button
                          onClick={() => goToPage(currentPage + 1)}
                          disabled={currentPage === totalPages}
                          className="p-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          aria-label="Next page"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-4 bg-error-50 dark:bg-error-900/20 border-2 border-error-200 dark:border-error-800 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-error-600 dark:text-error-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold text-error-900 dark:text-error-100">
                  Extraction Failed
                </p>
                <p className="text-sm text-error-700 dark:text-error-300 mt-1">
                  {error}
                </p>
                {requestResponseLog && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowDebugModal(true)}
                    className="mt-3 border-error-300 dark:border-error-700 text-error-700 dark:text-error-300 hover:bg-error-100 dark:hover:bg-error-900/40"
                  >
                    <Code className="w-4 h-4" />
                    View Request/Response Details
                  </Button>
                )}
              </div>
              <button
                onClick={() => setError(null)}
                className="flex-shrink-0 text-error-400 hover:text-error-600 dark:text-error-500 dark:hover:text-error-300 transition-colors"
                aria-label="Close error message"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </Card>

      {/* Debug Modal */}
      {showDebugModal && requestResponseLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden border-2 border-gray-200 dark:border-gray-700">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                    <Code className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Request/Response Details
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Debug information for skills extraction
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowDebugModal(false)}
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-100px)]">
              <div className="space-y-6">
                {/* Request Section */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 rounded text-xs font-semibold text-blue-700 dark:text-blue-300">
                      REQUEST
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(requestResponseLog.request.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <div className="space-y-2 text-sm">
                      <div className="flex items-start gap-2">
                        <span className="font-semibold text-gray-700 dark:text-gray-300 min-w-[80px]">Method:</span>
                        <span className="font-mono text-blue-600 dark:text-blue-400">{requestResponseLog.request.method}</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="font-semibold text-gray-700 dark:text-gray-300 min-w-[80px]">Endpoint:</span>
                        <span className="font-mono text-blue-600 dark:text-blue-400">{requestResponseLog.request.endpoint}</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="font-semibold text-gray-700 dark:text-gray-300 min-w-[80px]">Payload:</span>
                        <pre className="flex-1 bg-white dark:bg-gray-900 p-3 rounded border border-gray-200 dark:border-gray-700 overflow-x-auto text-xs">
                          {JSON.stringify(requestResponseLog.request.payload, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Response Section */}
                {requestResponseLog.response && (
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <div className="px-2 py-1 bg-green-100 dark:bg-green-900/30 rounded text-xs font-semibold text-green-700 dark:text-green-300">
                        RESPONSE
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(requestResponseLog.response.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <div className="space-y-2 text-sm">
                        <div className="flex items-start gap-2">
                          <span className="font-semibold text-gray-700 dark:text-gray-300 min-w-[80px]">Status:</span>
                          <span className="font-mono text-green-600 dark:text-green-400">{requestResponseLog.response.status}</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <span className="font-semibold text-gray-700 dark:text-gray-300 min-w-[80px]">Data:</span>
                          <pre className="flex-1 bg-white dark:bg-gray-900 p-3 rounded border border-gray-200 dark:border-gray-700 overflow-x-auto text-xs max-h-96">
                            {JSON.stringify(requestResponseLog.response.data, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Error Section */}
                {requestResponseLog.error && (
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <div className="px-2 py-1 bg-red-100 dark:bg-red-900/30 rounded text-xs font-semibold text-red-700 dark:text-red-300">
                        ERROR
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(requestResponseLog.error.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
                      <div className="space-y-3 text-sm">
                        <div className="flex items-start gap-2">
                          <span className="font-semibold text-gray-700 dark:text-gray-300 min-w-[80px]">Message:</span>
                          <span className="text-red-700 dark:text-red-300">{requestResponseLog.error.message}</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <span className="font-semibold text-gray-700 dark:text-gray-300 min-w-[80px]">Details:</span>
                          <pre className="flex-1 bg-white dark:bg-gray-900 p-3 rounded border border-red-200 dark:border-red-800 overflow-x-auto text-xs max-h-96">
                            {JSON.stringify(requestResponseLog.error.details, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex justify-end">
              <Button
                variant="outline"
                onClick={() => setShowDebugModal(false)}
                className="border-gray-300 dark:border-gray-600"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Save Config Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Save className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                Save Skills Configuration
              </h3>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Configuration Name *
                </label>
                <input
                  type="text"
                  value={configName}
                  onChange={(e) => setConfigName(e.target.value)}
                  placeholder="e.g., Senior Engineer Skills - ADOHERTY_DEMO"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description (Optional)
                </label>
                <textarea
                  value={configDescription}
                  onChange={(e) => setConfigDescription(e.target.value)}
                  placeholder="Describe this skill configuration..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  <strong>Saving:</strong> {skillsState.totalCount} skills from {getSourceLabel()}
                  {sourceInfo?.environmentId && ` (${sourceInfo.environmentId})`}
                </p>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowSaveModal(false);
                  setConfigName('');
                  setConfigDescription('');
                }}
                className="flex-1 border-gray-300 dark:border-gray-600"
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={saveSkillsConfig}
                disabled={!configName.trim()}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                <Save className="w-4 h-4" />
                Save Configuration
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Load Config Modal */}
      {showLoadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Upload className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                Load Skills Configuration
              </h3>
            </div>

            <div className="p-6 flex-1 overflow-y-auto">
              {savedConfigs.length === 0 ? (
                <div className="text-center py-12">
                  <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">No saved configurations found</p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                    Extract skills and click "Save Config" to create one
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {savedConfigs.map((config) => (
                    <div
                      key={config.id}
                      className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 dark:text-white">
                            {config.name}
                          </h4>
                          {config.description && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {config.description}
                            </p>
                          )}
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-500">
                            <span className="flex items-center gap-1">
                              <Database className="w-3 h-3" />
                              {config.totalCount} skills
                            </span>
                            <span className="flex items-center gap-1">
                              {config.sourceType === 'csv' && <FileText className="w-3 h-3" />}
                              {config.sourceType === 'api' && <Server className="w-3 h-3" />}
                              {config.sourceType === 'sftp' && <HardDrive className="w-3 h-3" />}
                              {config.sourceType || 'Unknown'}
                            </span>
                            {config.sourceInfo?.environmentId && (
                              <span>{config.sourceInfo.environmentId}</span>
                            )}
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {new Date(config.extractedAt).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => loadSkillsConfig(config)}
                            className="border-purple-300 dark:border-purple-600 text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20"
                          >
                            <Upload className="w-3 h-3" />
                            Load
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => deleteSkillsConfig(config.id)}
                            className="border-red-300 dark:border-red-600 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
              <Button
                variant="outline"
                onClick={() => setShowLoadModal(false)}
                className="border-gray-300 dark:border-gray-600"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Debug Modal - View Roles & Skills Data */}
      {showDebugModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  Extracted Roles & Skills Data
                </h3>
                <button
                  onClick={() => setShowDebugModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <span className="text-2xl">×</span>
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {(() => {
                const skillsExtractionData = localStorage.getItem('skillsExtractionData');
                if (!skillsExtractionData) {
                  return (
                    <div className="text-center py-8 text-gray-600 dark:text-gray-400">
                      <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No extraction data available</p>
                    </div>
                  );
                }

                try {
                  const data = JSON.parse(skillsExtractionData);

                  return (
                    <div className="space-y-6">
                      {/* Summary Stats */}
                      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                        <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Extraction Summary</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-blue-700 dark:text-blue-300 font-medium">Total Roles</p>
                            <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{data.roles?.length || 0}</p>
                          </div>
                          <div>
                            <p className="text-blue-700 dark:text-blue-300 font-medium">Total Skills</p>
                            <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{data.skills?.length || 0}</p>
                          </div>
                          <div>
                            <p className="text-blue-700 dark:text-blue-300 font-medium">Source</p>
                            <p className="text-lg font-semibold text-blue-900 dark:text-blue-100">{data.source_info?.environment || 'N/A'}</p>
                          </div>
                          <div>
                            <p className="text-blue-700 dark:text-blue-300 font-medium">Extracted At</p>
                            <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                              {data.extraction_time ? new Date(data.extraction_time).toLocaleString() : 'N/A'}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Complete API Response - Roles with all fields */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                          <Code className="w-5 h-5" />
                          Complete API Response JSON (Roles with Skills)
                        </h4>
                        <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-2">
                          <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                            This shows the complete roles array as received from the API, including all fields like id, title, skillProficiencies, archivalStatus, etc.
                          </p>
                        </div>
                        <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto max-h-[600px] text-xs">
                          {JSON.stringify({ roles: data.roles }, null, 2)}
                        </pre>
                      </div>

                      {/* Full Extraction Response */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                          <Code className="w-5 h-5" />
                          Full Extraction Response
                        </h4>
                        <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto max-h-96 text-xs">
                          {JSON.stringify(data, null, 2)}
                        </pre>
                      </div>
                    </div>
                  );
                } catch (err) {
                  return (
                    <div className="text-center py-8 text-red-600 dark:text-red-400">
                      <AlertCircle className="w-12 h-12 mx-auto mb-4" />
                      <p>Error parsing extraction data</p>
                      <p className="text-sm mt-2">{String(err)}</p>
                    </div>
                  );
                }
              })()}
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
              <Button
                variant="outline"
                onClick={() => setShowDebugModal(false)}
                className="border-gray-300 dark:border-gray-600"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExtractSkills;