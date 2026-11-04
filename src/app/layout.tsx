import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SalsaRide - Smart Adaptive Traffic Signal Optimizer',
  description: 'Alleviating urban traffic congestion through dynamic multi-corridor vehicle density tracking and intelligent phase timing.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-zinc-950 text-zinc-100 antialiased">
        {children}
      </body>
    </html>
  );
}

