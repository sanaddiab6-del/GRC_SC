/**
 * Utility functions for SICO GRC Platform Frontend
 * Includes class name merging and conditional styling helpers
 */

import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Merge Tailwind CSS classes with proper precedence
 * Combines clsx for conditional classes and tailwind-merge for deduplication
 * 
 * @param inputs - Class names to merge
 * @returns Merged class string
 * 
 * @example
 * cn("px-2 py-1", condition && "bg-blue-500", "hover:bg-blue-600")
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format date to localized string
 * Supports both English and Arabic locales
 * 
 * @param date - Date to format
 * @param locale - Locale code (en or ar)
 * @returns Formatted date string
 */
export function formatDate(date: Date | string, locale: string = 'en'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj.toLocaleDateString(locale === 'ar' ? 'ar-SA' : 'en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/**
 * Format compliance percentage with proper styling
 * 
 * @param percentage - Compliance percentage (0-100)
 * @returns Formatted string with % symbol
 */
export function formatPercentage(percentage: number): string {
  return `${Math.round(percentage)}%`
}

/**
 * Get compliance status color based on percentage
 * Follows NCA ECC color coding standards
 * 
 * @param percentage - Compliance percentage (0-100)
 * @returns Tailwind color class
 */
export function getComplianceColor(percentage: number): string {
  if (percentage >= 90) return 'text-green-600'
  if (percentage >= 70) return 'text-yellow-600'
  if (percentage >= 50) return 'text-orange-600'
  return 'text-red-600'
}

/**
 * Get risk level color
 * 
 * @param level - Risk level (critical, high, medium, low)
 * @returns Tailwind color class
 */
export function getRiskColor(level: string): string {
  const colors: Record<string, string> = {
    critical: 'text-red-600 bg-red-50',
    high: 'text-orange-600 bg-orange-50',
    medium: 'text-yellow-600 bg-yellow-50',
    low: 'text-green-600 bg-green-50',
  }
  return colors[level.toLowerCase()] || 'text-gray-600 bg-gray-50'
}

/**
 * Truncate text with ellipsis
 * 
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns Truncated text
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}
