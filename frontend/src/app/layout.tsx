import type { Metadata } from "next";
import "./globals.css";

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
        <div className="min-h-screen bg-background">
          {children}
        </div>
      </body>
    </html>
  );
}