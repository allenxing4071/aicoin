import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AIcoin - AI Trading System',
  description: 'AI-powered cryptocurrency trading system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  )
}

