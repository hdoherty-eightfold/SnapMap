/**
 * Eightfold Top Bar Component
 * Modern header with Eightfold brand styling
 * Scroll-based transparency effect
 */

import React, { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { useTheme } from '../../contexts/ThemeContext';

const stepTitles = [
  'Welcome to SnapMap',
  'Upload Your Data',
  'Review File Quality',
  'Map Your Fields',
  'Preview CSV Data',
  'Preview XML Format',
  'SFTP Upload',
  'Settings'
];

const stepDescriptions = [
  'Learn about SnapMap and how it transforms your HR data into Eightfold format using AI-powered field mapping',
  'Upload CSV or XML files up to 100MB. The system will automatically detect the entity type from your data',
  'Review your uploaded file for data quality issues, missing fields, and column name problems before mapping',
  'Semantic auto-mapping matches 80-90% of fields correctly. Click any source field, then click a target to map manually',
  'Review the CSV transformations carefully. Check date formats, field mappings, and data quality before export',
  'Preview the XML format of your transformed data. Download the full XML file or proceed to SFTP upload',
  'Upload transformed files directly to your SFTP server. Select credentials and track upload progress in real-time',
  'Configure your Google Gemini API key for semantic mapping features and select your preferred vector database'
];

export const TopBar: React.FC = () => {
  const { currentStep } = useApp();
  const { theme, toggleTheme } = useTheme();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // Check if page is scrolled more than 100px with debouncing
      setScrolled(window.scrollY > 100);
    };

    // Throttle scroll events to improve performance and reduce flicker
    let ticking = false;
    const throttledScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', throttledScroll, { passive: true });
    return () => window.removeEventListener('scroll', throttledScroll);
  }, []);

  return (
    <div className={`sticky top-0 z-50 transition-all duration-700 ease-out border-b ${
      scrolled
        ? 'bg-gradient-to-r from-eightfold-navy-600/10 to-eightfold-nile-500/10 border-eightfold-teal-300/5 backdrop-blur-lg'
        : 'bg-gradient-to-r from-eightfold-navy-600 to-eightfold-nile-500 border-eightfold-teal-300/20'
    }`}>
      <div className={`px-6 transition-all duration-700 ease-out ${scrolled ? 'py-1' : 'py-2'}`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            {/* Title - Eightfold Typography */}
            <h2 className={`transition-all duration-700 ease-out ${
              scrolled
                ? 'text-base mb-0 text-gray-900 dark:text-white'
                : 'text-xl mb-0 text-white'
            }`}>
              {stepTitles[currentStep]}
            </h2>

            {/* Description - Fades out when scrolled */}
            <p className={`text-sm text-gray-200 max-w-2xl transition-all duration-700 ease-out ${
              scrolled ? 'opacity-0 max-h-0 overflow-hidden' : 'opacity-100 max-h-16'
            }`}>
              {stepDescriptions[currentStep]}
            </p>
          </div>

          {/* Controls and Eightfold Logo */}
          <div className="flex items-center gap-4">
            {/* Dark Mode Toggle */}
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-all duration-300 hover:scale-110 ${
                scrolled
                  ? 'bg-white/10 hover:bg-white/20 text-gray-700 dark:text-gray-300'
                  : 'bg-white/20 hover:bg-white/30 text-white'
              }`}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
              title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? (
                <Moon className="w-4 h-4" />
              ) : (
                <Sun className="w-4 h-4" />
              )}
            </button>

            {/* Eightfold Logo - Large Brand Image */}
            <img
              src="https://eightfold.ai/wp-content/uploads/logo_color.png"
              alt="Eightfold"
              className={`w-auto object-contain transition-all duration-700 ease-out ${scrolled ? 'h-8' : 'h-12'}`}
              onError={(e) => {
                // Fallback to base64 encoded SVG if CDN fails
                e.currentTarget.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M20,50 C20,35 30,25 40,35 C50,45 60,45 70,35 C80,25 90,35 90,50 C90,65 80,75 70,65 C60,55 50,55 40,65 C30,75 20,65 20,50 Z' fill='%2388e2d2'/%3E%3C/svg%3E";
              }}
            />
          </div>
        </div>

      </div>
    </div>
  );
};

export default TopBar;
