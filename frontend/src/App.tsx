/**
 * Main Application Component
 * SnapMap - HR Data Transformation Tool
 * Modern UI with Sidebar Navigation and Dark Mode
 */

import React from 'react';
import { AppProvider, useApp } from './contexts/AppContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './contexts/ToastContext';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import FileUpload from './components/upload/FileUpload';
import IssueReview from './components/review/IssueReview';
import FieldMapping from './components/mapping/FieldMapping';
import TransformPreview from './components/export/TransformPreview';
import SFTPCredentialManager from './components/sftp/SFTPCredentialManager';
import SettingsPanel from './components/settings/SettingsPanel';
import './App.css';

const AppContent: React.FC = () => {
  const { currentStep, isSidebarCollapsed } = useApp();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex transition-colors">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className={`flex-1 transition-all duration-300 ${isSidebarCollapsed ? 'ml-20' : 'ml-64'}`}>
        {/* Top Bar */}
        <TopBar />

        {/* Content */}
        <main className="p-8">
          <div className="max-w-7xl mx-auto">
            {/* Step Content */}
            <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 overflow-hidden transition-colors">
              {currentStep === 0 && <FileUpload />}
              {currentStep === 1 && <IssueReview />}
              {currentStep === 2 && <FieldMapping />}
              {currentStep === 3 && <TransformPreview />}
              {currentStep === 4 && <TransformPreview />}
              {currentStep === 5 && <SFTPCredentialManager />}
              {currentStep === 6 && <SettingsPanel />}
            </div>

            {/* Helpful Tips */}
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg transition-colors">
              <div className="flex items-start gap-3">
                <span className="text-blue-600 dark:text-blue-400 text-lg">💡</span>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                    {currentStep === 0 && 'Getting Started'}
                    {currentStep === 1 && 'AI-Powered Analysis'}
                    {currentStep === 2 && 'Pro Tip'}
                    {currentStep === 3 && 'Quality Check'}
                    {currentStep === 4 && 'Success!'}
                    {currentStep === 5 && 'SFTP Setup'}
                    {currentStep === 6 && 'Configuration'}
                  </h3>
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    {currentStep === 0 && 'Upload CSV or Excel files up to 100MB. AI will automatically detect the entity type from your data.'}
                    {currentStep === 1 && 'Our AI analyzes your file and detects issues like missing fields, misspelled columns, and data quality problems. Review suggested fixes before proceeding.'}
                    {currentStep === 2 && 'Our AI auto-maps 80-90% of fields correctly. Green badges show high confidence matches. Click any source field, then click a target to map manually.'}
                    {currentStep === 3 && 'Review the transformations carefully. Check date formats, field mappings, and data quality before exporting.'}
                    {currentStep === 4 && 'Your data is ready! Download the standardized CSV file and upload it to Eightfold.'}
                    {currentStep === 5 && 'Configure SFTP credentials to automatically upload transformed files to your server.'}
                    {currentStep === 6 && 'Configure your Google Gemini API key for AI-powered features and select your preferred vector database.'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AppProvider>
          <AppContent />
        </AppProvider>
      </ToastProvider>
    </ThemeProvider>
  );
};

export default App;
