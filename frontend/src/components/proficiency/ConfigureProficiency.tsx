/**
 * Configure Proficiency Component - Step 3
 * Configure proficiency levels, LLM provider, and assessment prompts
 */

import React, { useState, useEffect } from 'react';
import {
  Settings, Zap, Brain, Edit3, Plus, Trash2, Save, RotateCcw,
  ChevronDown, ChevronUp, CheckCircle, AlertCircle, Info,
  Sliders, Code, Play, Eye, EyeOff, Key, Copy
} from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { cn } from '../../utils/cn';
import api from '../../utils/api';
import APIKeyManager from '../keys/APIKeyManager';

interface ProficiencyLevel {
  level: number;
  name: string;
  description: string;
  color: string;
}

interface LLMConfig {
  provider: 'openai' | 'anthropic' | 'google' | 'grok';
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
  { level: 1, name: 'Novice', description: 'Less than 6 months experience, basic understanding', color: 'bg-gray-500' },
  { level: 2, name: 'Developing', description: '6 months to 1 year, can work with guidance', color: 'bg-blue-500' },
  { level: 3, name: 'Intermediate', description: '1-3 years experience, works independently', color: 'bg-yellow-500' },
  { level: 4, name: 'Advanced', description: '3-5 years experience, deep expertise', color: 'bg-green-500' },
  { level: 5, name: 'Expert', description: '5+ years, thought leader, teaches others', color: 'bg-purple-500' }
];

const DEFAULT_PROMPT = `You are an expert skills assessor. Assign proficiency levels (1-5) for these skills based on industry standards.

Proficiency Levels:
1 = Novice (0-20% mastery, basic awareness, needs supervision)
2 = Developing (21-40% mastery, fundamental concepts, occasional guidance)
3 = Intermediate (41-60% mastery, solid working knowledge, works independently)
4 = Advanced (61-80% mastery, comprehensive expertise, mentors others)
5 = Expert (81-100% mastery, industry thought leader, innovates)

Skills to assess: {skills_to_assess}
--
Consider: skill complexity, industry standards, typical learning time, market demand.
Return ONLY valid JSON with ALL skills assessed.

Required JSON format:
{
  "assessments": [
    {
      "skill_name": "skill name here",
      "proficiency": number_between_1_and_5,
      "confidence_score": 0.0_to_1.0,
      "reasoning": "explanation for proficiency level",
      "evidence": ["evidence point 1", "evidence point 2"]
    }
  ]
}

{text}

{context}`;

const LLM_PROVIDERS = [
  {
    id: 'google',
    name: 'Google Gemini',
    description: 'Gemini Pro 2.5, fast and FREE',
    models: ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash'],
    icon: '✨',
    recommended: true,
    free: true
  },
  {
    id: 'grok',
    name: 'Grok (xAI)',
    description: 'Fast, free tier available',
    models: ['grok-beta'],
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
  }
];

export const ConfigureProficiency: React.FC = () => {
  const { skillsState, nextStep, setIsLoading, setError, isLoading, error } = useApp();

  // State
  const [proficiencyLevels, setProficiencyLevels] = useState<ProficiencyLevel[]>(DEFAULT_PROFICIENCY_LEVELS);
  const [llmConfig, setLLMConfig] = useState<LLMConfig>({
    provider: 'google',
    model: 'gemini-2.0-flash-exp',
    temperature: 0.7,
    max_tokens: 2000,
    api_key: ''
  });
  const [promptTemplate, setPromptTemplate] = useState<string>(DEFAULT_PROMPT);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showPromptEditor, setShowPromptEditor] = useState(false);
  const [showAPIKey, setShowAPIKey] = useState(false);
  const [testResults, setTestResults] = useState<any>(null);
  const [isTestingLLM, setIsTestingLLM] = useState(false);

  // Load saved configuration on mount
  useEffect(() => {
    loadSavedConfiguration();
  }, []);

  const loadSavedConfiguration = () => {
    try {
      const saved = localStorage.getItem('profstudio_proficiency_config');
      if (saved) {
        const config = JSON.parse(saved);
        if (config.proficiencyLevels) setProficiencyLevels(config.proficiencyLevels);
        if (config.llmConfig) setLLMConfig(config.llmConfig);
        if (config.promptTemplate) setPromptTemplate(config.promptTemplate);
      }
    } catch (err) {
      console.error('Error loading saved configuration:', err);
    }
  };

  const saveConfiguration = () => {
    try {
      const config = {
        proficiencyLevels,
        llmConfig,
        promptTemplate,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem('profstudio_proficiency_config', JSON.stringify(config));
      return true;
    } catch (err) {
      console.error('Error saving configuration:', err);
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

    try {
      const response = await api.post('/api/proficiency/test-llm', {
        provider: llmConfig.provider,
        model: llmConfig.model,
        api_key: llmConfig.api_key,
        temperature: llmConfig.temperature,
        max_tokens: llmConfig.max_tokens
      });

      if (response.data) {
        setTestResults(response.data);
      } else {
        setError(response.error || 'Failed to test LLM connection');
      }
    } catch (err: any) {
      setError(`Test failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsTestingLLM(false);
    }
  };

  const runSampleAssessment = async () => {
    setIsTestingLLM(true);
    setTestResults(null);
    setError(null);

    try {
      const sampleSkills = skillsState.skills.slice(0, 3); // Test with first 3 skills
      const response = await api.post('/api/proficiency/test-assessment', {
        skills: sampleSkills,
        proficiency_levels: proficiencyLevels,
        llm_config: llmConfig,
        prompt_template: promptTemplate,
        sample_text: 'Sample professional with 3 years of experience in software development, proficient in Python and JavaScript, with knowledge of databases and web technologies.'
      });

      if (response.data) {
        setTestResults(response.data);
      } else {
        setError(response.error || 'Failed to run sample assessment');
      }
    } catch (err: any) {
      setError(`Assessment test failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsTestingLLM(false);
    }
  };

  const handleContinue = () => {
    if (!llmConfig.api_key) {
      setError('Please configure an API key before proceeding');
      return;
    }

    if (!testResults?.success && !testResults?.assessments) {
      setError('Please test the LLM connection or run a sample assessment before proceeding');
      return;
    }

    const saved = saveConfiguration();
    if (saved) {
      // Store LLM config for the review step
      localStorage.setItem('llmConfig', JSON.stringify(llmConfig));
      localStorage.setItem('promptTemplate', promptTemplate);
      localStorage.setItem('proficiencyLevels', JSON.stringify(proficiencyLevels));
      nextStep();
    } else {
      setError('Failed to save configuration');
    }
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

              <div className="space-y-3 max-h-64 overflow-y-auto">
                {proficiencyLevels.map((level) => (
                  <div
                    key={level.level}
                    className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 dark:border-blue-800"
                  >
                    <div className={cn("w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold", level.color)}>
                      {level.level}
                    </div>
                    <div className="flex-1">
                      <input
                        type="text"
                        value={level.name}
                        onChange={(e) => updateProficiencyLevel(level.level, 'name', e.target.value)}
                        className="w-full text-sm font-medium text-gray-900 dark:text-white bg-transparent border-none focus:ring-0 p-0"
                        placeholder="Level name"
                      />
                      <input
                        type="text"
                        value={level.description}
                        onChange={(e) => updateProficiencyLevel(level.level, 'description', e.target.value)}
                        className="w-full text-xs text-gray-600 dark:text-gray-400 bg-transparent border-none focus:ring-0 p-0 mt-1"
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

          {/* API Key Management */}
          <APIKeyManager />

          {/* LLM Configuration */}
          <Card className="bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
                <Brain className="w-5 h-5 text-green-600 dark:text-green-400" />
                LLM Configuration
              </h3>

              {/* Provider Selection */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    AI Provider
                  </label>
                  <div className="grid grid-cols-1 gap-2">
                    {LLM_PROVIDERS.map((provider) => (
                      <div
                        key={provider.id}
                        className={cn(
                          "p-3 rounded-lg border cursor-pointer transition-all",
                          llmConfig.provider === provider.id
                            ? "border-green-500 bg-green-50 dark:bg-green-900/30"
                            : "border-gray-200 dark:border-gray-700 hover:border-green-300"
                        )}
                        onClick={() => setLLMConfig({ ...llmConfig, provider: provider.id as any, model: provider.models[0] })}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-lg">{provider.icon}</span>
                          <div className="flex-1">
                            <p className="font-medium text-gray-900 dark:text-white">{provider.name}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{provider.description}</p>
                          </div>
                          {llmConfig.provider === provider.id && (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Model Selection */}
                {selectedProvider && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Model
                    </label>
                    <select
                      value={llmConfig.model}
                      onChange={(e) => setLLMConfig({ ...llmConfig, model: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      {selectedProvider.models.map((model) => (
                        <option key={model} value={model}>{model}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* API Key */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showAPIKey ? 'text' : 'password'}
                      value={llmConfig.api_key}
                      onChange={(e) => setLLMConfig({ ...llmConfig, api_key: e.target.value })}
                      className="w-full px-3 py-2 pr-20 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="Enter your API key..."
                    />
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1">
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
                        <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                          Temperature: {llmConfig.temperature}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="2"
                          step="0.1"
                          value={llmConfig.temperature}
                          onChange={(e) => setLLMConfig({ ...llmConfig, temperature: parseFloat(e.target.value) })}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">Max Tokens</label>
                        <input
                          type="number"
                          value={llmConfig.max_tokens}
                          onChange={(e) => setLLMConfig({ ...llmConfig, max_tokens: parseInt(e.target.value) })}
                          className="w-full px-2 py-1 text-sm border rounded"
                          min="100"
                          max="8000"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Test Buttons */}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={testLLMConnection}
                    disabled={isTestingLLM || !llmConfig.api_key}
                    className="flex-1"
                  >
                    {isTestingLLM ? <LoadingSpinner size="sm" /> : <Zap className="w-4 h-4" />}
                    Test Connection
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={runSampleAssessment}
                    disabled={isTestingLLM || !llmConfig.api_key || skillsState.skills.length === 0}
                    className="flex-1"
                  >
                    {isTestingLLM ? <LoadingSpinner size="sm" /> : <Play className="w-4 h-4" />}
                    Test Assessment
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Prompt Template Editor */}
        <Card className="mt-8 bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                Prompt Template
              </h3>
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
                  onClick={() => setShowPromptEditor(!showPromptEditor)}
                  className="text-orange-600 border-orange-300 hover:bg-orange-50"
                >
                  <Code className="w-4 h-4" />
                  {showPromptEditor ? 'Hide Editor' : 'Show Editor'}
                </Button>
              </div>
            </div>

            {showPromptEditor ? (
              <div>
                <textarea
                  value={promptTemplate}
                  onChange={(e) => setPromptTemplate(e.target.value)}
                  className="w-full h-64 px-3 py-2 text-sm font-mono border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="Enter your prompt template..."
                />
                <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                  <p>Available variables: {'{text}'}, {'{context}'}, {'{skills}'}, {'{proficiency_levels}'}</p>
                </div>
              </div>
            ) : (
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap max-h-32 overflow-y-auto">
                  {promptTemplate.substring(0, 300)}...
                </pre>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Click "Show Editor" to modify the prompt template
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Test Results */}
        {testResults && (
          <Card className="mt-8 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
                <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                Test Results
              </h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto max-h-64">
                <pre className="text-sm font-mono">{JSON.stringify(testResults, null, 2)}</pre>
              </div>
            </div>
          </Card>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-error-50 dark:bg-error-900/20 border-2 border-error-200 dark:border-error-800 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-error-600 dark:text-error-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold text-error-900 dark:text-error-100">Configuration Error</p>
                <p className="text-sm text-error-700 dark:text-error-300 mt-1">{error}</p>
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
              onClick={saveConfiguration}
              className="border-gray-300 dark:border-gray-600"
            >
              <Save className="w-4 h-4" />
              Save Configuration
            </Button>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <Info className="w-4 h-4 inline mr-1" />
              Configuration will be saved automatically when proceeding
            </div>
          </div>

          <Button
            variant="primary"
            size="lg"
            onClick={handleContinue}
            disabled={!llmConfig.api_key || skillsState.skills.length === 0}
            className="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600"
          >
            <Zap className="w-5 h-5" />
            Run Assessment
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default ConfigureProficiency;