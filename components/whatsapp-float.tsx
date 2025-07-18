"use client"

import { MessageCircle } from "lucide-react"

export function WhatsAppFloat() {
  const handleClick = () => {
    window.open("https://wa.me/201011696196?text=🎮 Hi! I need help with game cards", "_blank")
  }

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-6 right-6 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white p-4 rounded-full shadow-2xl transition-all duration-300 hover:scale-110 z-50 animate-pulse hover:animate-none"
      aria-label="Contact us on WhatsApp"
    >
      <MessageCircle className="h-6 w-6" />
      <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-ping" />
    </button>
  )
}
