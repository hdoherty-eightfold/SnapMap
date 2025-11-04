/**
 * Utility for merging Tailwind CSS classes
 * Combines clsx and tailwind-merge for optimal class management
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
