/**
 * Welcome Component
 * Introduction page explaining SnapMap and how it works
 */

import React from 'react';
import { ArrowRight, Upload, FileSearch, Map, Eye, Cloud, Sparkles, CheckCircle } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';

export const Welcome: React.FC = () => {
  const { nextStep } = useApp();

  const features = [
    {
      icon: <Upload className="w-6 h-6" />,
      title: 'Upload Your Data',
      description: 'Support for CSV and XML files up to 100MB. Automatically detects entity type from your data.',
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: 'AI Mapping',
      description: 'Semantic field matching with 80-90% accuracy. Our AI understands the meaning behind your field names.',
    },
    {
      icon: <FileSearch className="w-6 h-6" />,
      title: 'Quality Review',
      description: 'Built-in validation detects data issues, missing fields, and suggests improvements.',
    },
    {
      icon: <Eye className="w-6 h-6" />,
      title: 'Preview & Edit',
      description: 'Review transformations before export. Make manual adjustments with our intuitive interface.',
    },
    {
      icon: <Cloud className="w-6 h-6" />,
      title: 'Export & Upload',
      description: 'Download XML files or upload directly to your SFTP server. Track progress in real-time.',
    },
  ];

  const steps = [
    {
      number: 1,
      title: 'Upload',
      description: 'Choose your data file',
    },
    {
      number: 2,
      title: 'Review',
      description: 'Check data quality',
    },
    {
      number: 3,
      title: 'Map',
      description: 'AI field matching',
    },
    {
      number: 4,
      title: 'Preview',
      description: 'Review transformed data',
    },
    {
      number: 5,
      title: 'Export',
      description: 'Download or upload to SFTP',
    },
  ];

  return (
    <div className="p-8">
      <div className="bg-white dark:bg-gray-900 -mx-8 px-8 pt-8 pb-6 mb-6 border-b border-gray-200 dark:border-gray-700 text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 mb-4">
          <Map className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Welcome to SnapMap
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-4">
          AI powered HR transformation
        </p>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-2xl">What is SnapMap?</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            SnapMap is an intelligent data transformation tool that converts your customer HR data into Eightfold's
            standardized format. Using advanced AI and semantic understanding, it automatically maps your source fields
            to Eightfold target fields, validates data quality, and generates transformation-ready XML files.
            The entire process takes just minutes instead of hours of manual work.
          </p>
        </CardContent>
      </Card>

      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {steps.map((step, index) => (
            <div key={step.number} className="relative">
              <Card className="h-full">
                <CardContent className="p-6 text-center">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-bold text-lg mb-3">
                    {step.number}
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    {step.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {step.description}
                  </p>
                </CardContent>
              </Card>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-2 transform -translate-y-1/2 z-10">
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
          Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="h-full">
              <CardContent className="p-6">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 mb-4">
                  {feature.icon}
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-2xl">Why Choose SnapMap?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Save Time</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Reduce manual data mapping from hours to minutes with AI automation
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Increase Accuracy</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Semantic understanding ensures better field matching than keyword-based tools
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Ensure Quality</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Built-in validation detects data issues before transformation
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Streamline Workflow</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  End-to-end process from upload to SFTP delivery in one tool
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center">
        <Button
          variant="primary"
          size="lg"
          onClick={nextStep}
          rightIcon={<ArrowRight className="w-5 h-5" />}
          className="px-8 py-4 text-lg"
        >
          Get Started
        </Button>
      </div>
    </div>
  );
};

export default Welcome;