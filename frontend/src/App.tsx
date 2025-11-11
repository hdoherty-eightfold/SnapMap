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
import PreviewCSV from './components/export/PreviewCSV';
import PreviewXML from './components/export/PreviewXML';
import SFTPUploadPage from './components/sftp/SFTPUploadPage';
import SettingsPanel from './components/settings/SettingsPanel';
import Welcome from './components/welcome/Welcome';
import NavigationArrows from './components/common/NavigationArrows';
import './App.css';

const AppContent: React.FC = () => {
  const { currentStep, isSidebarCollapsed } = useApp();

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 flex transition-colors">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className={`flex-1 transition-all duration-300 ${isSidebarCollapsed ? 'ml-20' : 'ml-64'} bg-gray-100 dark:bg-gray-900`}>
        {/* Top Bar */}
        <TopBar />

        {/* Content */}
        <main className="p-0">
          <div className="w-full">
            {/* Step Content */}
            <div className="min-h-screen">
              {currentStep === 0 && <Welcome />}
              {currentStep === 1 && <FileUpload />}
              {currentStep === 2 && <IssueReview />}
              {currentStep === 3 && <FieldMapping />}
              {currentStep === 4 && <PreviewCSV />}
              {currentStep === 5 && <PreviewXML />}
              {currentStep === 6 && <SFTPUploadPage />}
              {currentStep === 7 && <SettingsPanel />}
            </div>
          </div>
        </main>
      </div>

      {/* Navigation Arrows */}
      <NavigationArrows />
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
