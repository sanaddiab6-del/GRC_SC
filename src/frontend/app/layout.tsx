import type { Metadata } from 'next';
import { Inter, Cairo } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const cairo = Cairo({ subsets: ['arabic'], variable: '--font-cairo' });

export const metadata: Metadata = {
  title: 'SICO GRC Platform | منصة سيكو للحوكمة',
  description: 'Saudi Regulatory Compliance Engine - ECC, CCC, PDPL',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body className={`${inter.variable} ${cairo.variable}`}>
        {children}
      </body>
    </html>
  );
}
