"use client"

import Image from "next/image"

export function BrandMarquee() {
  const brands = [
    { name: "🎮 CrossFire", color: "text-red-400" },
    { name: "🔥 Free Fire", color: "text-orange-400" },
    { name: "🏆 PUBG Mobile", color: "text-blue-400" },
    { name: "📱 Vodafone Cash", color: "text-red-500", icon: "/images/payments/vodafone.png" },
    { name: "🧡 Orange Money", color: "text-orange-500", icon: "/images/payments/orange-money.png" },
    { name: "💜 WE Pay", color: "text-purple-500", icon: "/images/payments/we-pay.png" },
    { name: "⚡ InstaPay", color: "text-violet-500", icon: "/images/payments/instapay.png" },
    { name: "💳 Visa", color: "text-blue-600", icon: "/images/payments/visa.png" },
    { name: "💳 Mastercard", color: "text-red-600", icon: "/images/payments/mastercard.png" },
    { name: "🎯 24/7 Support", color: "text-pink-400" },
  ]

  return (
    <div className="bg-gradient-to-r from-slate-900 via-purple-900 to-violet-900 border-y-2 border-purple-500/30 py-6 overflow-hidden relative">
      {/* Simple Background */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 via-violet-500/5 to-purple-500/5" />

      <div className="flex animate-marquee whitespace-nowrap">
        {[...brands, ...brands, ...brands].map((brand, index) => (
          <div key={index} className="mx-8 flex items-center">
            {brand.icon ? (
              <div className="flex items-center space-x-2">
                <Image
                  src={brand.icon || "/placeholder.svg"}
                  alt={brand.name}
                  width={24}
                  height={24}
                  className="object-contain"
                />
                <span
                  className={`text-xl font-black ${brand.color} hover:scale-110 transition-transform cursor-pointer`}
                >
                  {brand.name}
                </span>
              </div>
            ) : (
              <span
                className={`text-2xl font-black ${brand.color} hover:scale-110 transition-transform cursor-pointer`}
              >
                {brand.name}
              </span>
            )}
            <div className="w-3 h-3 bg-gradient-to-r from-purple-400 to-violet-400 rounded-full ml-6" />
          </div>
        ))}
      </div>
    </div>
  )
}
