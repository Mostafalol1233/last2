"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Zap, Star, Crown, CreditCard } from "lucide-react"
import { useState, useEffect } from "react"
import Image from "next/image"

export function PaymentMethods() {
  const [activeCard, setActiveCard] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCard((prev) => (prev + 1) % 7)
    }, 4000) // Slower animation
    return () => clearInterval(interval)
  }, [])

  const paymentMethods = [
    {
      name: "Vodafone Cash",
      icon: "/images/payments/vodafone.png",
      description: "الدفع السريع عبر فودافون كاش",
      color: "from-red-500 to-red-700",
      bgColor: "bg-red-500/20",
      borderColor: "border-red-500/50",
      textColor: "text-red-400",
      emoji: "📱",
      features: ["فوري", "آمن", "سهل"],
    },
    {
      name: "Orange Money",
      icon: "/images/payments/orange-money.png",
      description: "دفع مريح عبر أورانج موني",
      color: "from-orange-500 to-orange-700",
      bgColor: "bg-orange-500/20",
      borderColor: "border-orange-500/50",
      textColor: "text-orange-400",
      emoji: "🧡",
      features: ["سريع", "موثوق", "مضمون"],
    },
    {
      name: "WE Pay",
      icon: "/images/payments/we-pay.png",
      description: "دفع آمن عبر WE Pay",
      color: "from-purple-500 to-purple-700",
      bgColor: "bg-purple-500/20",
      borderColor: "border-purple-500/50",
      textColor: "text-purple-400",
      emoji: "💜",
      features: ["آمن", "سريع", "مريح"],
    },
    {
      name: "CIB Bank",
      icon: "/images/payments/cib-bank.png",
      description: "تحويل بنكي آمن عبر CIB",
      color: "from-blue-500 to-blue-700",
      bgColor: "bg-blue-500/20",
      borderColor: "border-blue-500/50",
      textColor: "text-blue-400",
      emoji: "🏦",
      features: ["آمن", "مضمون", "رسمي"],
    },
    {
      name: "InstaPay",
      icon: "/images/payments/instapay.png",
      description: "دفع فوري عبر InstaPay",
      color: "from-violet-500 to-violet-700",
      bgColor: "bg-violet-500/20",
      borderColor: "border-violet-500/50",
      textColor: "text-violet-400",
      emoji: "⚡",
      features: ["فوري", "آمن", "سهل"],
    },
    {
      name: "Visa",
      icon: "/images/payments/visa.png",
      description: "ادفع بكارت Visa الخاص بك",
      color: "from-blue-600 to-blue-800",
      bgColor: "bg-blue-600/20",
      borderColor: "border-blue-600/50",
      textColor: "text-blue-500",
      emoji: "💳",
      features: ["عالمي", "آمن", "سريع"],
    },
    {
      name: "Mastercard",
      icon: "/images/payments/mastercard.png",
      description: "ادفع بكارت Mastercard",
      color: "from-red-600 to-orange-600",
      bgColor: "bg-red-600/20",
      borderColor: "border-red-600/50",
      textColor: "text-red-500",
      emoji: "💳",
      features: ["عالمي", "موثوق", "آمن"],
    },
  ]

  return (
    <section
      className="py-20 bg-gradient-to-br from-slate-900 via-purple-900 to-violet-900 relative overflow-hidden"
      id="payment"
    >
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div
          className="absolute top-20 left-20 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "6s" }}
        />
        <div
          className="absolute bottom-20 right-20 w-32 h-32 bg-violet-500/10 rounded-full blur-2xl animate-bounce"
          style={{ animationDuration: "4s" }}
        />
        <div
          className="absolute top-1/2 left-1/4 w-24 h-24 bg-pink-500/10 rounded-full blur-xl animate-pulse"
          style={{ animationDuration: "5s" }}
        />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="flex items-center space-x-3 bg-gradient-to-r from-purple-500/20 to-violet-500/20 backdrop-blur-sm rounded-full px-8 py-4 border border-purple-500/30">
                <CreditCard className="h-8 w-8 text-violet-400 animate-bounce" style={{ animationDuration: "2s" }} />
                <span className="text-2xl font-black bg-gradient-to-r from-purple-300 to-violet-300 bg-clip-text text-transparent">
                  💳 PAYMENT METHODS 💳
                </span>
                <CreditCard
                  className="h-8 w-8 text-violet-400 animate-bounce"
                  style={{ animationDuration: "2s", animationDelay: "0.5s" }}
                />
              </div>
            </div>
          </div>

          <h2 className="text-4xl md:text-7xl font-black mb-6 bg-gradient-to-r from-purple-400 via-violet-400 to-pink-400 bg-clip-text text-transparent leading-tight">
            CHOOSE YOUR
            <br />
            <span className="text-5xl md:text-8xl bg-gradient-to-r from-pink-400 to-violet-400 bg-clip-text text-transparent">
              PAYMENT WAY! 💳
            </span>
          </h2>

          <p className="text-lg md:text-2xl text-gray-300 max-w-3xl mx-auto font-bold leading-relaxed">
            🚀 Multiple secure payment methods for your convenience
            <br />
            <span className="text-violet-400 animate-pulse" style={{ animationDuration: "3s" }}>
              ⚡ FAST • SECURE • TRUSTED ⚡
            </span>
          </p>
        </div>

        {/* Payment Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 max-w-7xl mx-auto mb-16">
          {paymentMethods.map((method, index) => (
            <Card
              key={method.name}
              className={`relative group cursor-pointer transform transition-all duration-700 hover:scale-105 ${
                activeCard === index ? "scale-102 shadow-xl" : ""
              } ${method.bgColor} backdrop-blur-sm border-2 ${method.borderColor} hover:border-opacity-100 overflow-hidden`}
              onMouseEnter={() => setActiveCard(index)}
            >
              <CardHeader className="relative z-10 text-center pb-4">
                <div className="flex justify-center mb-4">
                  <div className="relative">
                    <div className="w-20 h-20 rounded-2xl bg-white/10 backdrop-blur-sm flex items-center justify-center shadow-2xl border border-white/20 overflow-hidden">
                      <Image
                        src={method.icon || "/placeholder.svg"}
                        alt={method.name}
                        width={60}
                        height={40}
                        className="object-contain"
                      />
                    </div>
                    <div
                      className="absolute -top-2 -right-2 text-2xl animate-bounce"
                      style={{ animationDuration: "2s" }}
                    >
                      {method.emoji}
                    </div>
                  </div>
                </div>

                <CardTitle
                  className={`text-lg md:text-xl font-black ${method.textColor} mb-2 group-hover:text-white transition-colors`}
                >
                  {method.name}
                </CardTitle>

                {/* Features */}
                <div className="flex justify-center space-x-2 mb-4">
                  {method.features.map((feature, i) => (
                    <span
                      key={i}
                      className={`px-2 py-1 rounded-full text-xs font-bold ${method.bgColor} ${method.textColor} border ${method.borderColor}`}
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </CardHeader>

              <CardContent className="relative z-10 text-center">
                <p className="text-gray-300 group-hover:text-white font-semibold mb-4 transition-colors text-sm leading-relaxed">
                  {method.description}
                </p>

                {/* Progress Bar */}
                <div className="w-full bg-gray-700 rounded-full h-2 mb-4 overflow-hidden">
                  <div
                    className={`h-full bg-gradient-to-r ${method.color} transition-all duration-2000 ${
                      activeCard === index ? "w-full" : "w-0"
                    }`}
                  />
                </div>

                <Button
                  className={`w-full bg-gradient-to-r ${method.color} hover:shadow-xl text-white font-black py-2 text-sm rounded-xl transform hover:scale-105 transition-all duration-300`}
                >
                  <Zap className="mr-2 h-4 w-4" />
                  اختر 🔥
                </Button>
              </CardContent>

              {/* Corner Decorations */}
              <div className="absolute top-2 right-2">
                <Star className={`h-3 w-3 ${method.textColor} animate-pulse`} />
              </div>
              <div className="absolute bottom-2 left-2">
                <Crown className={`h-3 w-3 ${method.textColor} animate-pulse`} />
              </div>
            </Card>
          ))}
        </div>

        {/* How to Pay Section */}
        <div className="text-center">
          <Card className="max-w-4xl mx-auto bg-gradient-to-br from-violet-500/20 via-purple-500/20 to-pink-500/20 backdrop-blur-sm border-2 border-violet-500/30 relative overflow-hidden">
            <CardHeader className="relative z-10">
              <CardTitle className="text-3xl md:text-4xl font-black text-center mb-4">
                <span className="bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
                  🎮 HOW TO PAY 🎮
                </span>
              </CardTitle>
            </CardHeader>

            <CardContent className="relative z-10 text-center">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-full flex items-center justify-center mb-4 animate-pulse">
                    <span className="text-2xl font-black text-white">1</span>
                  </div>
                  <h3 className="text-lg md:text-xl font-bold text-green-400 mb-2 leading-tight">اضغط "أضف للعربة"</h3>
                  <p className="text-gray-300 text-sm md:text-base leading-relaxed">اختر الكروت اللي عايزها</p>
                </div>

                <div className="flex flex-col items-center">
                  <div
                    className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-full flex items-center justify-center mb-4 animate-pulse"
                    style={{ animationDelay: "0.5s" }}
                  >
                    <span className="text-2xl font-black text-white">2</span>
                  </div>
                  <h3 className="text-lg md:text-xl font-bold text-blue-400 mb-2 leading-tight">اختر طريقة الدفع</h3>
                  <p className="text-gray-300 text-sm md:text-base leading-relaxed">حدد الطريقة المناسبة ليك</p>
                </div>

                <div className="flex flex-col items-center">
                  <div
                    className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-700 rounded-full flex items-center justify-center mb-4 animate-pulse"
                    style={{ animationDelay: "1s" }}
                  >
                    <span className="text-2xl font-black text-white">3</span>
                  </div>
                  <h3 className="text-lg md:text-xl font-bold text-purple-400 mb-2 leading-tight">استلم فوراً</h3>
                  <p className="text-gray-300 text-sm md:text-base leading-relaxed">الكروت هتوصلك في ثواني</p>
                </div>
              </div>

              <div className="bg-gradient-to-r from-purple-500/20 to-violet-500/20 rounded-2xl p-6 border border-violet-500/30">
                <h3 className="text-2xl md:text-3xl font-black mb-4">
                  <span className="bg-gradient-to-r from-pink-400 to-violet-400 bg-clip-text text-transparent animate-pulse">
                    ⚡ MAXIMUM SECURITY ⚡
                  </span>
                </h3>
                <div className="text-gray-300 text-base md:text-lg font-semibold leading-relaxed space-y-2">
                  <p>🛡️ All transactions are processed manually for maximum security</p>
                  <p>🔒 Your money and data are 100% protected</p>
                  <p>⚡ Lightning fast delivery within minutes!</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
