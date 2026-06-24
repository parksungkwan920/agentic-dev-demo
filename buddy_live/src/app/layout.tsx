import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '버디버디',
  description: '로컬 네트워크 실시간 채팅',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="h-screen overflow-hidden bg-white">{children}</body>
    </html>
  )
}
