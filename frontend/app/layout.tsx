import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sanadcom GRC Platform',
  description: 'Saudi-compliant GRC platform with AI/RAG capabilities',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
