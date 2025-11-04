/**
 * SFTP Credential Manager
 * Manage SFTP credentials for remote file uploads
 */

import React, { useState, useEffect } from 'react';
import { Server, Plus, Trash2, Edit2, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { useToast } from '../../contexts/ToastContext';
import {
  getSFTPCredentials,
  addSFTPCredential,
  updateSFTPCredential,
  deleteSFTPCredential,
  testSFTPConnection,
  type SFTPCredential,
  type SFTPCredentialInput
} from '../../services/sftp-api';

export const SFTPCredentialManager: React.FC = () => {
  const [credentials, setCredentials] = useState<SFTPCredential[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingCredential, setEditingCredential] = useState<SFTPCredential | null>(null);
  const [testingConnection, setTestingConnection] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    loadCredentials();
  }, []);

  const loadCredentials = async () => {
    try {
      setLoading(true);
      const creds = await getSFTPCredentials();
      setCredentials(creds);
    } catch (error: any) {
      toast.error('Failed to load SFTP credentials', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCredential = async (input: SFTPCredentialInput) => {
    try {
      await addSFTPCredential(input);
      toast.success('SFTP credential added', 'Connection saved successfully');
      setShowAddModal(false);
      loadCredentials();
    } catch (error: any) {
      toast.error('Failed to add credential', error.message);
    }
  };

  const handleUpdateCredential = async (id: string, input: SFTPCredentialInput) => {
    try {
      await updateSFTPCredential(id, input);
      toast.success('Credential updated', 'Changes saved successfully');
      setEditingCredential(null);
      loadCredentials();
    } catch (error: any) {
      toast.error('Failed to update credential', error.message);
    }
  };

  const handleDeleteCredential = async (id: string, name: string) => {
    if (!confirm(`Delete SFTP connection "${name}"?`)) return;

    try {
      await deleteSFTPCredential(id);
      toast.success('Credential deleted', `Removed "${name}" connection`);
      loadCredentials();
    } catch (error: any) {
      toast.error('Failed to delete credential', error.message);
    }
  };

  const handleTestConnection = async (id: string, name: string) => {
    try {
      setTestingConnection(id);
      const result = await testSFTPConnection(id);

      if (result.success) {
        toast.success('Connection successful', `Connected to "${name}"`);
      } else {
        toast.error('Connection failed', result.error || 'Could not connect to server');
      }
    } catch (error: any) {
      toast.error('Connection test failed', error.message);
    } finally {
      setTestingConnection(null);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">SFTP Connections</h2>
          <p className="text-gray-600 dark:text-gray-300 mt-1">
            Manage remote server connections for file uploads
          </p>
        </div>
        <Button
          variant="primary"
          size="lg"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => setShowAddModal(true)}
        >
          Add Connection
        </Button>
      </div>

      {credentials.length === 0 ? (
        <Card>
          <CardContent>
            <div className="text-center py-12">
              <Server className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                No SFTP connections configured
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Add your first SFTP connection to enable remote file uploads
              </p>
              <Button
                variant="primary"
                leftIcon={<Plus className="w-4 h-4" />}
                onClick={() => setShowAddModal(true)}
              >
                Add Connection
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {credentials.map((credential) => (
            <Card key={credential.id}>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                      <Server className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {credential.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                        {credential.username}@{credential.host}:{credential.port}
                      </p>
                      {credential.remote_path && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          Path: {credential.remote_path}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {credential.connection_status === 'connected' && (
                      <span className="flex items-center gap-1 text-sm text-success-600 dark:text-success-400">
                        <CheckCircle className="w-4 h-4" />
                        Connected
                      </span>
                    )}
                    {credential.connection_status === 'failed' && (
                      <span className="flex items-center gap-1 text-sm text-error-600 dark:text-error-400">
                        <XCircle className="w-4 h-4" />
                        Failed
                      </span>
                    )}

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleTestConnection(credential.id, credential.name)}
                      disabled={testingConnection === credential.id}
                    >
                      {testingConnection === credential.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        'Test'
                      )}
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditingCredential(credential)}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteCredential(credential.id, credential.name)}
                      className="text-error-600 hover:text-error-700 hover:border-error-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      {(showAddModal || editingCredential) && (
        <SFTPCredentialModal
          credential={editingCredential}
          onSave={(input) => {
            if (editingCredential) {
              handleUpdateCredential(editingCredential.id, input);
            } else {
              handleAddCredential(input);
            }
          }}
          onClose={() => {
            setShowAddModal(false);
            setEditingCredential(null);
          }}
        />
      )}
    </div>
  );
};

// SFTP Credential Modal
interface SFTPCredentialModalProps {
  credential: SFTPCredential | null;
  onSave: (input: SFTPCredentialInput) => void;
  onClose: () => void;
}

const SFTPCredentialModal: React.FC<SFTPCredentialModalProps> = ({
  credential,
  onSave,
  onClose,
}) => {
  const [formData, setFormData] = useState<SFTPCredentialInput>({
    name: credential?.name || '',
    host: credential?.host || '',
    port: credential?.port || 22,
    username: credential?.username || '',
    password: '',
    remote_path: credential?.remote_path || '/',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200 dark:border-gray-800">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              {credential ? 'Edit' : 'Add'} SFTP Connection
            </h2>
          </div>

          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Connection Name *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Production Server"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                  Host *
                </label>
                <input
                  type="text"
                  required
                  value={formData.host}
                  onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="ftp.example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                  Port *
                </label>
                <input
                  type="number"
                  required
                  value={formData.port}
                  onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="22"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Username *
              </label>
              <input
                type="text"
                required
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="username"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Password {!credential && '*'}
              </label>
              <input
                type="password"
                required={!credential}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder={credential ? '••••••••' : 'password'}
              />
              {credential && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Leave blank to keep existing password
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Remote Path
              </label>
              <input
                type="text"
                value={formData.remote_path}
                onChange={(e) => setFormData({ ...formData, remote_path: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="/uploads"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Default upload directory on the remote server
              </p>
            </div>
          </div>

          <div className="p-6 border-t border-gray-200 dark:border-gray-800 flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
            >
              {credential ? 'Update' : 'Add'} Connection
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SFTPCredentialManager;
