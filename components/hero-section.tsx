import { Button } from "@/components/ui/button"
import { ArrowRight, Zap, Crown } from "lucide-react"
import Image from "next/image"

export function HeroSection() {
  return (
    <section className="relative bg-gradient-to-br from-purple-900 via-violet-900 to-indigo-900 text-white overflow-hidden min-h-screen flex items-center">
      {/* Gaming Hero Image */}
      <div className="absolute inset-0 z-0">
        <Image
          src="/images/gaming-hero.png"
          alt="Gaming Background"
          fill
          className="object-cover opacity-40"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/80 via-violet-900/70 to-indigo-900/80" />
      </div>

      {/* Simple Background Elements */}
      <div className="absolute inset-0 z-10">
        <div className="absolute top-10 left-10 w-32 h-32 bg-purple-500/20 rounded-full blur-3xl" />
        <div className="absolute top-20 right-20 w-24 h-24 bg-violet-500/30 rounded-full blur-2xl" />
        <div className="absolute bottom-20 left-1/4 w-40 h-40 bg-pink-500/15 rounded-full blur-3xl" />
        <div className="absolute bottom-40 right-1/3 w-28 h-28 bg-purple-400/20 rounded-full blur-2xl" />
      </div>

      <div className="relative container mx-auto px-4 py-20 lg:py-32 z-20">
        <div className="max-w-4xl mx-auto text-center">
          {/* Gaming Badge */}
          <div className="flex justify-center mb-6">
            <div className="flex items-center space-x-2 bg-gradient-to-r from-purple-500/20 to-violet-500/20 backdrop-blur-sm rounded-full px-6 py-3 border border-purple-500/30">
              <Zap className="h-6 w-6 text-violet-400" />
              <span className="text-lg font-bold bg-gradient-to-r from-violet-300 to-pink-300 bg-clip-text text-transparent">
                🎮 INSTANT GAMING DELIVERY 🎮
              </span>
            </div>
          </div>

          {/* Main Title */}
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-black mb-8 leading-tight">
            <span className="block bg-gradient-to-r from-purple-400 via-violet-400 to-pink-400 bg-clip-text text-transparent">
              TOP-UP YOUR
            </span>
            <span className="block bg-gradient-to-r from-pink-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
              FAVORITE GAME
            </span>
            <span className="block text-6xl md:text-8xl bg-gradient-to-r from-violet-500 to-purple-500 bg-clip-text text-transparent">
              INSTANTLY! 🚀
            </span>
          </h1>

          <p className="text-xl md:text-3xl mb-10 text-violet-100 max-w-3xl mx-auto font-semibold">
            🎮 Get the HOTTEST deals on CrossFire, Free Fire, and PUBG cards in Egypt!
            <br />
            <span className="text-pink-300">⚡ FAST • SECURE • AMAZING BONUSES! ⚡</span>
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-12">
            <Button
              size="lg"
              className="group relative bg-gradient-to-r from-purple-600 via-violet-600 to-pink-600 hover:from-purple-700 hover:via-violet-700 hover:to-pink-700 text-white font-black px-12 py-6 text-xl rounded-2xl shadow-2xl hover:shadow-violet-500/50 transform hover:scale-105 transition-all duration-300"
            >
              <div className="relative flex items-center">
                <Crown className="mr-3 h-6 w-6" />🎮 BROWSE GAMES 🎮
                <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-1 transition-transform" />
              </div>
            </Button>

            <div className="flex items-center space-x-6 text-lg font-bold">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-green-400 rounded-full mr-3" />
                <span className="text-green-300">24/7 SUPPORT</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-blue-400 rounded-full mr-3" />
                <span className="text-blue-300">SECURE PAYMENT</span>
              </div>
            </div>
          </div>

          {/* Gaming Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-4xl font-black text-pink-400 mb-2">1000+</div>
              <div className="text-violet-200 font-semibold">Happy Gamers</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-black text-purple-400 mb-2">24/7</div>
              <div className="text-violet-200 font-semibold">Fast Support</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-black text-violet-400 mb-2">100%</div>
              <div className="text-violet-200 font-semibold">Secure</div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0 z-30">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-16 fill-white">
          <path
            d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z"
            opacity=".25"
          ></path>
          <path
            d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z"
            opacity=".5"
          ></path>
          <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z"></path>
        </svg>
      </div>
    </section>
  )
}
