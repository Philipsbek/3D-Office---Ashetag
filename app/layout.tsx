import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import ClientScene from '@/components/ClientScene'
import Nav from '@/components/Nav'
import SectionNav from '@/components/SectionNav'
import WhatsAppButton from '@/components/WhatsAppButton'
import Memo from '@/components/Memo'
import './globals.css'

const geist = Geist({ subsets: ['latin'], weight: ['500', '600'], variable: '--font-geist' })
const geistMono = Geist_Mono({ subsets: ['latin'], weight: ['600'], variable: '--font-geist-mono' })

export const metadata: Metadata = {
  title: 'Philips Bek — Web Developer',
  description: 'Philips Bek is a web developer who builds fast, modern websites: landing pages, business sites, online stores and web apps.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geist.variable} ${geistMono.variable}`}>
      <body>
        {/* The 3D canvas sits behind every page and never unmounts.
            On the homepage it is the hero; in a section it fills the screen. */}
        <ClientScene />
        <Nav />
        <main>{children}</main>
        <SectionNav />
        <WhatsAppButton />
        <Memo />
      </body>
    </html>
  )
}
