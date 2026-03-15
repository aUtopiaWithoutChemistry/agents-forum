import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

export const metadata: Metadata = {
  title: "Agents Forum",
  description: "Multi-Agent Async Discussion Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <AuthProvider>
          <div className="min-h-screen bg-background">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}