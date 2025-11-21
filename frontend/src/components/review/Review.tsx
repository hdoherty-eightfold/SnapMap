import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { apiClient } from '../../utils/api';
import { Download, ArrowRight } from 'lucide-react';
import { Button } from '../common/Button';

interface AssessmentResult {
  skill_name: string;
  proficiency_level: string;
  proficiency_numeric: number;
  confidence_score: number;
  evidence: string[];
  reasoning: string;
  years_experience?: number;
}

const Review: React.FC = () => {
  const { currentStep, setCurrentStep } = useApp();
  const [assessments, setAssessments] = useState<AssessmentResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runningAssessment, setRunningAssessment] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<'name' | 'proficiency' | 'confidence'>('name');
  const [filterByConfidence, setFilterByConfidence] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const itemsPerPage = 30;

  // Export state
  const [exporting, setExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportLog, setExportLog] = useState<string[]>([]);
  const [exportResults, setExportResults] = useState<{success: number, failed: number, skipped: number, total: number} | null>(null);

  // Debug/Details state
  const [exportDetails, setExportDetails] = useState<any[]>([]);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState<any>(null);

  // Connection info from Step 2
  const [connectedEnvironment, setConnectedEnvironment] = useState<string>('');
  const [availableRoles, setAvailableRoles] = useState<any[]>([]);

  useEffect(() => {
    // Load any existing assessment results
    const saved = localStorage.getItem('assessmentResults');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Ensure we have an array
        if (Array.isArray(parsed)) {
          console.log('[Review] Loaded assessments array:', parsed.length, 'items');
          setAssessments(parsed);
        } else if (parsed && typeof parsed === 'object' && Array.isArray(parsed.assessments)) {
          // Handle case where we might have { assessments: [...] }
          console.log('[Review] Loaded assessments from object:', parsed.assessments.length, 'items');
          setAssessments(parsed.assessments);
        } else {
          console.warn('[Review] Invalid assessment data format:', parsed);
          setAssessments([]);
        }
      } catch (e) {
        console.error('[Review] Failed to load saved assessments:', e);
        setAssessments([]);
      }
    } else {
      console.log('[Review] No saved assessments found in localStorage');
    }

    // Load connection info from Step 2
    const envId = localStorage.getItem('profstudio_env_id');
    const envName = localStorage.getItem('profstudio_env_name') || envId;
    setConnectedEnvironment(envName || 'Not connected');

    // Load roles from skills extraction (Step 2)
    const skillsData = localStorage.getItem('skillsExtractionData');
    if (skillsData) {
      try {
        const data = JSON.parse(skillsData);
        console.log('[Review] Skills extraction data:', data);
        if (data.roles && Array.isArray(data.roles)) {
          console.log('[Review] Loaded roles:', data.roles.length, 'roles');
          setAvailableRoles(data.roles);
        } else {
          console.log('[Review] No roles found in skillsExtractionData');
        }
      } catch (e) {
        console.error('[Review] Failed to load roles:', e);
      }
    } else {
      console.log('[Review] No skillsExtractionData found in localStorage');
    }
  }, []);

  const runAssessment = async () => {
    const savedSkills = localStorage.getItem('extractedSkills');
    if (!savedSkills) {
      setError('No skills available for assessment. Please complete Step 2.');
      return;
    }

    const savedLLMConfig = localStorage.getItem('llmConfig');
    if (!savedLLMConfig) {
      setError('LLM configuration is incomplete. Please configure in Step 3.');
      return;
    }

    setRunningAssessment(true);
    setError(null);

    try {
      const skills = JSON.parse(savedSkills);
      const llmConfig = JSON.parse(savedLLMConfig);

      const response = await apiClient.post('/api/proficiency/assess', {
        text: localStorage.getItem('sampleData') || 'Sample professional profile for assessment',
        skills: skills.map((skill: any) => ({
          name: skill.name,
          description: skill.description || skill.name
        })),
        proficiency_levels: JSON.parse(localStorage.getItem('proficiencyLevels') || JSON.stringify([
          { level: 1, name: 'Novice', description: 'Less than 6 months experience, basic understanding', color: 'bg-gray-500' },
          { level: 2, name: 'Developing', description: '6 months to 1 year, can work with guidance', color: 'bg-blue-500' },
          { level: 3, name: 'Intermediate', description: '1-3 years experience, works independently', color: 'bg-yellow-500' },
          { level: 4, name: 'Advanced', description: '3-5 years experience, deep expertise', color: 'bg-green-500' },
          { level: 5, name: 'Expert', description: '5+ years, thought leader, teaches others', color: 'bg-purple-500' }
        ])),
        llm_config: llmConfig,
        prompt_template: localStorage.getItem('promptTemplate') || 'Assess proficiency for these skills.',
        context: 'Professional skill assessment based on extracted skills'
      });

      const responseData = response.data || response;
      setAssessments(responseData.assessments);
      localStorage.setItem('assessmentResults', JSON.stringify(responseData.assessments));
    } catch (err: any) {
      setError(err.message || 'Assessment failed');
    } finally {
      setRunningAssessment(false);
    }
  };

  const getProficiencyColor = (level: number) => {
    const colors = ['gray', 'red', 'yellow', 'blue', 'green', 'purple'];
    return colors[level] || 'gray';
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const exportToCSV = () => {
    if (!Array.isArray(assessments) || assessments.length === 0) {
      alert('No assessments available to export');
      return;
    }
    const headers = ['Skill Name', 'Proficiency Level', 'Proficiency Numeric', 'Confidence Score', 'Reasoning', 'Evidence', 'Years Experience'];
    const csvData = assessments.map(assessment => [
      assessment.skill_name,
      assessment.proficiency_level,
      assessment.proficiency_numeric,
      assessment.confidence_score,
      assessment.reasoning,
      assessment.evidence.join('; '),
      assessment.years_experience || ''
    ]);

    const csvContent = [headers, ...csvData]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `proficiency_assessment_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToEightfold = async () => {
    try {
      setExporting(true);
      setExportLog([]);
      setExportResults(null);
      setError(null);

      // Add log entry
      const addLog = (message: string) => {
        const timestamp = new Date().toLocaleTimeString();
        setExportLog(prev => [...prev, `[${timestamp}] ${message}`]);
      };

      addLog('Starting export to Eightfold...');

      // Validate we have assessments
      if (!assessments || assessments.length === 0) {
        addLog('❌ ERROR: No assessment results found');
        setError('No assessment results to export. Please run an assessment first.');
        setExporting(false);
        return;
      }

      // Validate we have roles
      if (!availableRoles || availableRoles.length === 0) {
        addLog('❌ ERROR: No roles found from Step 2');
        setError('No roles found. Please extract skills from Step 2 first.');
        setExporting(false);
        return;
      }

      // Get environment ID
      const environmentId = localStorage.getItem('profstudio_env_id');
      if (!environmentId) {
        addLog('❌ ERROR: No environment connected');
        setError('No environment connected. Please complete Step 2 first.');
        setExporting(false);
        return;
      }

      addLog(`Environment: ${connectedEnvironment}`);
      addLog(`Found ${availableRoles.length} role(s) to update`);
      addLog(`Found ${assessments.length} skill assessments`);

      // Log detailed role information
      if (availableRoles.length > 0) {
        addLog(`\nRoles to be updated:`);
        availableRoles.forEach((role, index) => {
          const skillCount = role.skillProficiencies?.length || 0;
          addLog(`  ${index + 1}. ${role.title || role.id} (${skillCount} skills)`);
        });
        addLog(''); // Empty line for readability
      }

      // Build proficiency map from assessments
      const proficiencyMap: Record<string, number> = {};
      assessments.forEach(assessment => {
        const skillName = assessment.skill_name;
        const proficiency = assessment.proficiency_numeric;
        proficiencyMap[skillName.toLowerCase().trim()] = proficiency;
      });

      addLog(`Built proficiency map for ${Object.keys(proficiencyMap).length} skills`);

      // Export each role
      let successCount = 0;
      let failedCount = 0;
      let skippedCount = 0;
      const totalRoles = availableRoles.length;
      const details: any[] = [];

      for (let i = 0; i < availableRoles.length; i++) {
        const role = availableRoles[i];
        const progress = Math.round(((i + 1) / totalRoles) * 100);
        setExportProgress(progress);

        addLog(`\n[${i + 1}/${totalRoles}] Processing role: ${role.title || role.id}`);

        try {
          // Get auth token from localStorage
          const authToken = localStorage.getItem('profstudio_auth_token');

          const requestPayload = {
            assessments: assessments,
            proficiency_map: proficiencyMap,
            environment_id: environmentId,
            role_id: role.id,
            role_title: role.title,
            role_data: role,
            auth_token: authToken
          };

          const response = await apiClient.post('/api/proficiency/export-to-eightfold', requestPayload);

          // Determine if role was skipped or successfully updated
          const wasSkipped = response.data?.method_used === 'SKIPPED' || response.data?.total_skills === 0;

          // Capture request/response details for debugging
          // Sanitize request payload to reduce size and hide sensitive data
          const sanitizedRequest = {
            environment_id: requestPayload.environment_id,
            role_id: requestPayload.role_id,
            role_title: requestPayload.role_title,
            assessment_count: requestPayload.assessments.length,
            proficiency_map_size: Object.keys(requestPayload.proficiency_map).length,
            role_has_skills: requestPayload.role_data?.skillProficiencies?.length || 0,
            auth_token: authToken ? '***' + authToken.slice(-4) : 'none', // Show last 4 chars only
            // Include full data for debugging if needed (commented out to save memory)
            // full_assessments: requestPayload.assessments,
            // full_proficiency_map: requestPayload.proficiency_map,
            // full_role_data: requestPayload.role_data
          };

          details.push({
            role_index: i + 1,
            role_id: role.id,
            role_title: role.title,
            request: sanitizedRequest,
            response: response.data,
            success: response.data?.success || false,
            skipped: wasSkipped,
            timestamp: new Date().toISOString()
          });

          if (response.data?.success) {
            // Show the reason if available, otherwise show the message
            const logMessage = response.data.reason || response.data.message || `Updated ${response.data.assessed_skills}/${response.data.total_skills} skills`;

            // Separate skipped from success
            if (wasSkipped) {
              skippedCount++;
              addLog(`⚠️ SKIPPED: ${logMessage}`);
            } else {
              successCount++;
              addLog(`✅ SUCCESS: ${logMessage}`);
            }
          } else {
            failedCount++;
            addLog(`❌ FAILED: ${response.data?.message || 'Unknown error'}`);
          }
        } catch (err: any) {
          failedCount++;
          const errorMsg = err.response?.data?.detail || err.message || 'Unknown error';
          addLog(`❌ FAILED: ${errorMsg}`);

          // Capture error details
          details.push({
            role_index: i + 1,
            role_id: role.id,
            role_title: role.title,
            request: {
              role_id: role.id,
              role_title: role.title,
              environment_id: environmentId
            },
            response: null,
            error: {
              message: errorMsg,
              detail: err.response?.data,
              stack: err.stack
            },
            success: false,
            skipped: false,
            timestamp: new Date().toISOString()
          });
        }
      }

      // Store details for debugging
      setExportDetails(details);

      addLog(`\n=== Export Complete ===`);
      addLog(`✅ Success: ${successCount} role(s)`);
      addLog(`⚠️ Skipped: ${skippedCount} role(s)`);
      addLog(`❌ Failed: ${failedCount} role(s)`);
      addLog(`📊 Total: ${totalRoles} role(s)`);

      // Add warning if all roles were skipped
      if (skippedCount === totalRoles && totalRoles > 0) {
        addLog(`\n⚠️ WARNING: All roles were skipped - they have no skillProficiencies to update`);
        addLog(`This usually means the roles don't have any skills assigned in Eightfold yet`);
      }

      setExportResults({
        success: successCount,
        failed: failedCount,
        skipped: skippedCount,
        total: totalRoles
      });

    } catch (err: any) {
      const errorMsg = err.message || 'Unknown error';
      setError(`Export failed: ${errorMsg}`);
      setExportLog(prev => [...prev, `\n❌ FATAL ERROR: ${errorMsg}`]);
    } finally {
      setExporting(false);
      setExportProgress(100);
    }
  };

  // Filter and sort assessments
  const getFilteredAssessments = () => {
    // Ensure assessments is an array
    if (!Array.isArray(assessments)) {
      return [];
    }
    let filtered = [...assessments];

    // Apply confidence filter
    if (filterByConfidence !== 'all') {
      filtered = filtered.filter(assessment => {
        const score = assessment.confidence_score;
        if (filterByConfidence === 'high') return score >= 0.8;
        if (filterByConfidence === 'medium') return score >= 0.6 && score < 0.8;
        if (filterByConfidence === 'low') return score < 0.6;
        return true;
      });
    }

    // Apply sorting
    filtered.sort((a, b) => {
      if (sortBy === 'name') {
        return a.skill_name.localeCompare(b.skill_name);
      } else if (sortBy === 'proficiency') {
        return b.proficiency_numeric - a.proficiency_numeric;
      } else if (sortBy === 'confidence') {
        return b.confidence_score - a.confidence_score;
      }
      return 0;
    });

    return filtered;
  };

  // Paginate assessments
  const getPaginatedAssessments = () => {
    const filtered = getFilteredAssessments();
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return {
      assessments: filtered.slice(startIndex, endIndex),
      totalItems: filtered.length,
      totalPages: Math.ceil(filtered.length / itemsPerPage)
    };
  };

  const { assessments: paginatedAssessments, totalItems, totalPages } = getPaginatedAssessments();

  // Debug pagination
  useEffect(() => {
    console.log('[Review Pagination Debug]', {
      assessmentsLength: assessments.length,
      isArray: Array.isArray(assessments),
      filterByConfidence,
      sortBy,
      totalItems,
      totalPages,
      currentPage,
      itemsPerPage
    });
  }, [assessments, filterByConfidence, sortBy, totalItems, totalPages, currentPage]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-6">
      <div className="w-full max-w-5xl">
        {/* Main Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-6">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">👁️</span>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Review and Load</h2>
            <p className="text-gray-600 dark:text-gray-400">
              Review and load proficiency assessments into Eightfold
            </p>
          </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <span className="text-red-600">⚠️</span>
              <span className="ml-2 text-red-700">{error}</span>
            </div>
          </div>
        )}

          {/* Connection Info */}
          {connectedEnvironment && connectedEnvironment !== 'Not connected' && (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-xl p-6 mb-8">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                  <span className="text-2xl">🔌</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-blue-900 dark:text-blue-100 uppercase tracking-wide mb-2">Connected Environment</h3>
                  <p className="text-lg font-semibold text-blue-800 dark:text-blue-200 mb-2">{connectedEnvironment}</p>
                  {availableRoles.length > 0 && (
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      <span className="font-semibold">{availableRoles.length}</span> role(s) available for export
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

        {/* Export Progress and Log */}
        {(exporting || exportResults) && (
          <div className="bg-gray-50 border border-gray-300 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>🚀</span>
              Export Progress
            </h3>

            {/* Progress Bar */}
            {exporting && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-700 font-medium">Processing roles...</span>
                  <span className="text-sm text-gray-700 font-bold">{exportProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-full transition-all duration-300 ease-out"
                    style={{ width: `${exportProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Results Summary */}
            {exportResults && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-green-100 border border-green-300 rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-green-700">{exportResults.success}</div>
                  <div className="text-xs text-green-600 font-medium">✅ Success</div>
                </div>
                <div className="bg-yellow-100 border border-yellow-300 rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-yellow-700">{exportResults.skipped}</div>
                  <div className="text-xs text-yellow-600 font-medium">⚠️ Skipped</div>
                </div>
                <div className="bg-red-100 border border-red-300 rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-red-700">{exportResults.failed}</div>
                  <div className="text-xs text-red-600 font-medium">❌ Failed</div>
                </div>
                <div className="bg-blue-100 border border-blue-300 rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-blue-700">{exportResults.total}</div>
                  <div className="text-xs text-blue-600 font-medium">📊 Total</div>
                </div>
              </div>
            )}

            {/* Operation Log */}
            {exportLog.length > 0 && (
              <div className="bg-white border border-gray-300 rounded-lg p-4 max-h-96 overflow-y-auto">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Operation Log</h4>
                <div className="space-y-1 font-mono text-xs">
                  {exportLog.map((entry, index) => (
                    <div
                      key={index}
                      className={`${
                        entry.includes('✅') ? 'text-green-700' :
                        entry.includes('❌') ? 'text-red-700' :
                        entry.includes('===') ? 'text-blue-700 font-bold' :
                        'text-gray-700'
                      }`}
                    >
                      {entry}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* View Details Button */}
            {exportDetails.length > 0 && (
              <div className="mt-4 flex justify-center">
                <button
                  onClick={() => setShowDetailsModal(true)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <span>🔍</span>
                  View Request/Response Details ({exportDetails.length} roles)
                </button>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        {assessments.length > 0 && !exporting && (
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8 border-t border-gray-200 dark:border-gray-700">
            <Button
              variant="primary"
              size="md"
              onClick={exportToCSV}
              disabled={loading}
              className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white shadow-lg"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={exportToEightfold}
              disabled={exporting || loading}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg"
            >
              {exporting ? 'Exporting...' : 'Export to Eightfold'}
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>

      {/* Back to Run Assessment Button */}
      <div className="flex justify-center">
        <Button
          variant="outline"
          size="md"
          onClick={() => setCurrentStep(4)}
          className="border-2 border-teal-300 text-teal-600 hover:bg-teal-50 dark:border-teal-700 dark:text-teal-400 dark:hover:bg-teal-900/20"
        >
          ← Back to Run Assessment
        </Button>
      </div>
    </div>

    {/* Details Modal (rendered outside main content for proper z-index layering) */}
    {showDetailsModal && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <span>🔍</span>
                Export Request/Response Details
              </h3>
              <button
                onClick={() => {
                  setShowDetailsModal(false);
                  setSelectedDetail(null);
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <span className="text-2xl">×</span>
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6">
            {selectedDetail ? (
              // Show detailed view of one role
              <div className="space-y-4">
                <button
                  onClick={() => setSelectedDetail(null)}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  ← Back to list
                </button>

                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Role {selectedDetail.role_index}: {selectedDetail.role_title}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Role ID: {selectedDetail.role_id} | Status: {
                      selectedDetail.skipped ? '⚠️ Skipped' :
                      selectedDetail.success ? '✅ Success' :
                      '❌ Failed'
                    }
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Request Payload */}
                  <div>
                    <h5 className="font-semibold text-gray-900 dark:text-white mb-2">📤 Request Payload</h5>
                    <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto max-h-96 text-xs">
                      {JSON.stringify(selectedDetail.request, null, 2)}
                    </pre>
                  </div>

                  {/* Response Data */}
                  <div>
                    <h5 className="font-semibold text-gray-900 dark:text-white mb-2">
                      {selectedDetail.error ? '❌ Error Details' : '📥 Response Data'}
                    </h5>
                    <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto max-h-96 text-xs">
                      {JSON.stringify(selectedDetail.error || selectedDetail.response, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              // Show list of all roles
              <div className="space-y-4">
                {/* Export Summary */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-3">Export Summary</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <p className="text-blue-700 dark:text-blue-300 font-medium">Total Roles</p>
                      <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{exportDetails.length}</p>
                    </div>
                    <div>
                      <p className="text-green-700 dark:text-green-300 font-medium">✅ Success</p>
                      <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                        {exportDetails.filter(d => d.success && !d.skipped).length}
                      </p>
                    </div>
                    <div>
                      <p className="text-yellow-700 dark:text-yellow-300 font-medium">⚠️ Skipped</p>
                      <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">
                        {exportDetails.filter(d => d.skipped).length}
                      </p>
                    </div>
                    <div>
                      <p className="text-red-700 dark:text-red-300 font-medium">❌ Failed</p>
                      <p className="text-2xl font-bold text-red-900 dark:text-red-100">
                        {exportDetails.filter(d => !d.success).length}
                      </p>
                    </div>
                  </div>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Click on any role to view detailed request/response JSON
                </p>

                {exportDetails.map((detail, index) => {
                  const statusIcon = detail.skipped ? '⚠️' : (detail.success ? '✅' : '❌');
                  const statusText = detail.skipped ? 'Skipped' : (detail.success ? 'Success' : 'Failed');

                  return (
                    <button
                      key={index}
                      onClick={() => setSelectedDetail(detail)}
                      className={`w-full text-left p-4 rounded-lg border transition-colors ${
                        detail.skipped
                          ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 hover:bg-yellow-100 dark:hover:bg-yellow-900/30'
                          : detail.success
                          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 hover:bg-green-100 dark:hover:bg-green-900/30'
                          : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 hover:bg-red-100 dark:hover:bg-red-900/30'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {statusIcon} Role {detail.role_index}: {detail.role_title}
                          </h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            ID: {detail.role_id} | Status: {statusText}
                          </p>
                        </div>
                        <span className="text-blue-600 dark:text-blue-400">→</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <div className="p-6 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => {
                setShowDetailsModal(false);
                setSelectedDetail(null);
              }}
              className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    )}
  </div>
  );
};

export default Review;