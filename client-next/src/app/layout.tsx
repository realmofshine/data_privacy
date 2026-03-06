import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Data Privacy & Security Intelligence Platform",
  description: "AI-powered data privacy platform with 55 agents across 15 operational modes",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
