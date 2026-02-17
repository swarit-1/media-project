import type { Metadata } from "next";
import { Toaster } from "@/components/ui/sonner";
import { QueryProvider } from "@/lib/providers/query-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Elastic",
  description: "B2B platform connecting newsrooms with freelance journalists",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans">
        <QueryProvider>
          {children}
        </QueryProvider>
        <Toaster position="bottom-right" />
      </body>
    </html>
  );
}
