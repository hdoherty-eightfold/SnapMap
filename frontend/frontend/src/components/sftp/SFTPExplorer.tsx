/**
 * SFTP Explorer Component
 * Browse and manage files on SFTP server
 *
 * NOTE: This is a placeholder UI component. Backend API endpoints need to be implemented.
 * Required endpoints:
 * - GET /api/sftp/list/{credential_id}?path=<remote_path> - List directory contents
 * - GET /api/sftp/download/{credential_id}?path=<file_path> - Download file
 * - DELETE /api/sftp/delete/{credential_id}?path=<file_path> - Delete file (optional)
 */

import React, { useState, useEffect } from 'react';
import {
  Folder,
  File,
  Download,
  Trash2,
  RefreshCw,
  ChevronRight,
  Home,
  AlertCircle,
  Loader2,
  Calendar,
  HardDrive
} from 'lucide-react';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { useToast } from '../../contexts/ToastContext';
import {
  getSFTPCredentials,
  type SFTPCredential
} from '../../services/sftp-api';

// Mock data structure for file/folder
interface FileItem {
  name: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: string;
  path: string;
}

export const SFTPExplorer: React.FC = () => {
  const toast = useToast();

  const [credentials, setCredentials] = useState<SFTPCredential[]>([]);
  const [selectedCredentialId, setSelectedCredentialId] = useState<string>('');
  const [currentPath, setCurrentPath] = useState<string>('/');
  const [items, setItems] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Mock data for demonstration
  const mockItems: FileItem[] = [
    {
      name: 'uploads',
      type: 'directory',
      path: '/uploads',
      modified: '2025-11-01T10:00:00Z'
    },
    {
      name: 'exports',
      type: 'directory',
      path: '/exports',
      modified: '2025-11-02T14:30:00Z'
    },
    {
      name: 'employee_data.csv',
      type: 'file',
      size: 245678,
      path: '/employee_data.csv',
      modified: '2025-11-04T08:15:00Z'
    },
    {
      name: 'transformed_output.xml',
      type: 'file',
      size: 512340,
      path: '/transformed_output.xml',
      modified: '2025-11-05T12:45:00Z'
    }
  ];

  useEffect(() => {
    loadCredentials();
  }, []);

  useEffect(() => {
    if (selectedCredentialId) {
      loadDirectoryContents(currentPath);
    }
  }, [selectedCredentialId, currentPath]);

  const loadCredentials = async () => {
    try {
      setLoading(true);
      const creds = await getSFTPCredentials();
      setCredentials(creds);

      if (creds.length > 0) {
        setSelectedCredentialId(creds[0].id);
      }
    } catch (error: any) {
      toast.error('Failed to load credentials', error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadDirectoryContents = async (path: string) => {
    try {
      setRefreshing(true);

      // TODO: Replace with actual API call when backend endpoint is ready
      // const response = await fetch(`/api/sftp/list/${selectedCredentialId}?path=${encodeURIComponent(path)}`);
      // const data = await response.json();
      // setItems(data.items);

      // Using mock data for now
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
      setItems(mockItems);

      toast.info('Mock Data', 'Showing placeholder data. Backend API needs implementation.');
    } catch (error: any) {
      toast.error('Failed to load directory', error.message);
      setItems([]);
    } finally {
      setRefreshing(false);
    }
  };

  const handleItemClick = (item: FileItem) => {
    if (item.type === 'directory') {
      setCurrentPath(item.path);
    }
  };

  const handleDownload = async (item: FileItem) => {
    try {
      // TODO: Implement actual download when backend is ready
      // const response = await fetch(`/api/sftp/download/${selectedCredentialId}?path=${encodeURIComponent(item.path)}`);
      // const blob = await response.blob();
      // ... download logic

      toast.info('Download', `Would download: ${item.name} (Backend API needed)`);
    } catch (error: any) {
      toast.error('Download failed', error.message);
    }
  };

  const handleDelete = async (item: FileItem) => {
    if (!confirm(`Delete ${item.name}?`)) return;

    try {
      // TODO: Implement actual delete when backend is ready
      // await fetch(`/api/sftp/delete/${selectedCredentialId}?path=${encodeURIComponent(item.path)}`, { method: 'DELETE' });

      toast.info('Delete', `Would delete: ${item.name} (Backend API needed)`);
      loadDirectoryContents(currentPath);
    } catch (error: any) {
      toast.error('Delete failed', error.message);
    }
  };

  const navigateUp = () => {
    const parts = currentPath.split('/').filter(p => p);
    parts.pop();
    const newPath = '/' + parts.join('/');
    setCurrentPath(newPath || '/');
  };

  const formatSize = (bytes?: number): string => {
    if (!bytes) return '-';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getBreadcrumbs = (): string[] => {
    if (currentPath === '/') return ['Home'];
    return ['Home', ...currentPath.split('/').filter(p => p)];
  };

  if (loading) {
    return (
      <div className="p-8">
        <Card>
          <CardContent>
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">SFTP Explorer</h2>
        <p className="text-gray-600 dark:text-gray-300 mt-1">
          Browse and manage files on your SFTP server
        </p>
      </div>

      {/* Backend API Notice */}
      <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
              Backend API Implementation Needed
            </p>
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
              This component requires the following API endpoints to be implemented:
            </p>
            <ul className="text-sm text-yellow-700 dark:text-yellow-300 mt-2 list-disc list-inside space-y-1">
              <li>GET /api/sftp/list/&#123;credential_id&#125;?path=&lt;remote_path&gt; - List directory contents</li>
              <li>GET /api/sftp/download/&#123;credential_id&#125;?path=&lt;file_path&gt; - Download file</li>
              <li>DELETE /api/sftp/delete/&#123;credential_id&#125;?path=&lt;file_path&gt; - Delete file (optional)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Connection Selection */}
      <Card>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                SFTP Connection
              </label>
              {credentials.length === 0 ? (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  No SFTP connections configured. Please add one in Settings.
                </p>
              ) : (
                <select
                  value={selectedCredentialId}
                  onChange={(e) => setSelectedCredentialId(e.target.value)}
                  className="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {credentials.map((cred) => (
                    <option key={cred.id} value={cred.id}>
                      {cred.name} ({cred.username}@{cred.host})
                    </option>
                  ))}
                </select>
              )}
            </div>
            <div className="pt-6">
              <Button
                variant="outline"
                onClick={() => loadDirectoryContents(currentPath)}
                disabled={refreshing || !selectedCredentialId}
                leftIcon={<RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />}
              >
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* File Browser */}
      {selectedCredentialId && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Files & Folders</CardTitle>
              {currentPath !== '/' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={navigateUp}
                  leftIcon={<ChevronRight className="w-4 h-4 rotate-180" />}
                >
                  Up
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {/* Breadcrumbs */}
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
              <Home className="w-4 h-4" />
              {getBreadcrumbs().map((crumb, index) => (
                <React.Fragment key={index}>
                  {index > 0 && <ChevronRight className="w-4 h-4" />}
                  <span className={index === getBreadcrumbs().length - 1 ? 'text-gray-900 dark:text-white font-medium' : ''}>
                    {crumb}
                  </span>
                </React.Fragment>
              ))}
            </div>

            {/* File List */}
            {refreshing ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
              </div>
            ) : items.length === 0 ? (
              <div className="text-center py-12">
                <Folder className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">Empty directory</p>
              </div>
            ) : (
              <div className="space-y-1">
                {items.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group"
                  >
                    {/* Icon & Name */}
                    <div
                      className="flex items-center gap-3 flex-1 min-w-0 cursor-pointer"
                      onClick={() => handleItemClick(item)}
                    >
                      {item.type === 'directory' ? (
                        <Folder className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                      ) : (
                        <File className="w-5 h-5 text-gray-600 dark:text-gray-400 flex-shrink-0" />
                      )}
                      <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {item.name}
                      </span>
                    </div>

                    {/* Metadata */}
                    <div className="hidden md:flex items-center gap-6 text-xs text-gray-500 dark:text-gray-400">
                      {item.type === 'file' && (
                        <div className="flex items-center gap-1">
                          <HardDrive className="w-3 h-3" />
                          <span>{formatSize(item.size)}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        <span>{formatDate(item.modified)}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    {item.type === 'file' && (
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownload(item)}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(item)}
                          className="text-error-600 hover:text-error-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SFTPExplorer;
