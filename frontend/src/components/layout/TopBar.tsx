/**
 * Eightfold Top Bar Component
 * Modern header with Eightfold brand styling
 * Scroll-based transparency effect
 */

import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';

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
  'Upload CSV files from any HR system or flat file source',
  'Review data quality, missing fields, and column issues before mapping',
  'AI-powered semantic matching automatically maps fields to Eightfold format',
  'Review CSV transformations and validate data quality before export',
  'Preview the XML format of your transformed data',
  'Upload transformed files directly to your SFTP server',
  'Configure your Google Gemini API key and select your preferred vector database'
];

export const TopBar: React.FC = () => {
  const { currentStep } = useApp();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // Check if page is scrolled more than 50px
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className={`sticky top-0 z-10 transition-all duration-300 border-b ${
      scrolled
        ? 'bg-gradient-to-r from-eightfold-navy-600/10 to-eightfold-nile-500/10 border-eightfold-teal-300/5 backdrop-blur-lg'
        : 'bg-gradient-to-r from-eightfold-navy-600 to-eightfold-nile-500 border-eightfold-teal-300/20'
    }`}>
      <div className={`px-6 transition-all duration-300 ${scrolled ? 'py-1' : 'py-2'}`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            {/* Title - Eightfold Typography */}
            <h2 className={`transition-all duration-300 ${
              scrolled
                ? 'text-base mb-0 text-gray-900 dark:text-white'
                : 'text-xl mb-0 text-white'
            }`}>
              {stepTitles[currentStep]}
            </h2>

            {/* Description - Fades out when scrolled */}
            <p className={`text-sm text-gray-200 max-w-2xl transition-all duration-300 ${
              scrolled ? 'opacity-0 max-h-0 overflow-hidden' : 'opacity-100 max-h-16'
            }`}>
              {stepDescriptions[currentStep]}
            </p>
          </div>

          {/* Eightfold Logo with Branding */}
          <div className="flex items-center gap-6">
            {/* Eightfold Logo - Large Brand Image */}
            <img
              src="https://eightfold.ai/wp-content/uploads/logo_color.png"
              alt="Eightfold"
              className={`w-auto object-contain transition-all duration-300 ${scrolled ? 'h-8' : 'h-12'}`}
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
