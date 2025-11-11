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
    description: 'Introduction to SnapMap'
  },
  {
    id: 1,
    name: 'Upload',
    icon: '📁',
    description: 'Upload your HR data files'
  },
  {
    id: 2,
    name: 'File Review',
    icon: '🔍',
    description: 'Review data quality and issues'
  },
  {
    id: 3,
    name: 'Map Fields',
    icon: '🔗',
    description: 'Auto-map and adjust field mappings'
  },
  {
    id: 4,
    name: 'Preview CSV',
    icon: '👁️',
    description: 'Preview CSV transformations'
  },
  {
    id: 5,
    name: 'Preview XML',
    icon: '📄',
    description: 'Preview XML format'
  },
  {
    id: 6,
    name: 'SFTP Upload',
    icon: '📤',
    description: 'Upload files to SFTP server'
  },
  {
    id: 7,
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
    if (stepId === 0) return true; // Welcome - always accessible
    if (stepId === 1) return true; // Upload - always accessible
    if (stepId === 2) return !!uploadedFile; // File Review - requires upload
    if (stepId === 3) return !!uploadedFile; // Map Fields - requires upload
    if (stepId === 4) return !!uploadedFile && mappings.length > 0; // Preview CSV
    if (stepId === 5) return !!uploadedFile && mappings.length > 0; // Preview XML
    if (stepId === 6) return true; // SFTP Upload - always accessible
    if (stepId === 7) return true; // Settings - always accessible
    return false;
  };

  return (
    <aside className={`fixed left-0 top-0 bottom-0 bg-gradient-navy border-r border-eightfold-teal-300/20 flex flex-col transition-all duration-300 ${isSidebarCollapsed ? 'w-20' : 'w-64'}`}>
      {/* Collapse Toggle Button - Eightfold Styled */}
      <button
        onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        className="absolute -right-3 top-6 z-10 w-6 h-6 bg-eightfold-teal-300 border border-eightfold-teal-400 rounded-full flex items-center justify-center hover:bg-eightfold-teal-400 transition-all hover:scale-110 shadow-eightfold-teal text-eightfold-navy-600"
        title={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        <span className="text-xs font-bold">{isSidebarCollapsed ? '→' : '←'}</span>
      </button>

      {/* Logo/Brand - SnapMap */}
      <div className="p-6 border-b border-eightfold-teal-300/20">
        {!isSidebarCollapsed ? (
          <>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-400 via-teal-400 to-emerald-500 flex items-center justify-center shadow-lg">
                <span className="text-xl font-bold text-white">S</span>
              </div>
              <h1 className="text-3xl font-black bg-gradient-to-r from-cyan-300 via-teal-300 to-emerald-400 bg-clip-text text-transparent tracking-tight">
                SnapMap
              </h1>
            </div>
            <p className="text-xs text-cyan-200/90 mt-2 font-semibold tracking-wide" style={{ marginLeft: '52px' }}>
              AI-Powered HR Data Transformation
            </p>
          </>
        ) : (
          <div className="flex justify-center">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-400 via-teal-400 to-emerald-500 flex items-center justify-center shadow-lg">
              <span className="text-xl font-bold text-white">S</span>
            </div>
          </div>
        )}
      </div>

      {/* Navigation - Eightfold Styled */}
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
              {/* Active Indicator */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-eightfold-teal-300 rounded-r" />
              )}

              {/* Icon */}
              <span className={`text-xl flex-shrink-0 ${isSidebarCollapsed ? '' : 'mt-0.5'}`}>
                {isCompleted ? '✓' : item.icon}
              </span>

              {/* Content - Only show when expanded */}
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

      {/* Actions - Eightfold Styled */}
      <div className="p-4 border-t border-eightfold-teal-300/20 space-y-2">
        {/* Theme Toggle - Eightfold Pill Button */}
        <button
          onClick={toggleTheme}
          className={`w-full px-4 py-2.5 text-sm font-semibold text-eightfold-navy-600 bg-eightfold-teal-300 hover:bg-eightfold-teal-400 rounded-pill transition-all hover:-translate-y-0.5 shadow-eightfold-teal flex items-center ${isSidebarCollapsed ? 'justify-center' : 'justify-center gap-2'}`}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? '🌙' : '☀️'}
          {!isSidebarCollapsed && <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>}
        </button>

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
