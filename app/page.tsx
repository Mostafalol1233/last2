"use client"

import { useState } from "react"
import { GameSelection } from "@/components/game-selection"
import { GameCards } from "@/components/game-cards"
import { Header } from "@/components/header"
import { ContactSection } from "@/components/contact-section"

export default function HomePage() {
  const [selectedGame, setSelectedGame] = useState<string | null>(null)

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Header />

      {!selectedGame ? (
        <>
          <GameSelection onGameSelect={setSelectedGame} />
          <ContactSection />
        </>
      ) : (
        <GameCards selectedGame={selectedGame} onBackToGames={() => setSelectedGame(null)} />
      )}
    </main>
  )
}
