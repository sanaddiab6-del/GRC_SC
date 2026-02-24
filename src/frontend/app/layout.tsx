import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SICO GRC Platform | منصة سيكو للحوكمة",
  description: "Saudi Regulatory Compliance Engine - ECC, CCC, PDPL",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
