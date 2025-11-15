import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { apiClient } from '../../utils/api';

interface APIKey {
  id: string;
  provider: 'google' | 'openai' | 'anthropic' | 'grok';
  name: string;
  key: string;
  status: 'untested' | 'valid' | 'invalid' | 'testing';
  created_at: string;
  last_tested?: string;
}

interface APIKeyManagerProps {
  onKeySelect?: (provider: string, keyId: string) => void;
  selectedProvider?: string;
  selectedKeyId?: string;
}

const PROVIDER_INFO = {
  google: { name: 'Google Gemini', icon: '✨', color: 'blue' },
  openai: { name: 'OpenAI', icon: '🤖', color: 'green' },
  anthropic: { name: 'Anthropic', icon: '🧠', color: 'purple' },
  grok: { name: 'Grok (xAI)', icon: '🚀', color: 'orange' }
};

export const APIKeyManager: React.FC<APIKeyManagerProps> = ({
  onKeySelect,
  selectedProvider,
  selectedKeyId
}) => {
  const [keys, setKeys] = useState<APIKey[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newKey, setNewKey] = useState({
    provider: 'google' as keyof typeof PROVIDER_INFO,
    name: '',
    key: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadKeys();
  }, []);

  const loadKeys = async () => {
    try {
      const savedKeys = localStorage.getItem('llm_api_keys');
      if (savedKeys) {
        setKeys(JSON.parse(savedKeys));
      }

      // Load default Gemini key if exists
      const defaultGeminiKey: APIKey = {
        id: 'default-gemini',
        provider: 'google',
        name: 'Default Gemini Key',
        key: 'AIzaSyB5SgAyxG2tdSQBF_QtsvM7MLv8hjZAWDY',
        status: 'untested',
        created_at: new Date().toISOString()
      };

      const existingKeys = savedKeys ? JSON.parse(savedKeys) : [];
      if (!existingKeys.find((k: APIKey) => k.id === 'default-gemini')) {
        const updatedKeys = [defaultGeminiKey, ...existingKeys];
        setKeys(updatedKeys);
        localStorage.setItem('llm_api_keys', JSON.stringify(updatedKeys));
      }
    } catch (err) {
      console.error('Failed to load API keys:', err);
    }
  };

  const saveKeys = (updatedKeys: APIKey[]) => {
    setKeys(updatedKeys);
    localStorage.setItem('llm_api_keys', JSON.stringify(updatedKeys));
  };

  const addKey = () => {
    if (!newKey.name || !newKey.key) {
      setError('Name and API key are required');
      return;
    }

    const keyToAdd: APIKey = {
      id: `${newKey.provider}-${Date.now()}`,
      provider: newKey.provider,
      name: newKey.name,
      key: newKey.key,
      status: 'untested',
      created_at: new Date().toISOString()
    };

    const updatedKeys = [keyToAdd, ...keys];
    saveKeys(updatedKeys);

    setNewKey({ provider: 'google', name: '', key: '' });
    setShowAddForm(false);
    setError(null);
  };

  const testKey = async (keyId: string) => {
    const keyToTest = keys.find(k => k.id === keyId);
    if (!keyToTest) return;

    setKeys(keys.map(k =>
      k.id === keyId ? { ...k, status: 'testing' } : k
    ));

    try {
      const response = await apiClient.post('/api/llm/test-key', {
        provider: keyToTest.provider,
        api_key: keyToTest.key
      });

      const isValid = response.data?.valid === true;
      const updatedKeys = keys.map(k =>
        k.id === keyId
          ? {
              ...k,
              status: isValid ? 'valid' : 'invalid',
              last_tested: new Date().toISOString()
            }
          : k
      );
      saveKeys(updatedKeys);
    } catch (err) {
      const updatedKeys = keys.map(k =>
        k.id === keyId
          ? {
              ...k,
              status: 'invalid',
              last_tested: new Date().toISOString()
            }
          : k
      );
      saveKeys(updatedKeys);
    }
  };

  const deleteKey = (keyId: string) => {
    if (keyId === 'default-gemini') {
      setError('Cannot delete the default Gemini key');
      return;
    }

    const updatedKeys = keys.filter(k => k.id !== keyId);
    saveKeys(updatedKeys);
  };

  const getStatusColor = (status: APIKey['status']) => {
    switch (status) {
      case 'valid': return 'text-green-600 bg-green-100';
      case 'invalid': return 'text-red-600 bg-red-100';
      case 'testing': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: APIKey['status']) => {
    switch (status) {
      case 'valid': return '✓ Valid';
      case 'invalid': return '✗ Invalid';
      case 'testing': return '⟳ Testing...';
      default: return '? Untested';
    }
  };

  return (
    <Card padding="lg">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">LLM API Keys</h3>
          <p className="text-sm text-gray-600 mt-1">
            Manage your API keys for different LLM providers
          </p>
        </div>
        <Button
          onClick={() => setShowAddForm(true)}
          size="sm"
          disabled={showAddForm}
        >
          + Add Key
        </Button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {showAddForm && (
        <Card padding="md" className="mb-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Provider
              </label>
              <select
                value={newKey.provider}
                onChange={(e) => setNewKey({ ...newKey, provider: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {Object.entries(PROVIDER_INFO).map(([key, info]) => (
                  <option key={key} value={key}>
                    {info.icon} {info.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key Name
              </label>
              <input
                type="text"
                value={newKey.name}
                onChange={(e) => setNewKey({ ...newKey, name: e.target.value })}
                placeholder="e.g., Production Gemini Key"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={newKey.key}
                onChange={(e) => setNewKey({ ...newKey, key: e.target.value })}
                placeholder="Enter your API key..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex space-x-2">
              <Button onClick={addKey} size="sm">
                Add Key
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowAddForm(false);
                  setError(null);
                  setNewKey({ provider: 'google', name: '', key: '' });
                }}
                size="sm"
              >
                Cancel
              </Button>
            </div>
          </div>
        </Card>
      )}

      <div className="space-y-3">
        {keys.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No API keys configured. Add one to get started.
          </div>
        ) : (
          keys.map((key) => {
            const provider = PROVIDER_INFO[key.provider];
            const isSelected = selectedProvider === key.provider && selectedKeyId === key.id;

            return (
              <div
                key={key.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => onKeySelect?.(key.provider, key.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{provider.icon}</div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">{key.name}</span>
                        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(key.status)}`}>
                          {getStatusText(key.status)}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {provider.name} • {key.key.substring(0, 8)}...
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        testKey(key.id);
                      }}
                      size="sm"
                      variant="outline"
                      disabled={key.status === 'testing'}
                    >
                      {key.status === 'testing' ? 'Testing...' : 'Test'}
                    </Button>

                    {key.id !== 'default-gemini' && (
                      <Button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteKey(key.id);
                        }}
                        size="sm"
                        variant="outline"
                        className="text-red-600 hover:text-red-700"
                      >
                        Delete
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
};

export default APIKeyManager;