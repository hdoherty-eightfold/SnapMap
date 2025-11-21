/**
 * Configure Proficiency Component - Step 3
 * Configure proficiency levels, LLM provider, and assessment prompts
 */

import React, { useState, useEffect } from 'react';
import {
  Settings, Zap, Brain, Edit3, Plus, Trash2, Save, RotateCcw,
  ChevronDown, ChevronUp, CheckCircle, AlertCircle, Info,
  Sliders, Code, Play, Eye, EyeOff, Key, Copy, X, ArrowRight
} from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { useToast } from '../../contexts/ToastContext';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { cn } from '../../utils/cn';
import api from '../../utils/api';
import { APIKeyManager } from '../keys/APIKeyManager';
import { Select, SelectOption } from '../ui/Select';
import { ConfigurationManager } from '../configuration/ConfigurationManager';
import { promptTemplates, getDefaultPrompt, type PromptTemplate } from '../../config/promptTemplates';
import styles from './ConfigureProficiency.module.css';

interface ProficiencyLevel {
  level: number;
  name: string;
  description: string;
}

interface LLMConfig {
  provider: 'openai' | 'anthropic' | 'google' | 'grok' | 'huggingface';
  model: string;
  temperature: number;
  max_tokens: number;
  api_key: string;
}

interface PromptTemplate {
  name: string;
  content: string;
  variables: string[];
}

const DEFAULT_PROFICIENCY_LEVELS: ProficiencyLevel[] = [
  { level: 1, name: 'Novice', description: 'Less than 6 months experience, basic understanding' },
  { level: 2, name: 'Developing', description: '6 months to 1 year, can work with guidance' },
  { level: 3, name: 'Intermediate', description: '1-3 years experience, works independently' },
  { level: 4, name: 'Advanced', description: '3-5 years experience, deep expertise' },
  { level: 5, name: 'Expert', description: '5+ years, thought leader, teaches others' }
];

const DEFAULT_PROMPT = `You are an expert skills assessor. Assess proficiency levels for each skill based on typical industry standards.

Skills to assess:
{skills}

Proficiency Levels:
{proficiency_levels}

For each skill, provide ONLY:
1. Numeric proficiency level (1-5, must match one of the levels above)
2. Confidence score (0.0 to 1.0)
3. Brief reasoning

Return your response as a JSON array:
[
  {{
    "skill_name": "exact skill name from list",
    "proficiency_numeric": 1-5,
    "confidence_score": 0.0-1.0,
    "evidence": ["brief point 1", "brief point 2"],
    "reasoning": "concise explanation"
  }}
]

IMPORTANT: Keep responses CONCISE. Return ONLY valid JSON, no other text.`;

const LLM_PROVIDERS = [
  {
    id: 'openrouter',
    name: 'OpenRouter',
    description: '400+ models with single API key - FREE models available!',
    models: [
      'deepseek/deepseek-r1:free',
      'google/gemini-2.5-flash',
      'deepseek/deepseek-chat',
      'google/gemini-2.5-pro',
      'x-ai/grok-3',
      'anthropic/claude-3.5-sonnet',
      'openai/gpt-4-turbo'
    ],
    icon: '🔀',
    recommended: true,
    free: true
  },
  {
    id: 'deepseek',
    name: 'DeepSeek',
    description: 'DeepSeek-V3 & R1 - VERY cheap, 5M free tokens/month',
    models: ['deepseek-chat', 'deepseek-reasoner'],
    icon: '🚀',
    recommended: false,
    free: true
  },
  {
    id: 'google',
    name: 'Google Gemini',
    description: 'Gemini 2.5, fast and FREE',
    models: ['gemini-2.5-flash', 'gemini-2.5-pro'],
    icon: '✨',
    recommended: true,
    free: true
  },
  {
    id: 'huggingface',
    name: 'Hugging Face',
    description: '800K+ open-source models, FREE tier',
    models: [
      'google/flan-t5-xxl',
      'google/flan-t5-large',
      'mistralai/Mistral-7B-Instruct-v0.3',
      'HuggingFaceH4/zephyr-7b-beta',
      'tiiuae/falcon-7b-instruct'
    ],
    icon: '🤗',
    recommended: true,
    free: true
  },
  {
    id: 'grok',
    name: 'Grok (xAI)',
    description: 'Fast, free tier available',
    models: ['grok-beta', 'grok-2-latest', 'grok-vision-beta'],
    icon: '🚀',
    free: true
  },
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'GPT-4, high quality',
    models: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    icon: '🤖',
    premium: true
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    description: 'Claude, excellent reasoning',
    models: ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
    icon: '🧠',
    premium: true
  },
  {
    id: 'ollama',
    name: 'Ollama (Local)',
    description: 'Run models locally - FREE, private, unlimited',
    models: [
      'phi3.5:3.8b-mini-instruct-q4_K_M',
      'llama3.3:latest',
      'llama3.2:latest',
      'qwen2.5:latest',
      'mistral:latest',
      'phi3:latest',
      'deepseek-r1:latest'
    ],
    icon: '🦙',
    recommended: true,
    free: true,
    local: true
  }
];

export const ConfigureProficiency: React.FC = () => {
  const { skillsState, nextStep, setIsLoading, setError, isLoading, error, setCurrentStep } = useApp();
  const { success, error: showToastError } = useToast();

  // Clear global error when component mounts (entering this page)
  useEffect(() => {
    setError(null);
  }, [setError]);

  // State
  const [proficiencyLevels, setProficiencyLevels] = useState<ProficiencyLevel[]>(DEFAULT_PROFICIENCY_LEVELS);
  const [llmConfig, setLLMConfig] = useState<LLMConfig>({
    provider: 'openrouter',
    model: 'deepseek/deepseek-r1:free',
    temperature: 0.7,
    max_tokens: 8000,
    api_key: ''
  });
  const [selectedAPIKey, setSelectedAPIKey] = useState<{ provider: string; keyId: string } | null>(null);
  const [selectedPromptId, setSelectedPromptId] = useState<string>(getDefaultPrompt().id);
  const [promptTemplate, setPromptTemplate] = useState<string>(getDefaultPrompt().template);
  const [promptPreview, setPromptPreview] = useState<string>('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showPromptEditor, setShowPromptEditor] = useState(false);
  const [showAPIKey, setShowAPIKey] = useState(false);
  const [testResults, setTestResults] = useState<any>(null);
  const [isTestingLLM, setIsTestingLLM] = useState(false);
  const [showManageConfigs, setShowManageConfigs] = useState(false);
  const [savedAPIKeys, setSavedAPIKeys] = useState<any[]>([]);
  const [showConfigManager, setShowConfigManager] = useState(false);
  const [configManagerTab, setConfigManagerTab] = useState<'save' | 'load'>('load');
  const [newConfigName, setNewConfigName] = useState('');
  const [unlimitedTokens, setUnlimitedTokens] = useState(false);
  const [savedConfigurations, setSavedConfigurations] = useState<any[]>([]);

  // Load saved API keys on mount
  useEffect(() => {
    const loadSavedKeys = () => {
      try {
        const saved = localStorage.getItem('llm_api_keys');
        if (saved) {
          const keys = JSON.parse(saved);
          setSavedAPIKeys(keys);
        }
      } catch (e) {
        // Silently fail
      }
    };
    loadSavedKeys();
  }, []);

  // Load saved configuration on mount
  useEffect(() => {
    loadSavedConfiguration();
  }, []);

  // Generate prompt preview whenever skills, levels, or template changes
  useEffect(() => {
    const generatePreview = () => {
      // Format skills
      const skillsText = skillsState.skills.length > 0
        ? skillsState.skills.map(s => `- ${s.name}`).join('\n')
        : '(No skills loaded yet)';

      // Format proficiency levels
      const levelsText = proficiencyLevels.map(
        level => `- ${level.name} (${level.level}): ${level.description}`
      ).join('\n');

      // Replace merge strings with actual data
      let preview = promptTemplate
        .replace('{skills}', skillsText)
        .replace('{proficiency_levels}', levelsText);

      setPromptPreview(preview);
    };

    generatePreview();
  }, [skillsState.skills, proficiencyLevels, promptTemplate]);

  // Load saved configurations from API on mount
  useEffect(() => {
    loadSavedConfigurations();
  }, []);

  // Load saved configurations from API
  const loadSavedConfigurations = async () => {
    try {
      const response = await api.get('/api/configurations/');
      setSavedConfigurations(response.data || []);
    } catch (error) {
      console.error('Failed to load configurations:', error);
    }
  };

  // Load a specific configuration (called from ConfigurationManager)
  const loadConfiguration = async (config: any) => {
    try {
      // Apply configuration
      setProficiencyLevels(config.proficiency_levels || config.proficiencyLevels);
      setLLMConfig({
        ...llmConfig, // Keep current API key
        provider: config.llm_config?.provider || config.llmConfig?.provider,
        model: config.llm_config?.model || config.llmConfig?.model,
        temperature: config.llm_config?.temperature || config.llmConfig?.temperature,
        max_tokens: config.llm_config?.max_tokens || config.llmConfig?.max_tokens
      });
      setPromptTemplate(config.prompt_template || config.promptTemplate);
      setSelectedPromptId(config.prompt_template_id || 'simple');

      success('Configuration loaded successfully');
    } catch (error) {
      showToastError('Failed to load configuration');
    }
  };

  const loadSavedConfiguration = () => {
    try {
      const saved = localStorage.getItem('profstudio_proficiency_config');
      if (saved) {
        const config = JSON.parse(saved);
        if (config.proficiencyLevels) setProficiencyLevels(config.proficiencyLevels);
        if (config.llmConfig) setLLMConfig(config.llmConfig);

        // Migrate old prompt template to new format
        if (config.promptTemplate) {
          let template = config.promptTemplate;

          // Check if template has old variables
          const hasOldVariables = template.includes('{skills_to_assess}') ||
                                   template.includes('{text}') ||
                                   template.includes('{context}');

          if (hasOldVariables) {
            // Replace old variable names
            template = template.replace(/\{skills_to_assess\}/g, '{skills}');

            // Remove {text} and {context} and their surrounding content
            template = template.replace(/\{text\}/g, '');
            template = template.replace(/\{context\}/g, '');

            // Clean up extra whitespace/newlines
            template = template.replace(/\n{3,}/g, '\n\n').trim();

            // If template is now broken, use DEFAULT_PROMPT
            if (!template.includes('{skills}') || !template.includes('{proficiency_levels}')) {
              template = DEFAULT_PROMPT;
              showToastError(
                'Prompt Template Updated',
                'Your saved prompt was missing required variables. Reset to default template with {skills} and {proficiency_levels}.'
              );
            } else {
              success(
                'Prompt Template Migrated',
                'Updated template: {skills_to_assess} → {skills}, removed {text} and {context}'
              );
            }

            setPromptTemplate(template);

            // Save the migrated template
            config.promptTemplate = template;
            localStorage.setItem('profstudio_proficiency_config', JSON.stringify(config));
          } else {
            setPromptTemplate(template);
          }
        }
      }
    } catch (err) {
      // Silently fail
    }
  };

  const saveConfiguration = async (configName?: string) => {
    // If no name provided, open modal in save mode
    if (!configName || !configName.trim()) {
      setConfigManagerTab('save');
      setNewConfigName(`${llmConfig.provider} ${llmConfig.model}`.substring(0, 50));
      setShowConfigManager(true);
      return false;
    }

    try {
      // Default color mapping for proficiency levels
      const levelColors = [
        'bg-red-100 text-red-800',
        'bg-orange-100 text-orange-800',
        'bg-yellow-100 text-yellow-800',
        'bg-green-100 text-green-800',
        'bg-blue-100 text-blue-800'
      ];

      // Transform proficiency levels to include color field
      const proficiencyLevelsWithColor = proficiencyLevels.map((level: any, index: number) => ({
        level: level.level || (index + 1),
        name: level.name,
        description: level.description,
        color: level.color || levelColors[index] || 'bg-gray-100 text-gray-800'
      }));

      const configData = {
        name: configName.trim(),
        description: `${proficiencyLevels.length} levels`,
        proficiency_levels: proficiencyLevelsWithColor,
        llm_config: {
          provider: llmConfig.provider,
          model: llmConfig.model,
          temperature: llmConfig.temperature,
          max_tokens: llmConfig.max_tokens
        },
        prompt_template: promptTemplate,
        author: 'User'
      };

      // Save to backend API
      const response = await fetch('http://localhost:8002/api/configurations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configData)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Save failed: ${response.statusText}`);
      }

      const savedConfig = await response.json();

      // Also save to localStorage for backward compatibility
      const localConfig = {
        proficiencyLevels,
        llmConfig,
        promptTemplate,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem('profstudio_proficiency_config', JSON.stringify(localConfig));

      success('Configuration Saved', `"${configName}" has been saved successfully.`);
      return true;
    } catch (err: any) {
      console.error('Save configuration error:', err);
      showToastError('Save Failed', err.message || 'Failed to save configuration. Please try again.');
      return false;
    }
  };


  const addProficiencyLevel = () => {
    const newLevel = proficiencyLevels.length + 1;
    setProficiencyLevels([...proficiencyLevels, {
      level: newLevel,
      name: `Level ${newLevel}`,
      description: 'Enter description...',
      color: 'bg-indigo-500'
    }]);
  };

  const removeProficiencyLevel = (levelToRemove: number) => {
    if (proficiencyLevels.length <= 2) return; // Keep at least 2 levels
    setProficiencyLevels(proficiencyLevels.filter(level => level.level !== levelToRemove));
  };

  const updateProficiencyLevel = (level: number, field: keyof ProficiencyLevel, value: any) => {
    setProficiencyLevels(proficiencyLevels.map(pl =>
      pl.level === level ? { ...pl, [field]: value } : pl
    ));
  };

  const resetToDefaults = () => {
    setProficiencyLevels(DEFAULT_PROFICIENCY_LEVELS);
    setPromptTemplate(DEFAULT_PROMPT);
    setLLMConfig({
      provider: 'google',
      model: 'gemini-2.0-flash-exp',
      temperature: 0.7,
      max_tokens: 2000,
      api_key: ''
    });
  };

  const testLLMConnection = async () => {
    if (!llmConfig.api_key) {
      setError('Please enter an API key first');
      return;
    }

    setIsTestingLLM(true);
    setTestResults(null);
    setError(null);

    const requestPayload = {
      provider: llmConfig.provider,
      model: llmConfig.model,
      api_key: llmConfig.api_key,
      temperature: llmConfig.temperature,
      max_tokens: llmConfig.max_tokens
    };

    try {
      const response = await api.post('/api/proficiency/test-llm', requestPayload);

      // Check if response has an error (from api.ts wrapper)
      if (response.error) {
        // Extract detailed error information
        let errorMessage = response.error;
        let errorDetails: any = {
          status: response.status,
          message: response.error
        };

        // Try to get more specific error information
        if (typeof response.error === 'string') {
          try {
            // In case error is a JSON string
            const parsedError = JSON.parse(response.error);
            errorMessage = parsedError.detail || parsedError.message || response.error;
            errorDetails = parsedError;
          } catch (e) {
            // Error is just a plain string
            errorMessage = response.error;
          }
        } else if (typeof response.error === 'object') {
          // Error is already an object
          errorMessage = response.error.detail || response.error.message || JSON.stringify(response.error);
          errorDetails = response.error;
        }

        setError(`Test failed (HTTP ${response.status}): ${errorMessage}`);

        // Store error details for debugging
        setTestResults({
          success: false,
          error: errorMessage,
          _debug: {
            request: requestPayload,
            error: {
              status: response.status,
              message: errorMessage,
              details: errorDetails,
              fullError: response.error
            },
            timestamp: new Date().toISOString()
          }
        });
        return;
      }

      if (response.data) {
        // Store both the result and full request/response for display
        setTestResults({
          ...response.data,
          _debug: {
            request: requestPayload,
            response: response.data,
            timestamp: new Date().toISOString()
          }
        });
        success('LLM Test Successful', `${llmConfig.provider} ${llmConfig.model} is working correctly`);
      } else {
        setError('Failed to test LLM connection: No data received');
      }
    } catch (err: any) {
      // Extract detailed error information
      let errorMessage = 'Unknown error occurred';
      let errorDetails: any = {};

      // Try multiple ways to extract the error message
      if (err.response) {
        // Axios-style error response
        errorDetails.status = err.response.status;
        errorDetails.statusText = err.response.statusText;
        errorDetails.data = err.response.data;

        // Extract the actual error message
        if (typeof err.response.data === 'object') {
          errorMessage = err.response.data.detail || err.response.data.message || JSON.stringify(err.response.data);
        } else if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        }
      } else if (err.message) {
        // Standard Error object
        errorMessage = err.message;
        errorDetails.type = err.name || 'Error';
      } else if (typeof err === 'string') {
        // String error
        errorMessage = err;
      } else {
        // Fallback to stringifying the error
        errorMessage = JSON.stringify(err);
      }

      setError(`Test failed: ${errorMessage}`);

      // Store comprehensive error details
      setTestResults({
        success: false,
        error: errorMessage,
        _debug: {
          request: requestPayload,
          error: {
            status: err.response?.status || 0,
            statusText: err.response?.statusText || 'Unknown',
            message: errorMessage,
            details: errorDetails,
            rawError: err
          },
          timestamp: new Date().toISOString()
        }
      });
    } finally {
      setIsTestingLLM(false);
    }
  };

  const handleContinue = () => {
    if (!llmConfig.api_key) {
      setError('Please configure an API key before proceeding');
      return;
    }

    if (skillsState.skills.length === 0) {
      setError('No skills found. Please go back to import skills first.');
      return;
    }

    // Testing is recommended but not required - show warning if not tested
    if (!testResults?.success && !testResults?.assessments) {
      showToastError('Recommended', 'Consider testing the LLM connection first, but you can proceed without testing.');
      // Allow proceeding after showing warning
    }

    // Store LLM config for the review step (localStorage for backward compatibility)
    localStorage.setItem('llmConfig', JSON.stringify(llmConfig));
    localStorage.setItem('promptTemplate', promptTemplate);
    localStorage.setItem('proficiencyLevels', JSON.stringify(proficiencyLevels));

    // Move to next step - configuration will be auto-saved with assessment results
    nextStep();
  };

  const copyPromptToClipboard = () => {
    navigator.clipboard.writeText(promptTemplate);
  };

  const selectedProvider = LLM_PROVIDERS.find(p => p.id === llmConfig.provider);

  return (
    <div className="max-w-7xl mx-auto p-8">
      <Card padding="lg">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-purple-100 to-indigo-100 dark:from-purple-900/30 dark:to-indigo-900/30 mb-4">
            <Settings className="w-8 h-8 text-purple-600 dark:text-purple-400" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Configure Proficiency Assessment
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            Set up proficiency levels, choose your LLM provider, and customize assessment prompts
          </p>
        </div>

        {/* Prompt Template Editor - Moved to top */}
        <Card className="mb-8 bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Edit3 className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                  Prompt Template
                </h3>
                <select
                  value={selectedPromptId}
                  onChange={(e) => {
                    const template = promptTemplates.find(t => t.id === e.target.value);
                    if (template) {
                      setSelectedPromptId(template.id);
                      setPromptTemplate(template.template);
                      success('Template Changed', `Switched to "${template.name}" template`);
                    }
                  }}
                  className="px-3 py-1.5 text-sm border border-orange-300 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  {promptTemplates.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name} {template.recommended ? '⭐' : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyPromptToClipboard}
                  className="text-orange-600 border-orange-300 hover:bg-orange-50"
                >
                  <Copy className="w-4 h-4" />
                  Copy
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setPromptTemplate(DEFAULT_PROMPT);
                    success('Prompt Reset', 'Prompt template reset to default with {skills} and {proficiency_levels}');
                  }}
                  className="text-blue-600 border-blue-300 hover:bg-blue-50"
                >
                  <RotateCcw className="w-4 h-4" />
                  Reset to Default
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowPromptEditor(!showPromptEditor)}
                  className="text-orange-600 border-orange-300 hover:bg-orange-50"
                >
                  <Code className="w-4 h-4" />
                  {showPromptEditor ? 'Hide Editor' : 'Show Editor'}
                </Button>
              </div>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
                  PREVIEW (with your actual skills and levels):
                </span>
                <span className="text-xs text-green-600 dark:text-green-400">
                  {skillsState.skills.length} skills loaded
                </span>
              </div>
              <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap max-h-48 overflow-y-auto border-l-4 border-blue-500 pl-3">
                {promptPreview.substring(0, 500)}{promptPreview.length > 500 ? '...' : ''}
              </pre>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 flex items-center gap-1">
                <Info className="w-3 h-3" />
                This preview updates automatically when skills or proficiency levels change. Click "Show Editor" to modify the template.
              </p>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Proficiency Levels Configuration */}
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  Proficiency Levels
                </h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={addProficiencyLevel}
                    className="text-blue-600 border-blue-300 hover:bg-blue-50"
                  >
                    <Plus className="w-4 h-4" />
                    Add Level
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={resetToDefaults}
                    className="text-gray-600 border-gray-300 hover:bg-gray-50"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Reset
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                {proficiencyLevels.map((level) => (
                  <div
                    key={level.level}
                    className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 dark:border-blue-800"
                  >
                    <div className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-600 text-white text-sm font-bold">
                      {level.level}
                    </div>
                    <div className="flex-1">
                      <input
                        type="text"
                        value={level.name}
                        onChange={(e) => updateProficiencyLevel(level.level, 'name', e.target.value)}
                        className="w-full text-sm font-semibold text-gray-900 dark:text-white bg-transparent border-none focus:ring-0 p-0 focus:outline-none"
                        placeholder={`Level ${level.level}`}
                      />
                      <input
                        type="text"
                        value={level.description}
                        onChange={(e) => updateProficiencyLevel(level.level, 'description', e.target.value)}
                        className="w-full text-xs text-gray-600 dark:text-gray-400 bg-transparent border-none focus:ring-0 p-0 mt-1 focus:outline-none"
                        placeholder="Level description"
                      />
                    </div>
                    {proficiencyLevels.length > 2 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeProficiencyLevel(level.level)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* Combined LLM Setup & Configuration */}
          <Card className="bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Brain className="w-5 h-5 text-green-600 dark:text-green-400" />
                  LLM Configuration
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setConfigManagerTab('load');
                    setShowConfigManager(true);
                  }}
                  className="text-green-600 border-green-300 hover:bg-green-50 dark:text-green-400 dark:border-green-700 dark:hover:bg-green-900/20"
                >
                  <Settings className="w-4 h-4" />
                  Configuration Manager
                </Button>
              </div>

              {/* LLM Configuration Section */}
              <div className="space-y-4">

                <Select
                  label="AI Provider"
                  value={llmConfig.provider}
                  onValueChange={(providerId) => {
                    const provider = LLM_PROVIDERS.find(p => p.id === providerId);
                    if (provider) {
                      // Set max_tokens based on provider limits
                      let maxTokens = llmConfig.max_tokens;
                      if (providerId === 'huggingface') {
                        // Hugging Face has a max of 8000 tokens
                        maxTokens = Math.min(8000, llmConfig.max_tokens);
                        setUnlimitedTokens(false); // Disable unlimited for HuggingFace
                      }

                      setLLMConfig({
                        ...llmConfig,
                        provider: providerId as any,
                        model: provider.models[0],
                        max_tokens: maxTokens
                      });
                    }
                  }}
                  options={LLM_PROVIDERS.map(provider => ({
                    value: provider.id,
                    label: provider.name,
                    description: provider.description,
                    icon: provider.icon,
                    badge: provider.free ? 'Free' : undefined
                  }))}
                  placeholder="Choose an AI provider"
                  required
                />

                {/* Model Selection */}
                {selectedProvider && (
                  <Select
                    label="Model"
                    value={llmConfig.model}
                    onValueChange={(model) => setLLMConfig({ ...llmConfig, model })}
                    options={selectedProvider.models.map(model => ({
                      value: model,
                      label: model === 'gemini-2.5-flash' ? 'Gemini 2.5 Flash' :
                             model === 'gemini-2.5-pro' ? 'Gemini 2.5 Pro' :
                             model,
                      description: model === 'gemini-2.5-flash' ? 'Fast, efficient, and versatile' :
                                  model === 'gemini-2.5-pro' ? 'Most capable reasoning model' :
                                  model.includes('flash') ? 'Fast and efficient' :
                                  model.includes('pro') ? 'Most capable' :
                                  model.includes('beta') ? 'Latest features' : undefined
                    }))}
                    placeholder="Select a model"
                    required
                  />
                )}

                {/* API Key Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    API Key
                  </label>
                  {(() => {
                    const providerKeys = savedAPIKeys.filter(k => k.provider === llmConfig.provider);

                    if (providerKeys.length > 0) {
                      return (
                        <div className="space-y-2">
                          <Select
                            value={selectedAPIKey?.keyId || 'manual'}
                            onValueChange={(value) => {
                              if (value === 'manual') {
                                setSelectedAPIKey(null);
                                setLLMConfig({ ...llmConfig, api_key: '' });
                              } else {
                                const key = providerKeys.find(k => k.id === value);
                                if (key) {
                                  setSelectedAPIKey({ provider: llmConfig.provider, keyId: value });
                                  setLLMConfig({
                                    ...llmConfig,
                                    api_key: key.key,
                                    model: key.model || llmConfig.model  // Use saved model if available
                                  });
                                }
                              }
                            }}
                            options={[
                              ...providerKeys.map(key => ({
                                value: key.id,
                                label: key.name,
                                description: `${key.key.substring(0, 8)}...${key.key.substring(key.key.length - 4)}`
                              })),
                              {
                                value: 'manual',
                                label: 'Enter manually',
                                description: 'Use a different API key'
                              }
                            ]}
                            placeholder="Select a saved API key"
                          />
                          {(!selectedAPIKey || selectedAPIKey.keyId === 'manual') && (
                            <div className="relative mt-2">
                              <input
                                type={showAPIKey ? 'text' : 'password'}
                                value={llmConfig.api_key}
                                onChange={(e) => setLLMConfig({ ...llmConfig, api_key: e.target.value })}
                                className="w-full px-3 py-2 pr-10 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm hover:border-green-400 focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                                placeholder="Enter your API key..."
                              />
                              <div className="absolute right-2 top-1/2 -translate-y-1/2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => setShowAPIKey(!showAPIKey)}
                                  className="h-6 w-6 p-0"
                                >
                                  {showAPIKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    } else {
                      return (
                        <div className="space-y-2">
                          <div className="relative">
                            <input
                              type={showAPIKey ? 'text' : 'password'}
                              value={llmConfig.api_key}
                              onChange={(e) => setLLMConfig({ ...llmConfig, api_key: e.target.value })}
                              className="w-full px-3 py-2 pr-10 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm hover:border-green-400 focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                              placeholder="Enter your API key..."
                            />
                            <div className="absolute right-2 top-1/2 -translate-y-1/2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowAPIKey(!showAPIKey)}
                                className="h-6 w-6 p-0"
                              >
                                {showAPIKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </Button>
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                            <Info className="w-3 h-3" />
                            No saved keys for {selectedProvider?.name}. Click "Manage Configs" to add one.
                          </p>
                        </div>
                      );
                    }
                  })()}
                </div>

                {/* Advanced Settings */}
                <div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="w-full justify-between"
                  >
                    Advanced Settings
                    {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>

                  {showAdvanced && (
                    <div className="mt-3 space-y-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Temperature: {llmConfig.temperature}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="2"
                          step="0.1"
                          value={llmConfig.temperature}
                          onChange={(e) => setLLMConfig({ ...llmConfig, temperature: parseFloat(e.target.value) })}
                          className={cn("w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer", styles.slider)}
                        />
                        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                          <span>Conservative (0.0)</span>
                          <span>Balanced (1.0)</span>
                          <span>Creative (2.0)</span>
                        </div>
                      </div>

                      {/* Unlimited Tokens Checkbox */}
                      <div className="flex items-center gap-2 p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                        <input
                          type="checkbox"
                          id="unlimited-tokens"
                          checked={unlimitedTokens}
                          disabled={llmConfig.provider === 'huggingface'}
                          onChange={(e) => {
                            setUnlimitedTokens(e.target.checked);
                            if (e.target.checked) {
                              setLLMConfig({ ...llmConfig, max_tokens: 100000 });
                            } else {
                              setLLMConfig({ ...llmConfig, max_tokens: 8000 });
                            }
                          }}
                          className={cn(
                            "w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 dark:focus:ring-green-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
                            llmConfig.provider === 'huggingface' && "opacity-50 cursor-not-allowed"
                          )}
                        />
                        <label
                          htmlFor="unlimited-tokens"
                          className={cn(
                            "text-sm font-medium cursor-pointer",
                            llmConfig.provider === 'huggingface'
                              ? "text-gray-400 dark:text-gray-600 cursor-not-allowed"
                              : "text-gray-700 dark:text-gray-300"
                          )}
                        >
                          Unlimited Output Tokens
                          {llmConfig.provider === 'huggingface' && (
                            <span className="ml-2 text-xs text-amber-600 dark:text-amber-400">
                              (Max 8000 for Hugging Face)
                            </span>
                          )}
                        </label>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Max Tokens {unlimitedTokens && <span className="text-xs text-gray-500">(Unlimited)</span>}
                          {llmConfig.provider === 'huggingface' && (
                            <span className="ml-2 text-xs text-amber-600 dark:text-amber-400">
                              (Max 8000)
                            </span>
                          )}
                        </label>
                        <input
                          type="number"
                          value={unlimitedTokens ? 100000 : llmConfig.max_tokens}
                          onChange={(e) => {
                            const value = parseInt(e.target.value);
                            // Enforce Hugging Face limit
                            const maxValue = llmConfig.provider === 'huggingface' ? 8000 : 100000;
                            setLLMConfig({ ...llmConfig, max_tokens: Math.min(value, maxValue) });
                          }}
                          disabled={unlimitedTokens}
                          className={cn(
                            "w-full px-3 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm hover:border-green-400 focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all",
                            unlimitedTokens && "opacity-50 cursor-not-allowed"
                          )}
                          min="100"
                          max={llmConfig.provider === 'huggingface' ? 8000 : 100000}
                          placeholder="8000"
                        />
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {unlimitedTokens
                            ? "Output tokens are unlimited - LLM will generate complete responses without truncation"
                            : llmConfig.provider === 'huggingface'
                            ? "Hugging Face models have a maximum of 8000 output tokens"
                            : "Recommended: 2000-4000 for brief assessments, 8000+ for detailed responses"
                          }
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Test Button */}
                <div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={testLLMConnection}
                    disabled={isTestingLLM || !llmConfig.api_key}
                    className="w-full"
                  >
                    {isTestingLLM ? <LoadingSpinner size="sm" /> : <Zap className="w-4 h-4" />}
                    Test Connection
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>


        {/* Test Results */}
        {testResults && (
          <Card className={cn(
            "mt-8",
            testResults.success === false
              ? "bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20"
              : "bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20"
          )}>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
                {testResults.success === false ? (
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                ) : (
                  <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                )}
                Test Results
              </h3>

              <div className="space-y-4">
                {/* Error Summary (if failed) */}
                {testResults.success === false && testResults._debug?.error && (
                  <div className="bg-red-100 dark:bg-red-900/30 border-2 border-red-300 dark:border-red-700 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-red-900 dark:text-red-100 mb-2 break-words">
                          Test Failed
                          {testResults._debug.error.status && testResults._debug.error.status !== 0 && (
                            <span className="ml-2 text-sm font-normal">
                              (HTTP {testResults._debug.error.status} - {testResults._debug.error.statusText})
                            </span>
                          )}
                        </h4>
                        <p className="text-sm text-red-800 dark:text-red-200 mb-3 break-words overflow-wrap-anywhere">
                          {testResults._debug.error.message || testResults.error || 'Unknown error'}
                        </p>
                        {testResults._debug.error.details && (
                          <div className="text-xs text-red-700 dark:text-red-300 space-y-1">
                            {testResults._debug.error.details.type && (
                              <div><strong>Error Type:</strong> {testResults._debug.error.details.type}</div>
                            )}
                            {testResults._debug.error.details.data && (
                              <div>
                                <strong>Backend Response:</strong>
                                <pre className="mt-1 p-2 bg-red-200 dark:bg-red-900/50 rounded overflow-auto max-w-full break-words whitespace-pre-wrap">
                                  {JSON.stringify(testResults._debug.error.details.data, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Success Summary */}
                {testResults.success !== false && testResults.response && (
                  <div className="bg-emerald-100 dark:bg-emerald-900/30 border-2 border-emerald-300 dark:border-emerald-700 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-emerald-900 dark:text-emerald-100 mb-2">
                          Connection Successful
                        </h4>
                        <p className="text-sm text-emerald-800 dark:text-emerald-200">
                          Successfully connected to {testResults.provider} using {testResults.model}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Request Section */}
                {testResults._debug?.request && (
                  <div>
                    <div className="font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                      <Code className="w-4 h-4" />
                      Request Payload:
                    </div>
                    <div className="bg-gray-900 text-blue-400 p-4 rounded-lg overflow-auto max-h-48">
                      <pre className="text-xs font-mono break-words whitespace-pre-wrap max-w-full">{JSON.stringify(testResults._debug.request, null, 2)}</pre>
                    </div>
                  </div>
                )}

                {/* Response Section */}
                {testResults._debug?.response && (
                  <div>
                    <div className="font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      Response:
                    </div>
                    <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto max-h-48">
                      <pre className="text-xs font-mono break-words whitespace-pre-wrap max-w-full">{JSON.stringify(testResults._debug.response, null, 2)}</pre>
                    </div>
                  </div>
                )}

                {/* Error Details Section */}
                {testResults._debug?.error && (
                  <div>
                    <div className="font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" />
                      Full Error Details:
                    </div>
                    <div className="bg-gray-900 text-red-400 p-4 rounded-lg overflow-auto max-h-64">
                      <pre className="text-xs font-mono break-words whitespace-pre-wrap max-w-full">{JSON.stringify(testResults._debug.error, null, 2)}</pre>
                    </div>
                  </div>
                )}

                {/* Full Results (fallback) */}
                {!testResults._debug && (
                  <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-sm font-mono break-words whitespace-pre-wrap max-w-full">{JSON.stringify(testResults, null, 2)}</pre>
                  </div>
                )}
              </div>
            </div>
          </Card>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-error-50 dark:bg-error-900/20 border-2 border-error-200 dark:border-error-800 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-error-600 dark:text-error-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-error-900 dark:text-error-100">Configuration Error</p>
                <p className="text-sm text-error-700 dark:text-error-300 mt-1 break-words overflow-wrap-anywhere">{error}</p>
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

        {/* Action Buttons */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="md"
              onClick={() => setCurrentStep(2)}
              className="border-2 border-teal-300 text-teal-600 hover:bg-teal-50 dark:border-teal-700 dark:text-teal-400 dark:hover:bg-teal-900/20 px-6 py-2.5"
            >
              ← Back to Extract Skills
            </Button>
            <Button
              variant="outline"
              size="md"
              onClick={() => {
                setConfigManagerTab('save');
                setNewConfigName(`${llmConfig.provider} ${llmConfig.model}`.substring(0, 50));
                setShowConfigManager(true);
              }}
              className="border-gray-300 dark:border-gray-600 px-6 py-2.5"
            >
              <Save className="w-4 h-4" />
              Save Configuration
            </Button>
          </div>

          <div className="flex flex-col items-end gap-2">
            {/* Status indicators */}
            <div className="flex items-center gap-4 text-sm">
              <div className={cn(
                "flex items-center gap-1",
                llmConfig.api_key ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
              )}>
                {llmConfig.api_key ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                API Key
              </div>
              <div className={cn(
                "flex items-center gap-1",
                skillsState.skills.length > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
              )}>
                {skillsState.skills.length > 0 ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                Skills ({skillsState.skills.length})
              </div>
              <div className={cn(
                "flex items-center gap-1",
                (testResults?.success || testResults?.assessments) ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"
              )}>
                {(testResults?.success || testResults?.assessments) ? <CheckCircle className="w-4 h-4" /> : <Info className="w-4 h-4" />}
                Test (Optional)
              </div>
            </div>

            <Button
              variant="primary"
              size="md"
              onClick={handleContinue}
              disabled={!llmConfig.api_key || skillsState.skills.length === 0}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg px-6 py-2.5"
            >
              Run Assessment
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>

      {/* Configuration Manager Modal */}
      {showConfigManager && (
        <ConfigurationManager
          currentConfig={{
            proficiencyLevels,
            llmConfig,
            promptTemplate
          }}
          onLoad={loadConfiguration}
          onClose={() => setShowConfigManager(false)}
          initialTab={configManagerTab}
          initialName={newConfigName}
        />
      )}

      {/* Prompt Template Editor Modal */}
      {showPromptEditor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-7xl max-h-[90vh] flex flex-col border-2 border-gray-200 dark:border-gray-700">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20 rounded-t-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                    <Edit3 className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      Edit Prompt Template
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Customize the AI assessment prompt
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowPromptEditor(false)}
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                </button>
              </div>
            </div>

            {/* Split View Editor */}
            <div className="flex-1 flex overflow-hidden">
              {/* Left: Template Editor */}
              <div className="flex-1 flex flex-col border-r border-gray-200 dark:border-gray-700">
                <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Template</h4>
                </div>
                <div className="flex-1 p-4">
                  <textarea
                    value={promptTemplate}
                    onChange={(e) => setPromptTemplate(e.target.value)}
                    className="w-full h-full px-4 py-3 text-sm font-mono border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-orange-500 resize-none"
                    placeholder="Enter your prompt template..."
                    spellCheck={false}
                  />
                </div>
              </div>

              {/* Right: Live Preview with Actual Data */}
              <div className="flex-1 flex flex-col">
                <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Preview with Actual Data</h4>
                  <span className="text-xs text-green-600 dark:text-green-400">
                    {skillsState.skills.length} skills • {proficiencyLevels.length} levels
                  </span>
                </div>
                <div className="flex-1 p-4 overflow-y-auto">
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">
                      {promptPreview}
                    </pre>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 rounded-b-xl flex justify-between items-center">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Character count: {promptTemplate.length}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowPromptEditor(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={() => {
                    setShowPromptEditor(false);
                    localStorage.setItem('promptTemplate', promptTemplate);
                  }}
                  className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600"
                >
                  <Save className="w-4 h-4" />
                  Save Changes
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manage Configs Modal */}
      {showManageConfigs && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col border-2 border-gray-200 dark:border-gray-700">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 rounded-t-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                    <Key className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      Manage API Configurations
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Add, edit, and manage your LLM API keys
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setShowManageConfigs(false);
                    // Reload saved keys after closing modal
                    const saved = localStorage.getItem('llm_api_keys');
                    if (saved) {
                      setSavedAPIKeys(JSON.parse(saved));
                    }
                  }}
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                {/* Info Banner */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                        Manage Your API Keys
                      </h4>
                      <p className="text-sm text-blue-700 dark:text-blue-300">
                        Add and organize API keys for different LLM providers. Your keys are securely stored locally and can be used across all assessments.
                      </p>
                    </div>
                  </div>
                </div>

                {/* API Key Manager Component */}
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                  <APIKeyManager
                    onKeySelect={(provider, keyId) => {
                      setSelectedAPIKey({ provider, keyId });
                      const savedKeys = JSON.parse(localStorage.getItem('llm_api_keys') || '[]');
                      const selectedKey = savedKeys.find((k: any) => k.id === keyId && k.provider === provider);
                      if (selectedKey) {
                        setLLMConfig(prev => ({
                          ...prev,
                          provider: provider as any,
                          api_key: selectedKey.key,
                          model: selectedKey.model || prev.model  // Use saved model if available
                        }));
                      }
                    }}
                    selectedProvider={selectedAPIKey?.provider}
                    selectedKeyId={selectedAPIKey?.keyId}
                  />
                </div>

                {/* Provider Information Cards */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                    Supported Providers
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {LLM_PROVIDERS.map(provider => (
                      <div
                        key={provider.id}
                        className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-700 transition-colors"
                      >
                        <div className="flex items-start gap-3">
                          <div className="text-2xl">{provider.icon}</div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h5 className="text-sm font-semibold text-gray-900 dark:text-white">
                                {provider.name}
                              </h5>
                              {provider.free && (
                                <span className="px-2 py-0.5 text-xs font-semibold bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-pill">
                                  Free Tier
                                </span>
                              )}
                            </div>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                              {provider.description}
                            </p>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {savedAPIKeys.filter(k => k.provider === provider.id).length} saved key(s)
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 rounded-b-xl flex justify-between items-center">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Total API Keys: {savedAPIKeys.length}
              </div>
              <Button
                variant="primary"
                onClick={() => {
                  setShowManageConfigs(false);
                  // Reload saved keys after closing modal
                  const saved = localStorage.getItem('llm_api_keys');
                  if (saved) {
                    setSavedAPIKeys(JSON.parse(saved));
                  }
                }}
                className="bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600"
              >
                Done
              </Button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ConfigureProficiency;