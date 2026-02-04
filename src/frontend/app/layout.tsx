import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SICO GRC Platform | Saudi Regulatory Compliance',
  description: 'Comprehensive GRC solution for ECC, CCC, and PDPL compliance',
  keywords: ['GRC', 'ECC', 'CCC', 'PDPL', 'Saudi Arabia', 'Compliance', 'Cybersecurity'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className="min-h-screen bg-gray-50 antialiased">
        {children}
      </body>
    </html>
  )
}
