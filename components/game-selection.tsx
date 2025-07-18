"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Crown, Gamepad2, Zap } from "lucide-react"
import Image from "next/image"

interface GameSelectionProps {
  onGameSelect: (gameSlug: string) => void
}

export function GameSelection({ onGameSelect }: GameSelectionProps) {
  const games = [
    {
      slug: "crossfire",
      name: "CrossFire",
      description: "أفضل أسعار كروت CrossFire في مصر",
      image: "/images/games/crossfire-bg.png",
      logo: "/images/game-logos/crossfire-logo.png",
      gradient: "from-red-500 to-orange-500",
      bgGradient: "from-red-900/20 to-orange-900/20",
      borderColor: "border-red-500/30",
      emoji: "🎯",
    },
    {
      slug: "free-fire",
      name: "Free Fire",
      description: "احصل على الماس بأفضل الأسعار",
      image: "/images/games/free-fire-bg.png",
      logo: "/images/game-logos/free-fire-logo.png",
      gradient: "from-orange-500 to-yellow-500",
      bgGradient: "from-orange-900/20 to-yellow-900/20",
      borderColor: "border-orange-500/30",
      emoji: "🔥",
    },
    {
      slug: "pubg-mobile",
      name: "PUBG Mobile",
      description: "كروت UC بأسعار لا تقاوم",
      image: "/images/games/pubg-mobile-bg.png",
      logo: "/images/game-logos/pubg-mobile-logo.png",
      gradient: "from-blue-500 to-cyan-500",
      bgGradient: "from-blue-900/20 to-cyan-900/20",
      borderColor: "border-blue-500/30",
      emoji: "🏆",
    },
  ]

  return (
    <section className="py-20 px-4 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-20 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-32 h-32 bg-violet-500/10 rounded-full blur-2xl animate-bounce" />
        <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-pink-500/10 rounded-full blur-xl animate-pulse" />
      </div>

      <div className="container mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <div className="flex items-center space-x-3 bg-gradient-to-r from-purple-500/20 to-violet-500/20 backdrop-blur-sm rounded-full px-8 py-4 border border-purple-500/30">
              <Crown className="h-8 w-8 text-yellow-400 animate-bounce" />
              <span className="text-2xl font-black text-white">👑 اختر لعبتك 👑</span>
              <Crown className="h-8 w-8 text-yellow-400 animate-bounce" />
            </div>
          </div>

          <h1 className="text-5xl md:text-7xl font-black mb-6 text-white leading-tight">
            🎮 CHOOSE YOUR
            <br />
            <span className="text-6xl md:text-8xl bg-gradient-to-r from-yellow-400 to-red-400 bg-clip-text text-transparent">
              FAVORITE GAME! 🚀
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto font-bold leading-relaxed">
            🔥 اختر لعبتك المفضلة واحصل على أفضل العروض
            <br />
            <span className="text-yellow-400 animate-pulse">⚡ أسعار مميزة • توصيل فوري • دعم 24/7 ⚡</span>
          </p>
        </div>

        {/* Games Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {games.map((game) => (
            <Card
              key={game.slug}
              className={`relative group cursor-pointer transform transition-all duration-500 hover:scale-105 bg-gradient-to-br ${game.bgGradient} backdrop-blur-sm border-2 ${game.borderColor} hover:border-opacity-100 overflow-hidden min-h-[400px]`}
              onClick={() => onGameSelect(game.slug)}
            >
              {/* Background Image */}
              <div
                className="absolute inset-0 bg-cover bg-center opacity-30 group-hover:opacity-50 transition-opacity"
                style={{
                  backgroundImage: `url(${game.image})`,
                }}
              />

              {/* Dark overlay */}
              <div className="absolute inset-0 bg-black/60" />

              <CardHeader className="relative z-10 text-center pb-4">
                <div className="flex justify-center mb-4">
                  <div className="relative">
                    <div className="w-24 h-24 rounded-2xl bg-white/10 backdrop-blur-sm flex items-center justify-center shadow-2xl border border-white/20 overflow-hidden">
                      <Image
                        src={game.logo || "/placeholder.svg"}
                        alt={game.name}
                        width={80}
                        height={80}
                        className="object-contain"
                      />
                    </div>
                    <div className="absolute -top-2 -right-2 text-3xl animate-bounce">{game.emoji}</div>
                  </div>
                </div>

                <CardTitle className="text-2xl md:text-3xl font-black text-white mb-2 group-hover:text-yellow-300 transition-colors">
                  {game.name}
                </CardTitle>
              </CardHeader>

              <CardContent className="relative z-10 text-center">
                <p className="text-gray-300 group-hover:text-white font-bold mb-6 text-lg leading-relaxed">
                  {game.description}
                </p>

                <div className="space-y-3 mb-6">
                  <div className="flex items-center justify-center space-x-2 text-green-300">
                    <Zap className="h-4 w-4" />
                    <span className="font-bold">توصيل فوري</span>
                  </div>
                  <div className="flex items-center justify-center space-x-2 text-yellow-300">
                    <Crown className="h-4 w-4" />
                    <span className="font-bold">أفضل الأسعار</span>
                  </div>
                  <div className="flex items-center justify-center space-x-2 text-blue-300">
                    <Gamepad2 className="h-4 w-4" />
                    <span className="font-bold">دعم 24/7</span>
                  </div>
                </div>

                <Button
                  className={`w-full bg-gradient-to-r ${game.gradient} hover:shadow-xl text-white font-black py-4 text-lg rounded-xl transform hover:scale-105 transition-all duration-300`}
                >
                  اختر {game.name} 🚀
                </Button>
              </CardContent>

              {/* Corner Effects */}
              <div className="absolute top-4 right-4 z-10">
                <Crown className="h-5 w-5 text-yellow-400 animate-pulse" />
              </div>
              <div className="absolute bottom-4 left-4 z-10">
                <Zap className="h-5 w-5 text-green-400 animate-pulse" />
              </div>
            </Card>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <div className="bg-gradient-to-r from-purple-500/20 to-violet-500/20 rounded-2xl p-8 border border-violet-500/30 max-w-4xl mx-auto">
            <h3 className="text-3xl md:text-4xl font-black mb-4 text-white">🔥 لماذا نحن الأفضل؟ 🔥</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div>
                <div className="text-4xl mb-2">⚡</div>
                <h4 className="font-black text-yellow-400 text-lg">توصيل فوري</h4>
                <p className="text-gray-300 font-semibold">خلال دقائق معدودة</p>
              </div>
              <div>
                <div className="text-4xl mb-2">💰</div>
                <h4 className="font-black text-green-400 text-lg">أفضل الأسعار</h4>
                <p className="text-gray-300 font-semibold">عروض وخصومات مميزة</p>
              </div>
              <div>
                <div className="text-4xl mb-2">🛡️</div>
                <h4 className="font-black text-blue-400 text-lg">آمان 100%</h4>
                <p className="text-gray-300 font-semibold">معاملات آمنة ومضمونة</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
