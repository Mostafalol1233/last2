"use client"
import { ModeToggle } from "@/components/mode-toggle"
import { Gamepad2 } from "lucide-react"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-purple-500/20 bg-slate-900/95 backdrop-blur-xl">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Gamepad2 className="h-8 w-8 text-purple-400" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Diaa ElDeen
              </h1>
              <p className="text-xs text-gray-400 font-semibold">by Diaa El Deen Sadek</p>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            <ModeToggle />
          </div>
        </div>
      </div>
    </header>
  )
}
