"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Star, Zap, ShoppingCart } from "lucide-react"
import { SimpleCheckout } from "@/components/simple-checkout"
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

interface GameCardsProps {
  selectedGame: string
  onBackToGames: () => void
}

export function GameCards({ selectedGame, onBackToGames }: GameCardsProps) {
  const [game, setGame] = useState<Game | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedCard, setSelectedCard] = useState<CardPackage | null>(null)
  const [showCheckout, setShowCheckout] = useState(false)

  useEffect(() => {
    fetchGame()
  }, [selectedGame])

  const fetchGame = async () => {
    try {
      const response = await fetch("/api/games")
      if (!response.ok) throw new Error("Network response was not ok")

      const games = await response.json()
      const foundGame = games.find((g: Game) => g.slug === selectedGame)
      setGame(foundGame || null)
    } catch (error) {
      console.error("Error fetching game:", error)
      setGame(null)
    } finally {
      setLoading(false)
    }
  }

  const handleBuyCard = (cardPackage: CardPackage) => {
    setSelectedCard(cardPackage)
    setShowCheckout(true)
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
        return "/placeholder.svg?height=400&width=600"
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-white text-xl font-bold">جاري التحميل...</p>
        </div>
      </div>
    )
  }

  if (!game) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-white text-xl font-bold mb-4">لم يتم العثور على اللعبة</p>
          <Button onClick={onBackToGames} className="bg-purple-600 hover:bg-purple-700">
            العودة للألعاب
          </Button>
        </div>
      </div>
    )
  }

  return (
    <section className="py-8 px-4 min-h-screen">
      <div className="container mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button
            onClick={onBackToGames}
            variant="outline"
            className="bg-white/10 border-white/20 text-white hover:bg-white/20"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            العودة للألعاب
          </Button>

          <div className="text-center">
            <h1 className="text-3xl md:text-5xl font-black text-white mb-2">🎮 {game.name} Store</h1>
            <p className="text-gray-300 font-semibold">{game.description}</p>
          </div>

          <div></div>
        </div>

        {/* Game Background Hero - استخدام الصورة الحقيقية بدلاً من الأيقونة المتحركة */}
        <div className="relative mb-12 rounded-3xl overflow-hidden">
          <div
            className="h-64 md:h-80 bg-cover bg-center"
            style={{
              backgroundImage: `url(${getGameBackground(game.slug)})`,
            }}
          />
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <div className="text-center">
              {/* استخدام الصورة الحقيقية للعبة بدلاً من الأيقونة */}
              <div className="w-32 h-32 mx-auto mb-4 rounded-2xl border-4 border-white/20 overflow-hidden bg-white/10 backdrop-blur-sm">
                <Image
                  src={getGameBackground(game.slug) || "/placeholder.svg"}
                  alt={game.name}
                  width={128}
                  height={128}
                  className="w-full h-full object-cover"
                />
              </div>
              <h2 className="text-4xl md:text-6xl font-black text-white mb-2">{game.name}</h2>
              <p className="text-xl text-gray-200 font-bold">🔥 أفضل العروض والأسعار 🔥</p>
            </div>
          </div>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {game.card_packages.map((cardPackage) => (
            <Card
              key={cardPackage.id}
              className="relative group hover:scale-105 transition-all duration-300 bg-white/5 backdrop-blur-sm border-2 border-purple-500/30 hover:border-purple-400/50 overflow-hidden"
            >
              {/* Card Image/Icon - استخدام صورة اللعبة بدلاً من الرمز المتحرك */}
              <div className="h-48 relative overflow-hidden">
                <Image
                  src={getGameBackground(game.slug) || "/placeholder.svg"}
                  alt={game.name}
                  fill
                  className="object-cover opacity-60"
                />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                  <div className="text-center z-10">
                    <div className="text-4xl mb-2">💎</div>
                    <div className="text-2xl font-black text-white">{cardPackage.points.toLocaleString()}</div>
                    <div className="text-sm text-gray-300 font-bold">نقطة</div>
                  </div>
                </div>

                {cardPackage.bonus_description && (
                  <Badge className="absolute top-2 right-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-bold">
                    <Star className="w-3 h-3 mr-1" />
                    BONUS
                  </Badge>
                )}
              </div>

              <CardHeader className="pb-2">
                <CardTitle className="text-lg font-black text-white text-center">{cardPackage.name}</CardTitle>
                <CardDescription className="text-center">
                  <div className="text-3xl font-black text-green-400 mb-2">{cardPackage.price_egp} جنيه</div>
                </CardDescription>
              </CardHeader>

              <CardContent className="pb-3">
                {cardPackage.bonus_description && (
                  <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-lg p-3 border border-yellow-500/30 mb-3">
                    <p className="text-sm text-yellow-300 font-bold text-center">🎁 {cardPackage.bonus_description}</p>
                  </div>
                )}

                <div className="flex items-center justify-center space-x-2 text-green-300 text-sm font-bold">
                  <Zap className="h-4 w-4" />
                  <span>توصيل فوري</span>
                </div>
              </CardContent>

              <CardFooter>
                <Button
                  onClick={() => handleBuyCard(cardPackage)}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-black py-3 text-lg"
                >
                  <ShoppingCart className="w-4 h-4 mr-2" />
                  اشتري الآن 🚀
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Simple Checkout Modal */}
        {selectedCard && (
          <SimpleCheckout
            isOpen={showCheckout}
            onClose={() => {
              setShowCheckout(false)
              setSelectedCard(null)
            }}
            game={game}
            cardPackage={selectedCard}
          />
        )}
      </div>
    </section>
  )
}
