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

  // Calculate left position to attach to sidebar edge
  const leftArrowPosition = isSidebarCollapsed ? '5rem' : '16rem'; // 80px vs 256px (exact sidebar width)

  return (
    <>
      {/* Previous Arrow - attached to right edge of sidebar */}
      {canGoPrevious && (
        <button
          onClick={previousStep}
          style={{ left: leftArrowPosition }}
          className="fixed top-1/2 transform -translate-y-1/2 z-20 w-4 h-28 bg-primary-600/50 hover:bg-primary-600/70 dark:bg-primary-700/50 dark:hover:bg-primary-700/70 text-white backdrop-blur-sm transition-all duration-300 flex items-center justify-center group rounded-r-lg border-r border-t border-b border-primary-400/20 shadow-sm"
          aria-label="Previous step"
        >
          <ChevronLeft className="w-4 h-4 group-hover:scale-110 group-hover:-translate-x-0.5 transition-all" />
        </button>
      )}

      {/* Next Arrow - attached to right edge of page */}
      {canGoNext && (
        <button
          onClick={nextStep}
          className="fixed right-0 top-1/2 transform -translate-y-1/2 z-20 w-4 h-28 bg-primary-600/50 hover:bg-primary-600/70 dark:bg-primary-700/50 dark:hover:bg-primary-700/70 text-white backdrop-blur-sm transition-all duration-300 flex items-center justify-center group rounded-l-lg border-l border-t border-b border-primary-400/20 shadow-sm"
          aria-label="Next step"
        >
          <ChevronRight className="w-4 h-4 group-hover:scale-110 group-hover:translate-x-0.5 transition-all" />
        </button>
      )}
    </>
  );
};

export default NavigationArrows;
