/**
 * Welcome Component
 * Introduction page explaining SnapMap and how it works
 */

import React from 'react';
import { ArrowRight, Upload, FileSearch, Map, Eye, Cloud, Sparkles, CheckCircle, PlayCircle, Clock, Users } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';

export const Welcome: React.FC = () => {
  const { nextStep } = useApp();

  const features = [
    {
      icon: <Upload className="w-6 h-6" />,
      title: 'Upload Your Data',
      description: 'Support for CSV and Excel files up to 100MB. No templates needed—just upload your source data.',
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: 'Intelligent Fuzzy Matching',
      description: 'AI automatically maps 80-90% of fields in seconds. Handles typos, variations, and complex types.',
    },
    {
      icon: <FileSearch className="w-6 h-6" />,
      title: 'Real-Time Validation',
      description: 'Catch errors before export. XSD validation ensures your data passes on the first try.',
    },
    {
      icon: <Eye className="w-6 h-6" />,
      title: 'Visual Mapping',
      description: 'See connection arrows showing what goes where. Drag-and-drop to fine-tune any mappings.',
    },
    {
      icon: <Cloud className="w-6 h-6" />,
      title: 'One-Click Export',
      description: 'Generate XSD-compliant XML in seconds. Ready to upload to Eightfold immediately.',
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
          Transform Eightfold data in <strong className="text-primary-600 dark:text-primary-400">minutes, not days</strong>
        </p>
        <p className="text-base text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
          Self-service ETL for non-technical HR users • Zero coding required • XSD-compliant on first try
        </p>
      </div>

      {/* Get Started Section */}
      <Card className="mb-8 border-l-4 border-l-primary-500 bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20">
        <CardContent className="p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-500 mb-4">
              <PlayCircle className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
              Ready to Get Started?
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Transform your HR data in just a few clicks. No setup required, no learning curve.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-6 bg-white dark:bg-gray-800/50 rounded-lg shadow-sm">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 mb-4">
                <Clock className="w-6 h-6" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Quick Start</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Complete your first transformation in under 10 minutes
              </p>
            </div>

            <div className="text-center p-6 bg-white dark:bg-gray-800/50 rounded-lg shadow-sm">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 mb-4">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">No Training</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Built for HR professionals, not IT experts
              </p>
            </div>

            <div className="text-center p-6 bg-white dark:bg-gray-800/50 rounded-lg shadow-sm">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 mb-4">
                <CheckCircle className="w-6 h-6" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Guaranteed Success</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                XSD-compliant output that passes validation every time
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800/50 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 text-center">
              What You'll Need
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0 w-2 h-2 rounded-full bg-primary-500"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Your source data file (CSV, Excel, or XML)
                </span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0 w-2 h-2 rounded-full bg-primary-500"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Knowledge of which Eightfold entity you're targeting
                </span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0 w-2 h-2 rounded-full bg-primary-500"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  5-10 minutes of your time
                </span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0 w-2 h-2 rounded-full bg-primary-500"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  That's it! No technical setup required
                </span>
              </div>
            </div>
          </div>

          <div className="text-center">
            <Button
              variant="primary"
              size="lg"
              onClick={nextStep}
              rightIcon={<ArrowRight className="w-5 h-5" />}
              className="px-8 py-4 text-lg shadow-lg hover:shadow-xl transition-shadow"
            >
              Start Transforming Your Data
            </Button>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-3">
              No account required • Free to use • Instant results
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="mb-8 border-l-4 border-l-red-500">
        <CardHeader>
          <CardTitle className="text-2xl">The Problem</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
            HR teams today face three major challenges when ingesting data into Eightfold:
          </p>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center text-red-600 dark:text-red-400 font-bold">
                1
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Complex CSV Templates</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Strict naming conventions like <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">EMPLOYEE-MAIN.csv</code> and <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">ROLE-ASSOCIATEDTAGS.csv</code> are overwhelming for non-technical users.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center text-red-600 dark:text-red-400 font-bold">
                2
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Denormalized Source Data</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Skills, education, and experience in separate columns need to become multiple rows. This requires scripting skills that HR teams don't have.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center text-red-600 dark:text-red-400 font-bold">
                3
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Manual Validation</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  One wrong date format or missing field causes the entire ingestion to fail. Errors are only discovered when it's too late.
                </p>
              </div>
            </div>
          </div>
          <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
            <p className="text-sm text-red-800 dark:text-red-300 font-medium">
              <strong>The Result:</strong> HR teams spend <strong>days—sometimes weeks</strong>—wrestling with data transformations, 
              forcing them to wait on IT and delaying their Eightfold go-live.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="mb-8 border-l-4 border-l-green-500">
        <CardHeader>
          <CardTitle className="text-2xl">The Solution: SnapMap</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
            SnapMap is a <strong>self-service ETL tool</strong> that lets non-technical HR users transform their data 
            in <strong>minutes, not days</strong>, with <strong>zero coding required</strong>.
          </p>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            Using advanced semantic understanding and AI-powered field mapping, SnapMap automatically matches your source fields
            to Eightfold target fields, validates data quality in real-time, and generates XSD-compliant XML files that pass 
            validation on the first try.
          </p>
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">10 min</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">vs. 2-3 days manual work</div>
            </div>
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">Zero</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Coding skills required</div>
            </div>
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">First Try</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">XSD validation passes</div>
            </div>
          </div>
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
          <CardTitle className="text-2xl">The Impact</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Time Savings</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  What used to take HR 2-3 days now takes 10 minutes. Eliminate the wait for IT support.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Zero Errors</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  XSD validation ensures data quality before ingestion. No more failed uploads.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Self-Service</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  HR no longer waits on IT. Non-technical users can complete transformations independently.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Faster Go-Live</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Eliminate weeks of delays. Get your Eightfold implementation live faster.
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