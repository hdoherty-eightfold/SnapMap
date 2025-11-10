/**
 * Button Component - Eightfold Design System
 * Signature pill-shaped buttons with Eightfold brand colors
 */

import React, { ButtonHTMLAttributes } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'gradient';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

const variantStyles: Record<ButtonVariant, string> = {
  // Eightfold Primary - Teal pill button (signature style)
  primary: `
    bg-eightfold-teal-300
    text-eightfold-navy-600
    hover:bg-eightfold-teal-400
    active:bg-eightfold-teal-500
    disabled:bg-gray-300 disabled:text-gray-500
    shadow-eightfold-teal
    hover:shadow-eightfold-teal-hover
    hover:-translate-y-0.5
    dark:bg-eightfold-teal-300 dark:text-eightfold-navy-600
  `,
  // Eightfold Secondary - Electric blue outline
  secondary: `
    bg-transparent
    border-2 border-eightfold-electric-500
    text-eightfold-electric-500
    hover:bg-eightfold-electric-50
    active:bg-eightfold-electric-100
    disabled:border-gray-300 disabled:text-gray-300
    hover:-translate-y-0.5
    dark:hover:bg-eightfold-electric-900/20
  `,
  // Outline variant
  outline: `
    border-2 border-eightfold-teal-300
    text-eightfold-teal-600
    hover:bg-eightfold-teal-50
    active:bg-eightfold-teal-100
    disabled:border-gray-300 disabled:text-gray-300
    hover:-translate-y-0.5
    dark:border-eightfold-teal-400 dark:text-eightfold-teal-300
  `,
  // Ghost variant
  ghost: `
    text-eightfold-navy-600
    hover:bg-gray-100
    active:bg-gray-200
    disabled:text-gray-300
    dark:text-gray-300 dark:hover:bg-gray-800
  `,
  // Danger variant - Eightfold orange
  danger: `
    bg-eightfold-orange-500
    text-white
    hover:bg-red-600
    active:bg-red-700
    disabled:bg-gray-300
    shadow-md
    hover:shadow-lg
    hover:-translate-y-0.5
  `,
  // Gradient variant - Special CTA (Eightfold signature animated gradient)
  gradient: `
    bg-gradient-eightfold-cta
    text-white
    shadow-eightfold-purple
    hover:shadow-eightfold-purple-hover
    hover:-translate-y-1
    font-bold
    disabled:opacity-50 disabled:cursor-not-allowed
  `,
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-6 py-2 text-sm',
  md: 'px-8 py-3 text-base',
  lg: 'px-10 py-4 text-lg',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  disabled,
  className,
  children,
  ...props
}) => {
  return (
    <button
      className={cn(
        // Eightfold signature pill shape (112px border-radius)
        'inline-flex items-center justify-center gap-2 rounded-pill font-semibold transition-all duration-200',
        'focus:outline-none focus:ring-3 focus:ring-eightfold-teal-300 focus:ring-offset-2',
        'disabled:cursor-not-allowed disabled:opacity-60',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        leftIcon && <span>{leftIcon}</span>
      )}
      {children}
      {!isLoading && rightIcon && <span>{rightIcon}</span>}
    </button>
  );
};

export default Button;
