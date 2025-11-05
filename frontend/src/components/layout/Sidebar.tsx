/**
 * Modern Sidebar Navigation Component
 * Inspired by Linear, Vercel, and Notion
 * With Dark Mode Support and Collapsible Functionality
 */

import React, { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useTheme } from '../../contexts/ThemeContext';

interface NavItem {
  id: number;
  name: string;
  icon: string;
  description: string;
}

const navItems: NavItem[] = [
  {
    id: 0,
    name: 'Upload',
    icon: '📁',
    description: 'Upload your HR data files'
  },
  {
    id: 1,
    name: 'Map Fields',
    icon: '🔗',
    description: 'Auto-map and adjust field mappings'
  },
  {
    id: 2,
    name: 'Review & Validate',
    icon: '🔍',
    description: 'Schema validation'
  },
  {
    id: 3,
    name: 'Preview CSV',
    icon: '👁️',
    description: 'Preview CSV transformations'
  },
  {
    id: 4,
    name: 'Preview XML',
    icon: '📄',
    description: 'Preview XML format'
  },
  {
    id: 5,
    name: 'SFTP Upload',
    icon: '📤',
    description: 'Upload files to SFTP server'
  },
  {
    id: 6,
    name: 'Settings',
    icon: '⚙️',
    description: 'Configure API keys'
  },
];

export const Sidebar: React.FC = () => {
  const { currentStep, setCurrentStep, uploadedFile, mappings, resetAll, isSidebarCollapsed, setIsSidebarCollapsed } = useApp();
  const { theme, toggleTheme } = useTheme();
  

  const handleNavClick = (stepId: number) => {
    // Allow navigation to any accessible step (SFTP and Settings are always accessible)
    if (isStepAccessible(stepId)) {
      setCurrentStep(stepId);
    }
  };

  const isStepAccessible = (stepId: number): boolean => {
    if (stepId === 0) return true; // Upload
    if (stepId === 1) return !!uploadedFile; // Map Fields - requires upload
    if (stepId === 2) return !!uploadedFile; // Review & Validate - requires upload
    if (stepId === 3) return !!uploadedFile && mappings.length > 0; // Preview CSV
    if (stepId === 4) return !!uploadedFile && mappings.length > 0; // Preview XML
    if (stepId === 5) return true; // SFTP Upload - always accessible
    if (stepId === 6) return true; // Settings - always accessible
    return false;
  };

  return (
    <aside className={`fixed left-0 top-0 bottom-0 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-all duration-300 ${isSidebarCollapsed ? 'w-20' : 'w-64'}`}>
      {/* Collapse Toggle Button */}
      <button
        onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        className="absolute -right-3 top-6 z-10 w-6 h-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm"
        title={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        <span className="text-xs">{isSidebarCollapsed ? '→' : '←'}</span>
      </button>

      {/* Logo/Brand */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        {!isSidebarCollapsed ? (
          <>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">SnapMap</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">HR Data Transformer</p>
          </>
        ) : (
          <h1 className="text-2xl text-center">📊</h1>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {!isSidebarCollapsed && (
          <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-3 mb-3">
            Workflow
          </div>
        )}
        {navItems.map((item) => {
          const isActive = currentStep === item.id;
          const isAccessible = isStepAccessible(item.id);
          const isCompleted = currentStep > item.id;

          return (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              disabled={!isAccessible}
              title={isSidebarCollapsed ? item.name : ''}
              className={`
                w-full text-left rounded-lg transition-all duration-200
                flex items-start group relative
                ${isSidebarCollapsed ? 'px-3 py-3 justify-center' : 'px-3 py-2.5 gap-3'}
                ${isActive
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 font-medium shadow-sm'
                  : isAccessible
                  ? 'hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                  : 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
                }
              `}
            >
              {/* Active Indicator */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-8 bg-primary-600 dark:bg-primary-500 rounded-r" />
              )}

              {/* Icon */}
              <span className={`text-xl flex-shrink-0 ${isSidebarCollapsed ? '' : 'mt-0.5'}`}>
                {isCompleted ? '✓' : item.icon}
              </span>

              {/* Content - Only show when expanded */}
              {!isSidebarCollapsed && (
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{item.name}</span>
                    {isCompleted && (
                      <span className="text-xs bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400 px-1.5 py-0.5 rounded">
                        Done
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-1">
                    {item.description}
                  </p>
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Actions */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-2">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className={`w-full px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors flex items-center ${isSidebarCollapsed ? 'justify-center' : 'justify-center gap-2'}`}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? '🌙' : '☀️'}
          {!isSidebarCollapsed && <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>}
        </button>

        <button
          onClick={resetAll}
          className={`w-full px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors ${isSidebarCollapsed ? 'flex justify-center' : ''}`}
          title={isSidebarCollapsed ? 'Start Over' : ''}
        >
          {isSidebarCollapsed ? '🔄' : '🔄 Start Over'}
        </button>

        {/* Quick Stats - Only show when expanded */}
        {!isSidebarCollapsed && (
          <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Progress</div>
            <div className="space-y-1.5 text-xs text-gray-600 dark:text-gray-400">
              <div className="flex justify-between">
                <span>File Uploaded:</span>
                <span className={uploadedFile ? 'text-success-600 dark:text-success-400 font-medium' : 'text-gray-400 dark:text-gray-600'}>
                  {uploadedFile ? '✓ Yes' : '✗ No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Fields Mapped:</span>
                <span className={mappings.length > 0 ? 'text-success-600 dark:text-success-400 font-medium' : 'text-gray-400 dark:text-gray-600'}>
                  {mappings.length > 0 ? `${mappings.length} fields` : '✗ None'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      {!isSidebarCollapsed && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-800">
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
            <p className="font-medium">v1.0.0</p>
            <p className="mt-1">Eightfold AI Hackathon 🚀</p>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
