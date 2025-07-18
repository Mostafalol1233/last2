"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Gamepad2, Star, ShoppingCart, Zap, Trophy, Target } from "lucide-react"
import Image from "next/image"

interface CardPackage {
  id: string
  name: string
  points: number
  price_egp: number
  bonus_description: string
  is_active: boolean
  sort_order: number
}

interface Game {
  id: string
  name: string
  slug: string
  description: string
  image_url: string
  is_active: boolean
  card_packages: CardPackage[]
}

interface GamesCatalogProps {
  selectedGame: string | null
}

export function GamesCatalog({ selectedGame }: GamesCatalogProps) {
  const [games, setGames] = useState<Game[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchGames()
  }, [])

  const fetchGames = async () => {
    try {
      const response = await fetch("/api/games", { cache: "no-store" })
      if (!response.ok) throw new Error("Network response was not ok")

      const payload = await response.json()
      setGames(Array.isArray(payload) ? payload : [])
    } catch (error) {
      console.error("Error fetching games:", error)
      setGames([])
    } finally {
      setLoading(false)
    }
  }

  const handleBuyClick = (game: Game, cardPackage: CardPackage) => {
    const message = `🎮 Hi! I want to buy ${cardPackage.name} for ${game.name}\n💰 Price: ${cardPackage.price_egp} EGP\n🎯 Points: ${cardPackage.points.toLocaleString()}\n${cardPackage.bonus_description ? `🎁 Bonus: ${cardPackage.bonus_description}` : ""}`
    const whatsappUrl = `https://wa.me/201011696196?text=${encodeURIComponent(message)}`
    window.open(whatsappUrl, "_blank")
  }

  const filteredGames = selectedGame ? games.filter((game) => game.slug === selectedGame) : games

  const getGameIcon = (gameSlug: string) => {
    switch (gameSlug) {
      case "crossfire":
        return <Target className="h-6 w-6 text-red-400" />
      case "free-fire":
        return <Zap className="h-6 w-6 text-orange-400" />
      case "pubg-mobile":
        return <Trophy className="h-6 w-6 text-blue-400" />
      default:
        return <Gamepad2 className="h-6 w-6 text-purple-400" />
    }
  }

  const getGameGradient = (gameSlug: string) => {
    switch (gameSlug) {
      case "crossfire":
        return "from-red-500/20 to-orange-500/20"
      case "free-fire":
        return "from-orange-500/20 to-yellow-500/20"
      case "pubg-mobile":
        return "from-blue-500/20 to-cyan-500/20"
      default:
        return "from-purple-500/20 to-pink-500/20"
    }
  }

  if (loading) {
    return (
      <section className="py-8 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center space-x-2 bg-purple-500/10 backdrop-blur-sm rounded-full px-6 py-3 mb-6">
              <Gamepad2 className="h-6 w-6 text-purple-400 animate-spin" />
              <span className="text-purple-300 font-medium">Loading Games...</span>
            </div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="py-8 px-4">
      <div className="container mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center space-x-2 bg-purple-500/10 backdrop-blur-sm rounded-full px-6 py-3 mb-6">
            <Gamepad2 className="h-6 w-6 text-purple-400" />
            <span className="text-purple-300 font-medium">
              {selectedGame ? `${filteredGames[0]?.name || "Game"} Cards` : "All Game Cards"}
            </span>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-purple-400 via-pink-400 to-red-400 bg-clip-text text-transparent">
            {selectedGame ? `${filteredGames[0]?.name || "Game"} Store` : "Game Cards Store"}
          </h1>

          <p className="text-gray-300 dark:text-gray-400 max-w-2xl mx-auto text-lg">
            {selectedGame
              ? `Get the best ${filteredGames[0]?.name || "game"} cards with instant delivery and amazing bonuses!`
              : "Choose from our popular gaming titles and get instant top-ups with amazing bonus offers"}
          </p>
        </div>

        {/* Games Grid */}
        <div className="grid gap-8">
          {filteredGames.map((game) => (
            <div
              key={game.id}
              className={`relative overflow-hidden rounded-3xl bg-gradient-to-br ${getGameGradient(game.slug)} backdrop-blur-sm border border-white/10`}
            >
              {/* Game Header */}
              <div className="p-6 border-b border-white/10">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="relative">
                      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm flex items-center justify-center border border-white/20">
                        {getGameIcon(game.slug)} {/* Reverted to Lucide icon */}
                      </div>
                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full" />
                    </div>
                    <div>
                      <h3 className="text-3xl font-bold text-white mb-1">{game.name}</h3>
                      <p className="text-gray-300">{game.description}</p>
                    </div>
                  </div>

                  <Badge className="bg-green-500/20 text-green-300 border-green-500/30">
                    <Zap className="w-3 h-3 mr-1" />
                    Instant Delivery
                  </Badge>
                </div>
              </div>

              {/* Cards Grid */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {game.card_packages.map((cardPackage) => (
                    <Card
                      key={cardPackage.id}
                      className="relative group hover:scale-105 transition-all duration-300 bg-white/5 backdrop-blur-sm border-white/10 hover:border-white/20 hover:bg-white/10"
                    >
                      <CardHeader className="pb-3">
                        <div className="flex justify-center mb-2">
                          <Image
                            src="/images/generic-card.png" // Generic card image
                            alt="Game Card"
                            width={80}
                            height={80}
                            className="object-contain"
                          />
                        </div>
                        <div className="flex justify-between items-start">
                          <CardTitle className="text-lg text-white group-hover:text-purple-300 transition-colors">
                            {cardPackage.name}
                          </CardTitle>
                          {cardPackage.bonus_description && (
                            <Badge
                              variant="secondary"
                              className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30"
                            >
                              <Star className="w-3 h-3 mr-1" />
                              Bonus
                            </Badge>
                          )}
                        </div>
                        <CardDescription className="text-gray-300">
                          {cardPackage.points.toLocaleString()} Points
                        </CardDescription>
                      </CardHeader>

                      <CardContent className="pb-3">
                        <div className="text-3xl font-bold text-green-400 mb-2">{cardPackage.price_egp} EGP</div>
                        {cardPackage.bonus_description && (
                          <p className="text-sm text-gray-400 bg-white/5 rounded-lg p-2">
                            🎁 {cardPackage.bonus_description}
                          </p>
                        )}
                      </CardContent>

                      <CardFooter>
                        <Button
                          className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold shadow-lg hover:shadow-green-500/25 transition-all duration-300"
                          onClick={() => handleBuyClick(game, cardPackage)}
                        >
                          <ShoppingCart className="w-4 h-4 mr-2" />
                          Buy Now
                        </Button>
                      </CardFooter>

                      {/* Hover effect */}
                      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 to-pink-500/0 group-hover:from-purple-500/10 group-hover:to-pink-500/10 rounded-lg transition-all duration-300 pointer-events-none" />
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredGames.length === 0 && (
          <div className="text-center py-16">
            <Gamepad2 className="h-16 w-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">No games found</h3>
            <p className="text-gray-500">Try selecting a different game or check back later.</p>
          </div>
        )}
      </div>
    </section>
  )
}
