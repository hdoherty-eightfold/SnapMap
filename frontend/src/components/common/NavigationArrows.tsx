/**
 * Navigation Arrows Component
 * Fixed position arrows for navigating between steps
 */

import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';

export const NavigationArrows: React.FC = () => {
  const { currentStep, previousStep, nextStep, isSidebarCollapsed } = useApp();

  const canGoPrevious = currentStep > 0;
  const canGoNext = currentStep < 7; // 7 total steps (0-7)

  // Calculate left position based on sidebar state
  const leftPosition = isSidebarCollapsed ? '6rem' : '17rem'; // 80px vs 272px (sidebar width + padding)

  return (
    <>
      {/* Previous Arrow */}
      {canGoPrevious && (
        <button
          onClick={previousStep}
          style={{ left: leftPosition }}
          className="fixed top-1/2 transform -translate-y-1/2 z-30 w-12 h-12 rounded-full bg-primary-600 hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-600 text-white shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center group"
          aria-label="Previous step"
        >
          <ChevronLeft className="w-6 h-6 group-hover:scale-110 transition-transform" />
        </button>
      )}

      {/* Next Arrow */}
      {canGoNext && (
        <button
          onClick={nextStep}
          className="fixed right-4 top-1/2 transform -translate-y-1/2 z-30 w-12 h-12 rounded-full bg-primary-600 hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-600 text-white shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center group"
          aria-label="Next step"
        >
          <ChevronRight className="w-6 h-6 group-hover:scale-110 transition-transform" />
        </button>
      )}
    </>
  );
};

export default NavigationArrows;
