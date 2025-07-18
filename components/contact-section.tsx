"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MessageCircle, Clock, Shield, Facebook, Phone, Mail } from "lucide-react"

export function ContactSection() {
  const handleWhatsAppClick = () => {
    const message = "Hi! I need help with game cards"
    window.open(`https://wa.me/201011696196?text=${encodeURIComponent(message)}`, "_blank")
  }

  const handleFacebookClick = () => {
    window.open("https://www.facebook.com/diaaaeldeen/", "_blank")
  }

  return (
    <section className="py-16 bg-gradient-to-br from-slate-900 to-gray-900 relative overflow-hidden" id="contact">
      <div className="container mx-auto px-4 relative z-10">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center space-x-2 bg-blue-500/10 backdrop-blur-sm rounded-full px-6 py-3 mb-6">
            <MessageCircle className="h-6 w-6 text-blue-400" />
            <span className="text-blue-300 font-medium">Contact Us</span>
          </div>

          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">Need Help?</h2>

          <div className="text-lg text-gray-300 max-w-2xl mx-auto leading-relaxed">
            <p>Need help or have questions? We're here to assist you 24/7</p>
            <p className="text-base text-gray-400 mt-2">تحتاج مساعدة أو لديك أسئلة؟ نحن هنا لمساعدتك</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Contact Card */}
          <Card className="bg-white/5 backdrop-blur-sm border border-white/10">
            <CardHeader>
              <CardTitle className="flex items-center text-xl font-bold text-white">
                <MessageCircle className="h-6 w-6 text-green-400 mr-3" />
                Get in Touch
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <MessageCircle className="h-6 w-6 text-green-400" />
                </div>
                <div>
                  <p className="font-semibold text-green-300">WhatsApp</p>
                  <p className="text-gray-300">01011696196</p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <Facebook className="h-6 w-6 text-blue-400" />
                </div>
                <div>
                  <p className="font-semibold text-blue-300">Facebook</p>
                  <p className="text-gray-300">Diaa ElDeen Sadek</p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <Clock className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <p className="font-semibold text-purple-300">Support Hours</p>
                  <p className="text-gray-300">Available 24/7</p>
                </div>
              </div>

              <div className="space-y-3 pt-4">
                <Button
                  onClick={handleWhatsAppClick}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3"
                >
                  <MessageCircle className="mr-2 h-5 w-5" />
                  Chat on WhatsApp
                </Button>

                <Button
                  onClick={handleFacebookClick}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3"
                >
                  <Facebook className="mr-2 h-5 w-5" />
                  Facebook Page
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Why Choose Us Card */}
          <Card className="bg-white/5 backdrop-blur-sm border border-white/10">
            <CardHeader>
              <CardTitle className="flex items-center text-xl font-bold text-white">
                <Shield className="h-6 w-6 text-blue-400 mr-3" />
                Why Choose Us?
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-3" />
                <div>
                  <p className="font-semibold text-green-300">Instant Delivery</p>
                  <p className="text-gray-400 text-sm">توصيل فوري خلال دقائق</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-3" />
                <div>
                  <p className="font-semibold text-blue-300">Best Prices</p>
                  <p className="text-gray-400 text-sm">أفضل الأسعار مع عروض مذهلة</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-3" />
                <div>
                  <p className="font-semibold text-purple-300">Secure Transactions</p>
                  <p className="text-gray-400 text-sm">معاملات آمنة ومضمونة</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mt-3" />
                <div>
                  <p className="font-semibold text-yellow-300">24/7 Support</p>
                  <p className="text-gray-400 text-sm">دعم العملاء على مدار الساعة</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Final CTA */}
        <div className="mt-12 text-center">
          <Card className="max-w-3xl mx-auto bg-white/5 backdrop-blur-sm border border-white/10">
            <CardContent className="py-8">
              <h3 className="text-2xl md:text-3xl font-bold mb-4 text-white">Ready to Top-Up?</h3>

              <div className="text-lg mb-6 text-gray-300 leading-relaxed">
                <p>
                  Join thousands of satisfied gamers who trust <span className="text-blue-400">Diaa ElDeen Sadek</span>
                </p>
                <p className="text-base text-gray-400 mt-1">انضم لآلاف اللاعبين الذين يثقون في ضياء الدين صادق</p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
                <Button
                  onClick={handleWhatsAppClick}
                  className="bg-green-600 hover:bg-green-700 text-white font-semibold px-8 py-3"
                >
                  Start Shopping Now
                </Button>

                <Button
                  onClick={handleFacebookClick}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3"
                >
                  Follow on Facebook
                </Button>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg mx-auto">
                <div className="flex items-center justify-center space-x-2 bg-white/5 rounded-lg p-3">
                  <Phone className="h-4 w-4 text-green-400" />
                  <span className="text-white text-sm">01011696196</span>
                </div>
                <div className="flex items-center justify-center space-x-2 bg-white/5 rounded-lg p-3">
                  <Mail className="h-4 w-4 text-blue-400" />
                  <span className="text-white text-sm">Available via WhatsApp</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
