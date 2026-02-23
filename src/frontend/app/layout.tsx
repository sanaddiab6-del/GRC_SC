
import type { Metadata } from 'next';
import './globals.css';
import React from 'react';

class GlobalErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean; error: any }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }
  componentDidCatch(error: any, info: any) {
    // Log error to console or external service
    console.error('Global error boundary caught:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-screen bg-background">
          <div className="text-center">
            <div className="text-red-600 text-lg font-bold mb-2">An unexpected error occurred.</div>
            <div className="text-gray-500 mb-2">{this.state.error?.message || String(this.state.error)}</div>
            <div className="text-gray-400 text-xs">Please check the browser console for details.</div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}


export const metadata: Metadata = {
  title: 'SICO GRC Platform | منصة سيكو للحوكمة',
  description: 'Saudi Regulatory Compliance Engine - ECC, CCC, PDPL',
};


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <GlobalErrorBoundary>{children}</GlobalErrorBoundary>;
}
