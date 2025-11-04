/**
 * Settings Panel Component
 * Configure API keys and vector database settings
 */

import React, { useState, useEffect } from 'react';
import { Settings, Key, Database, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

interface VectorDBOption {
  id: string;
  name: string;
  description: string;
  requires_api_key: boolean;
  recommended: boolean;
}

interface AIProviderOption {
  id: string;
  name: string;
  description: string;
  requires_api_key: boolean;
  recommended: boolean;
}

interface ConfigData {
  vector_db: {
    type: string;
    options: VectorDBOption[];
  };
  ai_inference: {
    enabled: boolean;
    provider: string;
    options: AIProviderOption[];
  };
  api_keys: {
    gemini_configured: boolean;
    openai_configured: boolean;
    pinecone_configured: boolean;
  };
}

const SettingsPanel: React.FC = () => {
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  // Form state
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [pineconeApiKey, setPineconeApiKey] = useState('');
  const [selectedVectorDB, setSelectedVectorDB] = useState('chromadb');
  const [selectedAIProvider, setSelectedAIProvider] = useState('gemini');
  const [testingConnection, setTestingConnection] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/config');
      setConfig(response.data);
      setSelectedVectorDB(response.data.vector_db.type);
      setSelectedAIProvider(response.data.ai_inference.provider);
      setLoading(false);
    } catch (error) {
      console.error('Error loading config:', error);
      setMessage({ type: 'error', text: 'Failed to load configuration' });
      setLoading(false);
    }
  };

  const saveApiKey = async (key: string, value: string) => {
    if (!value.trim()) {
      setMessage({ type: 'error', text: 'API key cannot be empty' });
      return;
    }

    setSaving(true);
    try {
      await axios.post('http://localhost:8000/api/config/api-key', {
        key: key,
        value: value
      });
      setMessage({ type: 'success', text: `${key} saved successfully!` });
      loadConfig(); // Reload config
    } catch (error) {
      console.error('Error saving API key:', error);
      setMessage({ type: 'error', text: 'Failed to save API key' });
    } finally {
      setSaving(false);
    }
  };

  const saveVectorDB = async (dbType: string) => {
    setSaving(true);
    try {
      await axios.post('http://localhost:8000/api/config/vector-db', {
        key: 'VECTOR_DB_TYPE',
        value: dbType
      });
      setMessage({ type: 'success', text: `Vector database changed to ${dbType}` });
      setSelectedVectorDB(dbType);
      loadConfig();
    } catch (error) {
      console.error('Error saving vector DB:', error);
      setMessage({ type: 'error', text: 'Failed to save vector database setting' });
    } finally {
      setSaving(false);
    }
  };

  const saveAIProvider = async (provider: string) => {
    setSaving(true);
    try {
      await axios.post('http://localhost:8000/api/config/ai-provider', {
        key: 'AI_INFERENCE_PROVIDER',
        value: provider
      });
      setMessage({ type: 'success', text: `AI provider changed to ${provider}` });
      setSelectedAIProvider(provider);
      loadConfig();
    } catch (error) {
      console.error('Error saving AI provider:', error);
      setMessage({ type: 'error', text: 'Failed to save AI provider setting' });
    } finally {
      setSaving(false);
    }
  };

  const testAPIConnection = async (provider: string) => {
    setTestingConnection(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/config/test-api-key?provider=${provider}`);
      if (response.data.valid) {
        setMessage({ type: 'success', text: `${provider} API key is valid!` });
      } else {
        setMessage({ type: 'error', text: `${provider} API key is invalid: ${response.data.message}` });
      }
    } catch (error) {
      console.error('Error testing connection:', error);
      setMessage({ type: 'error', text: 'Failed to test connection' });
    } finally {
      setTestingConnection(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Settings className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">Configure API keys and vector database</p>
          </div>
        </div>

        {/* Message Banner */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-start gap-3 ${
            message.type === 'success' ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' :
            message.type === 'error' ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' :
            'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
          }`}>
            {message.type === 'success' && <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />}
            {message.type === 'error' && <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />}
            {message.type === 'info' && <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />}
            <p className={`text-sm ${
              message.type === 'success' ? 'text-green-800 dark:text-green-200' :
              message.type === 'error' ? 'text-red-800 dark:text-red-200' :
              'text-blue-800 dark:text-blue-200'
            }`}>{message.text}</p>
          </div>
        )}

        <div className="space-y-6">
          {/* API Keys Section */}
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Key className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">API Keys</h2>
            </div>

            <div className="space-y-4">
              {/* Google Gemini */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Google Gemini API Key
                  {config?.api_keys.gemini_configured && (
                    <span className="ml-2 text-xs text-green-600 dark:text-green-400">✓ Configured</span>
                  )}
                </label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={geminiApiKey}
                    onChange={(e) => setGeminiApiKey(e.target.value)}
                    placeholder="Enter your Gemini API key"
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-800 dark:text-white"
                  />
                  <button
                    onClick={() => saveApiKey('GEMINI_API_KEY', geminiApiKey)}
                    disabled={saving || !geminiApiKey}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => testAPIConnection('gemini')}
                    disabled={testingConnection || !config?.api_keys.gemini_configured}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Test
                  </button>
                </div>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Get your API key from{' '}
                  <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-indigo-600 dark:text-indigo-400 hover:underline">
                    Google AI Studio
                  </a>
                </p>
              </div>

              {/* OpenAI (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  OpenAI API Key (Optional)
                  {config?.api_keys.openai_configured && (
                    <span className="ml-2 text-xs text-green-600 dark:text-green-400">✓ Configured</span>
                  )}
                </label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={openaiApiKey}
                    onChange={(e) => setOpenaiApiKey(e.target.value)}
                    placeholder="Enter your OpenAI API key"
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-800 dark:text-white"
                  />
                  <button
                    onClick={() => saveApiKey('OPENAI_API_KEY', openaiApiKey)}
                    disabled={saving || !openaiApiKey}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Save
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* AI Provider Selection */}
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertCircle className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Inference Provider</h2>
            </div>

            <div className="space-y-3">
              {config?.ai_inference.options.map((provider) => (
                <label
                  key={provider.id}
                  className={`flex items-start gap-3 p-4 border rounded-lg cursor-pointer transition ${
                    selectedAIProvider === provider.id
                      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                      : 'border-gray-300 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700'
                  }`}
                >
                  <input
                    type="radio"
                    name="ai-provider"
                    value={provider.id}
                    checked={selectedAIProvider === provider.id}
                    onChange={(e) => saveAIProvider(e.target.value)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 dark:text-white">{provider.name}</span>
                      {provider.recommended && (
                        <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                          Recommended
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{provider.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Vector Database Selection */}
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Database className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Vector Database</h2>
            </div>

            <div className="space-y-3">
              {config?.vector_db.options.map((db) => (
                <label
                  key={db.id}
                  className={`flex items-start gap-3 p-4 border rounded-lg cursor-pointer transition ${
                    selectedVectorDB === db.id
                      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                      : 'border-gray-300 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700'
                  }`}
                >
                  <input
                    type="radio"
                    name="vector-db"
                    value={db.id}
                    checked={selectedVectorDB === db.id}
                    onChange={(e) => saveVectorDB(e.target.value)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 dark:text-white">{db.name}</span>
                      {db.recommended && (
                        <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                          Recommended
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{db.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
