import type { Metadata } from "next";
import "./globals.css";
import Navbar from "./components/Navbar";

export const metadata: Metadata = {
  title: "SpeakNara - AI Lak Public Speaking Coach",
  description: "Master public speaking in Lak language with AI-powered coaching",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans">
        <Navbar />
        {children}
      </body>
    </html>
  );
}
