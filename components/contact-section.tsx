"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MessageCircle, Clock, Facebook, Phone, Mail, Crown, Zap } from "lucide-react"

export function ContactSection() {
  const handleWhatsAppClick = () => {
    const message = "Hi! I need help with game cards"
    window.open(`https://wa.me/201011696196?text=${encodeURIComponent(message)}`, "_blank")
  }

  const handleFacebookClick = () => {
    window.open("https://www.facebook.com/diaaaeldeen/", "_blank")
  }

  return (
    <section
      className="py-20 bg-gradient-to-br from-slate-900 via-purple-900 to-violet-900 relative overflow-hidden"
      id="contact"
    >
      {/* Background Effects - نفس الخلفية البنفسجية */}
      <div className="absolute inset-0">
        <div
          className="absolute top-20 left-20 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "4s" }}
        />
        <div
          className="absolute bottom-20 right-20 w-32 h-32 bg-violet-500/10 rounded-full blur-2xl animate-bounce"
          style={{ animationDuration: "3s" }}
        />
        <div
          className="absolute top-1/2 left-1/4 w-24 h-24 bg-pink-500/10 rounded-full blur-xl animate-pulse"
          style={{ animationDuration: "5s" }}
        />
        <div
          className="absolute bottom-40 right-1/3 w-28 h-28 bg-purple-400/10 rounded-full blur-2xl animate-pulse"
          style={{ animationDuration: "6s" }}
        />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="flex items-center space-x-3 bg-gradient-to-r from-purple-500/20 to-violet-500/20 backdrop-blur-sm rounded-full px-8 py-4 border border-purple-500/30">
                <MessageCircle className="h-8 w-8 text-violet-400 animate-bounce" style={{ animationDuration: "2s" }} />
                <span className="text-2xl font-black bg-gradient-to-r from-purple-300 to-violet-300 bg-clip-text text-transparent">
                  📞 CONTACT US 📞
                </span>
                <MessageCircle
                  className="h-8 w-8 text-violet-400 animate-bounce"
                  style={{ animationDuration: "2s", animationDelay: "0.5s" }}
                />
              </div>
            </div>
          </div>

          <h2 className="text-5xl md:text-7xl font-black mb-6 bg-gradient-to-r from-purple-400 via-violet-400 to-pink-400 bg-clip-text text-transparent leading-tight">
            NEED HELP?
            <br />
            <span className="text-6xl md:text-8xl bg-gradient-to-r from-pink-400 to-violet-400 bg-clip-text text-transparent">
              WE'RE HERE! 🚀
            </span>
          </h2>

          <div className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto font-bold leading-relaxed">
            <p className="text-violet-100">🎮 Need help or have questions? We're here to assist you 24/7</p>
            <p className="text-lg text-pink-300 mt-2 animate-pulse" style={{ animationDuration: "3s" }}>
              ⚡ تحتاج مساعدة أو لديك أسئلة؟ نحن هنا لمساعدتك ⚡
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto mb-16">
          {/* Contact Card */}
          <Card className="bg-gradient-to-br from-purple-500/20 to-violet-500/20 backdrop-blur-sm border-2 border-purple-500/30 hover:border-purple-400/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="flex items-center text-2xl font-black text-white">
                <MessageCircle className="h-8 w-8 text-green-400 mr-3 animate-pulse" />🎯 Get in Touch
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-6">
              <div className="flex items-center space-x-4 bg-white/5 rounded-xl p-4 border border-green-500/30">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500/30 to-emerald-500/30 rounded-xl flex items-center justify-center">
                  <MessageCircle className="h-8 w-8 text-green-400" />
                </div>
                <div>
                  <p className="font-black text-green-300 text-lg">📱 WhatsApp</p>
                  <p className="text-white font-bold text-xl">01011696196</p>
                  <p className="text-gray-300 text-sm">فوري • سريع • متاح 24/7</p>
                </div>
              </div>

              <div className="flex items-center space-x-4 bg-white/5 rounded-xl p-4 border border-blue-500/30">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500/30 to-cyan-500/30 rounded-xl flex items-center justify-center">
                  <Facebook className="h-8 w-8 text-blue-400" />
                </div>
                <div>
                  <p className="font-black text-blue-300 text-lg">📘 Facebook</p>
                  <p className="text-white font-bold text-xl">Diaa ElDeen Sadek</p>
                  <p className="text-gray-300 text-sm">تابعنا للعروض الحصرية</p>
                </div>
              </div>

              <div className="flex items-center space-x-4 bg-white/5 rounded-xl p-4 border border-purple-500/30">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500/30 to-violet-500/30 rounded-xl flex items-center justify-center">
                  <Clock className="h-8 w-8 text-purple-400" />
                </div>
                <div>
                  <p className="font-black text-purple-300 text-lg">⏰ Support Hours</p>
                  <p className="text-white font-bold text-xl">Available 24/7</p>
                  <p className="text-gray-300 text-sm">دعم مستمر طوال الأسبوع</p>
                </div>
              </div>

              <div className="space-y-3 pt-4">
                <Button
                  onClick={handleWhatsAppClick}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-black py-4 text-lg rounded-xl shadow-2xl hover:shadow-green-500/50 transition-all duration-300 transform hover:scale-105"
                >
                  <MessageCircle className="mr-3 h-6 w-6" />💬 Chat on WhatsApp
                </Button>

                <Button
                  onClick={handleFacebookClick}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-black py-4 text-lg rounded-xl shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 transform hover:scale-105"
                >
                  <Facebook className="mr-3 h-6 w-6" />📘 Facebook Page
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Why Choose Us Card */}
          <Card className="bg-gradient-to-br from-violet-500/20 to-pink-500/20 backdrop-blur-sm border-2 border-violet-500/30 hover:border-pink-400/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="flex items-center text-2xl font-black text-white">
                <Crown className="h-8 w-8 text-yellow-400 mr-3 animate-pulse" />👑 Why Choose Us?
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-6">
              <div className="flex items-start space-x-4 bg-white/5 rounded-xl p-4 border border-green-500/30">
                <div className="w-4 h-4 bg-green-500 rounded-full mt-2 animate-pulse" />
                <div>
                  <p className="font-black text-green-300 text-lg">⚡ Instant Delivery</p>
                  <p className="text-gray-300 font-semibold">توصيل فوري خلال دقائق معدودة</p>
                </div>
              </div>

              <div className="flex items-start space-x-4 bg-white/5 rounded-xl p-4 border border-blue-500/30">
                <div className="w-4 h-4 bg-blue-500 rounded-full mt-2 animate-pulse" />
                <div>
                  <p className="font-black text-blue-300 text-lg">💰 Best Prices</p>
                  <p className="text-gray-300 font-semibold">أفضل الأسعار مع عروض مذهلة</p>
                </div>
              </div>

              <div className="flex items-start space-x-4 bg-white/5 rounded-xl p-4 border border-purple-500/30">
                <div className="w-4 h-4 bg-purple-500 rounded-full mt-2 animate-pulse" />
                <div>
                  <p className="font-black text-purple-300 text-lg">🛡️ Secure Transactions</p>
                  <p className="text-gray-300 font-semibold">معاملات آمنة ومضمونة 100%</p>
                </div>
              </div>

              <div className="flex items-start space-x-4 bg-white/5 rounded-xl p-4 border border-yellow-500/30">
                <div className="w-4 h-4 bg-yellow-500 rounded-full mt-2 animate-pulse" />
                <div>
                  <p className="font-black text-yellow-300 text-lg">🎯 24/7 Support</p>
                  <p className="text-gray-300 font-semibold">دعم العملاء على مدار الساعة</p>
                </div>
              </div>

              <div className="flex items-start space-x-4 bg-white/5 rounded-xl p-4 border border-pink-500/30">
                <div className="w-4 h-4 bg-pink-500 rounded-full mt-2 animate-pulse" />
                <div>
                  <p className="font-black text-pink-300 text-lg">🎮 Gaming Expert</p>
                  <p className="text-gray-300 font-semibold">خبراء في عالم الألعاب</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Final CTA */}
        <div className="text-center">
          <Card className="max-w-5xl mx-auto bg-gradient-to-br from-purple-500/20 via-violet-500/20 to-pink-500/20 backdrop-blur-sm border-2 border-violet-500/30 relative overflow-hidden">
            <CardContent className="py-12 relative z-10">
              <div className="flex justify-center mb-6">
                <div className="flex items-center space-x-3 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 backdrop-blur-sm rounded-full px-8 py-4 border border-yellow-500/30">
                  <Crown className="h-8 w-8 text-yellow-400 animate-bounce" />
                  <span className="text-2xl font-black text-yellow-300">🚀 READY TO START? 🚀</span>
                  <Crown className="h-8 w-8 text-yellow-400 animate-bounce" />
                </div>
              </div>

              <h3 className="text-4xl md:text-5xl font-black mb-6 text-white leading-tight">
                Ready to Top-Up?
                <br />
                <span className="text-5xl md:text-6xl bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                  JOIN THOUSANDS! 🎮
                </span>
              </h3>

              <div className="text-xl mb-8 text-gray-300 leading-relaxed max-w-3xl mx-auto">
                <p className="font-bold">
                  Join thousands of satisfied gamers who trust{" "}
                  <span className="text-violet-400 font-black">Diaa ElDeen Sadek</span>
                </p>
                <p className="text-lg text-pink-300 mt-2 font-bold animate-pulse">
                  انضم لآلاف اللاعبين الذين يثقون في ضياء الدين صادق
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-6 justify-center mb-8">
                <Button
                  onClick={handleWhatsAppClick}
                  className="bg-gradient-to-r from-green-600 via-emerald-600 to-green-600 hover:from-green-700 hover:via-emerald-700 hover:to-green-700 text-white font-black px-12 py-4 text-xl rounded-2xl shadow-2xl hover:shadow-green-500/50 transform hover:scale-105 transition-all duration-300"
                >
                  <Zap className="mr-3 h-6 w-6" />🛒 Start Shopping Now
                </Button>

                <Button
                  onClick={handleFacebookClick}
                  className="bg-gradient-to-r from-blue-600 via-cyan-600 to-blue-600 hover:from-blue-700 hover:via-cyan-700 hover:to-blue-700 text-white font-black px-12 py-4 text-xl rounded-2xl shadow-2xl hover:shadow-blue-500/50 transform hover:scale-105 transition-all duration-300"
                >
                  <Crown className="mr-3 h-6 w-6" />👑 Follow on Facebook
                </Button>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
                <div className="flex items-center justify-center space-x-3 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-2xl p-4 border border-green-500/30">
                  <Phone className="h-6 w-6 text-green-400" />
                  <span className="text-white text-lg font-black">📱 01011696196</span>
                </div>
                <div className="flex items-center justify-center space-x-3 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-2xl p-4 border border-blue-500/30">
                  <Mail className="h-6 w-6 text-blue-400" />
                  <span className="text-white text-lg font-black">💬 Available via WhatsApp</span>
                </div>
              </div>
            </CardContent>

            {/* Corner Effects */}
            <div className="absolute top-4 right-4">
              <Crown className="h-6 w-6 text-yellow-400 animate-pulse" />
            </div>
            <div className="absolute bottom-4 left-4">
              <Zap className="h-6 w-6 text-green-400 animate-pulse" />
            </div>
          </Card>
        </div>
      </div>
    </section>
  )
}
