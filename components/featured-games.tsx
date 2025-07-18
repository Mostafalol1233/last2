"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Gamepad2, Star, Crown, Zap, Plus } from "lucide-react"
import { useCart } from "@/components/cart-provider"
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

export function FeaturedGames() {
  const [games, setGames] = useState<Game[]>([])
  const [loading, setLoading] = useState(true)
  const { dispatch } = useCart()

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

  const addToCart = (game: Game, cardPackage: CardPackage) => {
    dispatch({
      type: "ADD_ITEM",
      payload: {
        id: `${game.id}-${cardPackage.id}`,
        gameId: game.id,
        gameName: game.name,
        packageName: cardPackage.name,
        points: cardPackage.points,
        price: cardPackage.price_egp,
        bonusDescription: cardPackage.bonus_description,
      },
    })

    // Show success feedback
    console.log(`Added ${cardPackage.name} to cart`)
  }

  const getGameBackground = (gameSlug: string) => {
    switch (gameSlug) {
      case "crossfire":
        return "/images/games/crossfire-bg.png"
      case "free-fire":
        return "/images/games/free-fire-bg.png"
      case "pubg-mobile":
        return "/images/games/pubg-mobile-bg.png"
      default:
        return "/placeholder.svg?height=200&width=300"
    }
  }

  const getGameGradient = (gameSlug: string) => {
    switch (gameSlug) {
      case "crossfire":
        return "from-red-900/80 via-red-800/60 to-red-900/80"
      case "free-fire":
        return "from-orange-900/80 via-orange-800/60 to-orange-900/80"
      case "pubg-mobile":
        return "from-blue-900/80 via-blue-800/60 to-blue-900/80"
      default:
        return "from-purple-900/80 via-purple-800/60 to-purple-900/80"
    }
  }

  if (loading) {
    return (
      <section className="py-16 bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-6xl font-black mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              🔥 LOADING GAMES 🔥
            </h2>
            <div className="mx-auto">
              <Gamepad2 className="h-16 w-16 text-purple-400 animate-spin" />
            </div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section
      className="py-20 bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 relative overflow-hidden"
      id="games"
    >
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div
          className="absolute top-20 left-20 w-40 h-40 bg-red-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "4s" }}
        />
        <div
          className="absolute bottom-20 right-20 w-32 h-32 bg-orange-500/10 rounded-full blur-2xl animate-bounce"
          style={{ animationDuration: "3s" }}
        />
        <div
          className="absolute top-1/2 left-1/4 w-24 h-24 bg-yellow-500/10 rounded-full blur-xl animate-pulse"
          style={{ animationDuration: "5s" }}
        />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="flex items-center space-x-3 bg-gradient-to-r from-red-500/20 to-orange-500/20 backdrop-blur-sm rounded-full px-8 py-4 border border-red-500/30">
                <Crown className="h-8 w-8 text-yellow-400 animate-bounce" style={{ animationDuration: "2s" }} />
                <span className="text-2xl font-black text-white">👑 FEATURED GAMES 👑</span>
                <Crown
                  className="h-8 w-8 text-yellow-400 animate-bounce"
                  style={{ animationDuration: "2s", animationDelay: "0.5s" }}
                />
              </div>
            </div>
          </div>

          <h2 className="text-5xl md:text-7xl font-black mb-6 text-white leading-tight">
            HOTTEST GAMES
            <br />
            <span className="text-6xl md:text-8xl bg-gradient-to-r from-yellow-400 to-red-400 bg-clip-text text-transparent">
              IN EGYPT! 🚀
            </span>
          </h2>

          <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto font-bold leading-relaxed">
            🎮 Choose from our popular gaming titles and get instant top-ups
            <br />
            <span className="text-yellow-400 animate-pulse" style={{ animationDuration: "2s" }}>
              🔥 WITH AMAZING BONUS OFFERS! 🔥
            </span>
          </p>
        </div>

        <div className="grid gap-12">
          {games.map((game, gameIndex) => (
            <div
              key={game.id}
              className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-800/50 via-purple-800/30 to-slate-800/50 backdrop-blur-sm border-2 border-purple-500/30 hover:border-purple-400/50 transition-all duration-500 group"
            >
              <div className="p-6 md:p-8 border-b border-purple-500/20">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                  <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6">
                    <div className="relative">
                      <div className="w-20 h-20 md:w-24 md:h-24 rounded-2xl overflow-hidden border-2 border-purple-500/30 group-hover:border-orange-500/50 transition-colors">
                        <Image
                          src={game.image_url || "/placeholder.svg"}
                          alt={game.name}
                          width={96}
                          height={96}
                          className="object-cover w-full h-full"
                        />
                      </div>
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center animate-pulse">
                        <Zap className="h-3 w-3 text-white" />
                      </div>
                    </div>
                    <div className="text-center md:text-left">
                      <h3 className="text-3xl md:text-4xl font-black text-white mb-2 group-hover:text-orange-300 transition-colors">
                        {game.name}
                      </h3>
                      <p className="text-gray-300 text-base md:text-lg font-semibold">{game.description}</p>
                    </div>
                  </div>

                  <div className="flex flex-col items-center md:items-end space-y-2">
                    <Badge className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 text-green-300 border-green-500/30 font-bold">
                      <Zap className="w-4 h-4 mr-1" />
                      INSTANT DELIVERY
                    </Badge>
                    <Badge className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 text-yellow-300 border-yellow-500/30 font-bold">
                      <Star className="w-4 h-4 mr-1" />
                      BEST PRICES
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="p-6 md:p-8">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {game.card_packages.map((cardPackage, cardIndex) => (
                    <Card
                      key={cardPackage.id}
                      className="relative group/card hover:scale-105 transition-all duration-300 overflow-hidden border-2 border-purple-500/20 hover:border-orange-500/50 min-h-[400px]"
                    >
                      {/* Background Image */}
                      <div
                        className="absolute inset-0 bg-cover bg-center"
                        style={{
                          backgroundImage: `url(${getGameBackground(game.slug)})`,
                        }}
                      />

                      {/* Dark overlay for better text readability */}
                      <div className="absolute inset-0 bg-black/70 backdrop-blur-[1px]" />

                      <CardHeader className="pb-3 relative z-10">
                        <div className="flex justify-between items-start">
                          <CardTitle className="text-lg font-black text-white group-hover/card:text-orange-300 transition-colors drop-shadow-lg">
                            {cardPackage.name}
                          </CardTitle>
                          {cardPackage.bonus_description && (
                            <Badge
                              variant="secondary"
                              className="bg-gradient-to-r from-yellow-500/90 to-orange-500/90 text-white border-yellow-500/50 font-bold shadow-lg"
                            >
                              <Star className="w-3 h-3 mr-1" />
                              BONUS
                            </Badge>
                          )}
                        </div>
                        <CardDescription className="text-gray-200 font-bold text-lg drop-shadow-lg">
                          🎯 {cardPackage.points.toLocaleString()} Points
                        </CardDescription>
                      </CardHeader>

                      <CardContent className="pb-3 relative z-10">
                        <div className="text-2xl md:text-3xl font-black text-green-400 mb-3 drop-shadow-lg">
                          💰 {cardPackage.price_egp} EGP
                        </div>
                        {cardPackage.bonus_description && (
                          <div className="bg-gradient-to-r from-yellow-500/90 to-orange-500/90 rounded-lg p-3 border border-yellow-500/50 backdrop-blur-sm">
                            <p className="text-sm text-white font-bold drop-shadow">
                              🎁 {cardPackage.bonus_description}
                            </p>
                          </div>
                        )}
                      </CardContent>

                      <CardFooter className="relative z-10">
                        <Button
                          className="w-full bg-gradient-to-r from-red-600 via-orange-600 to-yellow-600 hover:from-red-700 hover:via-orange-700 hover:to-yellow-700 text-white font-black shadow-2xl hover:shadow-orange-500/50 transition-all duration-300 transform hover:scale-105 py-3 text-lg"
                          onClick={() => addToCart(game, cardPackage)}
                        >
                          <Plus className="w-5 h-5 mr-2" />🛒 ADD TO CART
                        </Button>
                      </CardFooter>

                      {/* Corner Effects */}
                      <div className="absolute top-2 right-2 z-10">
                        <Star className="h-4 w-4 text-orange-400 animate-pulse drop-shadow-lg" />
                      </div>
                      <div className="absolute bottom-2 left-2 z-10">
                        <Crown className="h-4 w-4 text-yellow-400 animate-pulse drop-shadow-lg" />
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
