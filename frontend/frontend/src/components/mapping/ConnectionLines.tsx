/**
 * ConnectionLines Component
 * Draws animated SVG lines connecting mapped source and target fields
 */

import React, { useEffect, useState, useRef } from 'react';
import type { Mapping } from '../../types';

interface ConnectionLinesProps {
  mappings: Mapping[];
  sourceFields: string[];
  targetFields: string[];
}

interface LineCoordinates {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color: string;
  confidence: number;
  animated: boolean;
}

export const ConnectionLines: React.FC<ConnectionLinesProps> = ({
  mappings,
  sourceFields,
  targetFields,
}) => {
  const [lines, setLines] = useState<LineCoordinates[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.95) return '#10B981'; // green
    if (confidence >= 0.80) return '#F59E0B'; // amber
    return '#6B7280'; // gray
  };

  const calculateLines = () => {
    if (!containerRef.current) return [];

    const container = containerRef.current.getBoundingClientRect();
    const newLines: LineCoordinates[] = [];

    mappings.forEach((mapping) => {
      // Find source field element
      const sourceElement = document.querySelector(
        `[data-source-field="${mapping.source}"]`
      );
      // Find target field element
      const targetElement = document.querySelector(
        `[data-target-field="${mapping.target}"]`
      );

      if (sourceElement && targetElement) {
        const sourceRect = sourceElement.getBoundingClientRect();
        const targetRect = targetElement.getBoundingClientRect();

        // Calculate line endpoints (center of each field box)
        const x1 = sourceRect.right - container.left;
        const y1 = sourceRect.top + sourceRect.height / 2 - container.top;
        const x2 = targetRect.left - container.left;
        const y2 = targetRect.top + targetRect.height / 2 - container.top;

        newLines.push({
          x1,
          y1,
          x2,
          y2,
          color: getConfidenceColor(mapping.confidence),
          confidence: mapping.confidence,
          animated: true,
        });
      }
    });

    return newLines;
  };

  useEffect(() => {
    // Trigger animation when mappings change
    setIsAnimating(true);

    // Small delay to allow DOM to update
    const timer = setTimeout(() => {
      const newLines = calculateLines();
      setLines(newLines);

      // Stop animation after 1 second
      setTimeout(() => setIsAnimating(false), 1000);
    }, 50);

    // Recalculate on window resize
    const handleResize = () => {
      const newLines = calculateLines();
      setLines(newLines);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', handleResize);
    };
  }, [mappings]);

  if (lines.length === 0) return null;

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 pointer-events-none"
      style={{ zIndex: 1 }}
    >
      <svg
        className="w-full h-full"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
        }}
      >
        <defs>
          {/* Arrow marker for line endings */}
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 10 3, 0 6" fill="currentColor" />
          </marker>

          {/* Animated gradient for pulsing effect */}
          <linearGradient id="pulse-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="transparent">
              <animate
                attributeName="stop-opacity"
                values="0;1;0"
                dur="2s"
                repeatCount="indefinite"
              />
            </stop>
            <stop offset="50%" stopColor="white" stopOpacity="0.5" />
            <stop offset="100%" stopColor="transparent">
              <animate
                attributeName="stop-opacity"
                values="0;1;0"
                dur="2s"
                repeatCount="indefinite"
                begin="1s"
              />
            </stop>
          </linearGradient>
        </defs>

        {lines.map((line, index) => {
          // Calculate curved path (Bezier curve)
          const midX = (line.x1 + line.x2) / 2;
          const curveOffset = Math.abs(line.x2 - line.x1) * 0.3; // Curve depth based on distance

          const path = `M ${line.x1} ${line.y1} Q ${midX} ${line.y1 - curveOffset}, ${line.x2} ${line.y2}`;

          return (
            <g key={`${index}-${line.x1}-${line.y1}`}>
              {/* Shadow line for depth */}
              <path
                d={path}
                fill="none"
                stroke="rgba(0, 0, 0, 0.1)"
                strokeWidth="3"
                strokeLinecap="round"
                transform="translate(2, 2)"
              />

              {/* Main line */}
              <path
                d={path}
                fill="none"
                stroke={line.color}
                strokeWidth="2.5"
                strokeLinecap="round"
                markerEnd="url(#arrowhead)"
                style={{
                  color: line.color,
                }}
                className={isAnimating ? 'animate-draw-line' : ''}
              />

              {/* Animated pulse overlay when animating */}
              {isAnimating && (
                <path
                  d={path}
                  fill="none"
                  stroke="url(#pulse-gradient)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  opacity="0.6"
                />
              )}

              {/* Confidence badge at midpoint */}
              <g transform={`translate(${midX}, ${(line.y1 + line.y2) / 2 - curveOffset / 2})`}>
                <circle
                  r="12"
                  fill="white"
                  stroke={line.color}
                  strokeWidth="2"
                />
                <text
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill={line.color}
                  fontSize="10"
                  fontWeight="600"
                >
                  {Math.round(line.confidence * 100)}
                </text>
              </g>
            </g>
          );
        })}
      </svg>

      <style>{`
        @keyframes draw-line {
          from {
            stroke-dasharray: 1000;
            stroke-dashoffset: 1000;
          }
          to {
            stroke-dasharray: 1000;
            stroke-dashoffset: 0;
          }
        }

        .animate-draw-line {
          animation: draw-line 0.8s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default ConnectionLines;
