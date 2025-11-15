/**
 * Eightfold Sidebar Navigation Component
 * Navy gradient background with teal accents
 * Eightfold brand styling throughout
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
    name: 'Welcome',
    icon: '👋',
    description: 'Introduction to Proficiency Studio'
  },
  {
    id: 1,
    name: 'Integration',
    icon: '🔌',
    description: 'Choose data source (CSV/API/SFTP)'
  },
  {
    id: 2,
    name: 'Extract Skills',
    icon: '📥',
    description: 'Pull skills from your source'
  },
  {
    id: 3,
    name: 'Configure',
    icon: '⚙️',
    description: 'Set proficiency levels, LLM & prompts'
  },
  {
    id: 4,
    name: 'Review',
    icon: '👁️',
    description: 'Review configuration issues'
  },
  {
    id: 5,
    name: 'Map Fields',
    icon: '🗺️',
    description: 'Map data fields'
  },
  {
    id: 6,
    name: 'Preview CSV',
    icon: '📄',
    description: 'Preview CSV output'
  },
  {
    id: 7,
    name: 'Preview XML',
    icon: '📋',
    description: 'Preview XML output'
  },
  {
    id: 8,
    name: 'SFTP Upload',
    icon: '📤',
    description: 'Upload via SFTP'
  },
  {
    id: 9,
    name: 'Settings',
    icon: '⚙️',
    description: 'Manage all configurations'
  },
];

export const Sidebar: React.FC = () => {
  const { currentStep, setCurrentStep, uploadedFile, mappings, skillsState, resetAll, isSidebarCollapsed, setIsSidebarCollapsed } = useApp();
  const { theme, toggleTheme } = useTheme();
  

  const handleNavClick = (stepId: number) => {
    // Allow navigation to any accessible step (SFTP and Settings are always accessible)
    if (isStepAccessible(stepId)) {
      setCurrentStep(stepId);
    }
  };

  const isStepAccessible = (stepId: number): boolean => {
    // Check if integration source is selected
    const integrationSource = localStorage.getItem('profstudio_integration_type');

    if (stepId === 0) return true; // Welcome - always accessible
    if (stepId === 1) return true; // Integration - always accessible
    if (stepId === 2) return !!integrationSource; // Extract Skills - requires integration source
    if (stepId === 3) return skillsState.extractionStatus === 'success'; // Configure - requires extracted skills
    if (stepId === 4) return !!uploadedFile; // Review - requires upload (keeping original logic)
    if (stepId === 5) return !!uploadedFile; // Map Fields - requires upload
    if (stepId === 6) return !!uploadedFile && mappings.length > 0; // Preview CSV
    if (stepId === 7) return !!uploadedFile && mappings.length > 0; // Preview XML
    if (stepId === 8) return true; // SFTP Upload - always accessible
    if (stepId === 9) return true; // Settings - always accessible
    return false;
  };

  return (
    <aside className={`fixed left-0 top-0 bottom-0 bg-gradient-navy border-r border-eightfold-teal-300/20 flex flex-col transition-all duration-300 ${isSidebarCollapsed ? 'w-20' : 'w-64'}`}>
      <button
        onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        className="absolute -right-3 top-6 z-10 w-6 h-6 bg-eightfold-teal-300 border border-eightfold-teal-400 rounded-full flex items-center justify-center hover:bg-eightfold-teal-400 transition-all hover:scale-110 shadow-eightfold-teal text-eightfold-navy-600"
        title={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        <span className="text-xs font-bold">{isSidebarCollapsed ? '→' : '←'}</span>
      </button>

      <div className="p-6 border-b border-eightfold-teal-300/20">
        {!isSidebarCollapsed ? (
          <>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 via-pink-500 to-rose-500 flex items-center justify-center shadow-lg">
                <span className="text-xl font-bold text-white">PS</span>
              </div>
              <h1 className="text-2xl font-black bg-gradient-to-r from-purple-300 via-pink-300 to-rose-400 bg-clip-text text-transparent tracking-tight">
                Proficiency Studio
              </h1>
            </div>
            <p className="text-xs text-purple-200/90 mt-2 font-semibold tracking-wide" style={{ marginLeft: '52px' }}>
              AI-Powered Skills Assessment
            </p>
          </>
        ) : (
          <div className="flex justify-center">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 via-pink-500 to-rose-500 flex items-center justify-center shadow-lg">
              <span className="text-xl font-bold text-white">P</span>
            </div>
          </div>
        )}
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {!isSidebarCollapsed && (
          <div className="text-caption text-eightfold-teal-300 uppercase tracking-wider px-3 mb-3 font-bold">
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
                  ? 'bg-eightfold-teal-300/20 text-eightfold-teal-300 font-semibold border-l-3 border-eightfold-teal-300'
                  : isAccessible
                  ? 'hover:bg-white/5 text-white/90 hover:text-eightfold-teal-200'
                  : 'text-white/30 cursor-not-allowed'
                }
              `}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-eightfold-teal-300 rounded-r" />
              )}

              <span className={`text-xl flex-shrink-0 ${isSidebarCollapsed ? '' : 'mt-0.5'}`}>
                {isCompleted ? '✓' : item.icon}
              </span>

              {!isSidebarCollapsed && (
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold">{item.name}</span>
                    {isCompleted && (
                      <span className="text-xs bg-eightfold-teal-300/20 text-eightfold-teal-300 px-2 py-0.5 rounded-pill font-bold">
                        Done
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-white/60 mt-0.5 line-clamp-1">
                    {item.description}
                  </p>
                </div>
              )}
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-eightfold-teal-300/20 space-y-3">
        {/* Connection Status Indicator */}
        {(() => {
          const integrationType = localStorage.getItem('profstudio_integration_type');
          const envId = localStorage.getItem('profstudio_env_id');
          const envName = localStorage.getItem('profstudio_env_name');

          if (integrationType) {
            return (
              <div className={`${isSidebarCollapsed ? 'px-2' : 'px-3'} py-2 bg-eightfold-teal-300/10 border border-eightfold-teal-300/20 rounded-lg`}>
                {!isSidebarCollapsed ? (
                  <div className="text-xs">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-eightfold-teal-200 font-semibold uppercase tracking-wide">Connected</span>
                    </div>
                    <div className="text-white/80">
                      {integrationType === 'csv' ? (
                        <span className="flex items-center gap-1">
                          <span>📄</span>
                          <span>CSV Upload</span>
                        </span>
                      ) : integrationType === 'api' ? (
                        <div>
                          <div className="flex items-center gap-1 mb-1">
                            <span>🔌</span>
                            <span>API Connection</span>
                          </div>
                          <div className="text-xs text-purple-200 bg-purple-500/20 px-2 py-1 rounded">
                            {envName || envId || 'Environment'}
                          </div>
                        </div>
                      ) : integrationType === 'sftp' ? (
                        <span className="flex items-center gap-1">
                          <span>📡</span>
                          <span>SFTP Connection</span>
                        </span>
                      ) : (
                        <span>{integrationType}</span>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center text-xs">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mb-1"></div>
                    <span className="text-lg">
                      {integrationType === 'csv' ? '📄' :
                       integrationType === 'api' ? '🔌' :
                       integrationType === 'sftp' ? '📡' : '🔗'}
                    </span>
                  </div>
                )}
              </div>
            );
          }
          return null;
        })()}

        <button
          onClick={resetAll}
          className={`w-full px-4 py-2.5 text-sm font-semibold text-white bg-white/10 hover:bg-white/20 rounded-pill transition-all ${isSidebarCollapsed ? 'flex justify-center' : ''}`}
          title={isSidebarCollapsed ? 'Start Over' : ''}
        >
          {isSidebarCollapsed ? '🔄' : '🔄 Start Over'}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
