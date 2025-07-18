"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { CreditCard, User, Phone, MessageCircle } from "lucide-react"
import Image from "next/image"

interface Game {
  id: string
  name: string
  slug: string
}

interface CardPackage {
  id: string
  name: string
  points: number
  price_egp: number
  bonus_description: string
}

interface SimpleCheckoutProps {
  isOpen: boolean
  onClose: () => void
  game: Game
  cardPackage: CardPackage
}

export function SimpleCheckout({ isOpen, onClose, game, cardPackage }: SimpleCheckoutProps) {
  const [step, setStep] = useState(1)
  const [customerInfo, setCustomerInfo] = useState({
    name: "",
    phone: "",
  })
  const [paymentMethod, setPaymentMethod] = useState("")

  const paymentMethods = [
    { id: "vodafone", name: "Vodafone Cash", icon: "/images/payments/vodafone.png", emoji: "📱" },
    { id: "orange", name: "Orange Money", icon: "/images/payments/orange-money.png", emoji: "🧡" },
    { id: "we", name: "WE Pay", icon: "/images/payments/we-pay.png", emoji: "💜" },
    { id: "instapay", name: "InstaPay", icon: "/images/payments/instapay.png", emoji: "⚡" },
    { id: "cib", name: "CIB Bank", icon: "/images/payments/cib-bank.png", emoji: "🏦" },
    { id: "visa", name: "Visa", icon: "/images/payments/visa.png", emoji: "💳" },
    { id: "mastercard", name: "Mastercard", icon: "/images/payments/mastercard.png", emoji: "💳" },
  ]

  const handleCheckout = () => {
    const selectedPayment = paymentMethods.find((method) => method.id === paymentMethod)

    const message =
      `🔥 طلب جديد من الموقع 🔥\n\n` +
      `👤 بيانات العميل:\n` +
      `الاسم: ${customerInfo.name}\n` +
      `الهاتف: ${customerInfo.phone}\n\n` +
      `🎮 تفاصيل الطلب:\n` +
      `اللعبة: ${game.name}\n` +
      `الكارت: ${cardPackage.name}\n` +
      `النقاط: ${cardPackage.points.toLocaleString()}\n` +
      `السعر: ${cardPackage.price_egp} جنيه\n` +
      `${cardPackage.bonus_description ? `🎁 المكافأة: ${cardPackage.bonus_description}\n` : ""}` +
      `\n💳 طريقة الدفع: ${selectedPayment?.emoji} ${selectedPayment?.name}\n\n` +
      `⚡ جاهز للتوصيل الفوري!`

    const whatsappUrl = `https://wa.me/201011696196?text=${encodeURIComponent(message)}`
    window.open(whatsappUrl, "_blank")
    onClose()
  }

  const resetModal = () => {
    setStep(1)
    setCustomerInfo({ name: "", phone: "" })
    setPaymentMethod("")
  }

  const handleClose = () => {
    resetModal()
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg bg-slate-900 border-purple-500/30 text-white">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-white text-xl font-black">
            <CreditCard className="h-5 w-5 text-purple-400" />🛒 إتمام الشراء - خطوة {step} من 3
          </DialogTitle>
        </DialogHeader>

        {step === 1 && (
          <div className="space-y-4">
            <h3 className="text-lg font-black text-purple-300">📋 تفاصيل الطلب</h3>

            <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-4 rounded-lg border border-purple-500/30">
              <div className="text-center mb-4">
                <div className="text-4xl mb-2">💎</div>
                <h4 className="text-xl font-black text-white">{cardPackage.name}</h4>
                <p className="text-purple-300 font-semibold">{game.name}</p>
                <p className="text-gray-300">🎯 {cardPackage.points.toLocaleString()} نقطة</p>
              </div>

              {cardPackage.bonus_description && (
                <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-lg p-3 border border-yellow-500/30 mb-3">
                  <p className="text-sm text-yellow-300 font-bold text-center">🎁 {cardPackage.bonus_description}</p>
                </div>
              )}

              <div className="text-center">
                <div className="text-3xl font-black text-green-400">💰 {cardPackage.price_egp} جنيه</div>
              </div>
            </div>

            <Button
              onClick={() => setStep(2)}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-black py-3"
            >
              متابعة للبيانات الشخصية 👤
            </Button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <h3 className="text-lg font-black text-purple-300">👤 البيانات الشخصية</h3>

            <div className="space-y-4">
              <div>
                <Label htmlFor="name" className="text-white font-bold flex items-center">
                  <User className="h-4 w-4 mr-2" />
                  الاسم الكامل *
                </Label>
                <Input
                  id="name"
                  value={customerInfo.name}
                  onChange={(e) => setCustomerInfo({ ...customerInfo, name: e.target.value })}
                  required
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  placeholder="أدخل اسمك الكامل"
                />
              </div>

              <div>
                <Label htmlFor="phone" className="text-white font-bold flex items-center">
                  <Phone className="h-4 w-4 mr-2" />
                  رقم الهاتف *
                </Label>
                <Input
                  id="phone"
                  value={customerInfo.phone}
                  onChange={(e) => setCustomerInfo({ ...customerInfo, phone: e.target.value })}
                  required
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  placeholder="01xxxxxxxxx"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setStep(1)}
                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
              >
                ← رجوع
              </Button>
              <Button
                onClick={() => setStep(3)}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-black"
                disabled={!customerInfo.name || !customerInfo.phone}
              >
                متابعة لطريقة الدفع 💳
              </Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <h3 className="text-lg font-black text-purple-300">💳 اختر طريقة الدفع</h3>

            <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod}>
              <div className="grid grid-cols-1 gap-3 max-h-60 overflow-y-auto">
                {paymentMethods.map((method) => (
                  <div
                    key={method.id}
                    className="flex items-center space-x-2 border border-purple-500/30 rounded-lg p-3 hover:bg-white/5 bg-white/5"
                  >
                    <RadioGroupItem value={method.id} id={method.id} className="text-purple-400" />
                    <Label
                      htmlFor={method.id}
                      className="flex items-center space-x-3 cursor-pointer flex-1 text-white font-semibold"
                    >
                      <Image
                        src={method.icon || "/placeholder.svg"}
                        alt={method.name}
                        width={24}
                        height={24}
                        className="object-contain"
                      />
                      <span>
                        {method.emoji} {method.name}
                      </span>
                    </Label>
                  </div>
                ))}
              </div>
            </RadioGroup>

            <div className="bg-blue-500/20 p-4 rounded-lg border border-blue-500/30">
              <h4 className="font-black text-blue-300 mb-2">📋 ملخص الطلب</h4>
              <p className="text-blue-200 font-bold">
                المبلغ: <span className="font-black text-green-400">{cardPackage.price_egp} جنيه</span>
              </p>
              <p className="text-blue-200 font-bold">
                الدفع:{" "}
                <span className="text-white">
                  {paymentMethods.find((m) => m.id === paymentMethod)?.name || "لم يتم الاختيار"}
                </span>
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setStep(2)}
                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
              >
                ← رجوع
              </Button>
              <Button
                onClick={handleCheckout}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-black py-3"
                disabled={!paymentMethod}
              >
                <MessageCircle className="w-4 h-4 mr-2" />🚀 إرسال الطلب عبر واتساب
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
