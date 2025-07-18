import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { WhatsAppFloat } from "@/components/whatsapp-float"
import { Toaster } from "@/components/ui/toaster"
import { RemoveV0Badge } from "@/components/remove-v0-badge"
import { CartProvider } from "@/components/cart-provider"
import { Analytics } from "@vercel/analytics/next"
import { Suspense } from "react"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Buy Game Cards Online | Diaa El Deen Sadek",
  description:
    "Buy prepaid CrossFire, Free Fire, and PUBG cards in Egypt with bonus deals, easy manual payments, and instant delivery.",
  keywords: "game cards, CrossFire, Free Fire, PUBG, Egypt, gaming, top up, digital cards",
  authors: [{ name: "Diaa El Deen Sadek" }],
  openGraph: {
    title: "Buy Game Cards Online | Diaa El Deen Sadek",
    description:
      "Buy prepaid CrossFire, Free Fire, and PUBG cards in Egypt with bonus deals, easy manual payments, and instant delivery.",
    type: "website",
  },
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <CartProvider>
          <Suspense fallback={null}>
            {children}
            <WhatsAppFloat />
            <Toaster />
            <RemoveV0Badge />
          </Suspense>
          <Analytics />
        </CartProvider>
      </body>
    </html>
  )
}
