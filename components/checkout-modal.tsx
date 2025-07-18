"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"
import { useCart } from "./cart-provider"
import { CreditCard } from "lucide-react"
import Image from "next/image"

interface CheckoutModalProps {
  isOpen: boolean
  onClose: () => void
  onComplete: () => void
}

export function CheckoutModal({ isOpen, onClose, onComplete }: CheckoutModalProps) {
  const { state, dispatch } = useCart()
  const [step, setStep] = useState(1)
  const [customerInfo, setCustomerInfo] = useState({
    name: "",
    phone: "",
    email: "",
    notes: "",
  })
  const [paymentMethod, setPaymentMethod] = useState("")

  const paymentMethods = [
    { id: "vodafone", name: "Vodafone Cash", icon: "/images/payments/vodafone.png", emoji: "📱" },
    { id: "orange", name: "Orange Money", icon: "/images/payments/orange-money.png", emoji: "🧡" },
    { id: "we", name: "WE Pay", icon: "/images/payments/we-pay.png", emoji: "💜" },
    { id: "instapay", name: "InstaPay", icon: "/images/payments/instapay.png", emoji: "⚡" },
    { id: "cib", name: "CIB Bank Transfer", icon: "/images/payments/cib-bank.png", emoji: "🏦" },
    { id: "visa", name: "Visa Card", icon: "/images/payments/visa.png", emoji: "💳" },
    { id: "mastercard", name: "Mastercard", icon: "/images/payments/mastercard.png", emoji: "💳" },
  ]

  const handleCheckout = () => {
    const orderSummary = state.items
      .map(
        (item) =>
          `🎮 ${item.packageName} - ${item.gameName}\n` +
          `🎯 ${item.points.toLocaleString()} Points\n` +
          `💰 ${item.price} EGP x ${item.quantity} = ${(item.price * item.quantity).toFixed(2)} EGP\n` +
          `${item.bonusDescription ? `🎁 ${item.bonusDescription}\n` : ""}`,
      )
      .join("\n")

    const selectedPayment = paymentMethods.find((method) => method.id === paymentMethod)

    const message =
      `🔥 NEW ORDER FROM WEBSITE 🔥\n\n` +
      `👤 Customer Information:\n` +
      `Name: ${customerInfo.name}\n` +
      `Phone: ${customerInfo.phone}\n` +
      `Email: ${customerInfo.email}\n\n` +
      `🛒 ORDER DETAILS:\n` +
      `${orderSummary}\n` +
      `💰 TOTAL: ${state.total.toFixed(2)} EGP\n\n` +
      `💳 Payment Method: ${selectedPayment?.emoji} ${selectedPayment?.name}\n\n` +
      `${customerInfo.notes ? `📝 Notes: ${customerInfo.notes}\n\n` : ""}` +
      `⚡ Ready for instant delivery!`

    const whatsappUrl = `https://wa.me/201011696196?text=${encodeURIComponent(message)}`
    window.open(whatsappUrl, "_blank")

    dispatch({ type: "CLEAR_CART" })
    onComplete()
  }

  const resetModal = () => {
    setStep(1)
    setCustomerInfo({ name: "", phone: "", email: "", notes: "" })
    setPaymentMethod("")
  }

  const handleClose = () => {
    resetModal()
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-900 border-purple-500/30 text-white">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-white text-2xl font-black">
            <CreditCard className="h-6 w-6 text-purple-400" />🚀 Checkout - Step {step} of 3
          </DialogTitle>
        </DialogHeader>

        {step === 1 && (
          <div className="space-y-4">
            <h3 className="text-xl font-black text-purple-300">📋 Order Summary</h3>
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {state.items.map((item) => (
                <div
                  key={item.id}
                  className="flex justify-between items-center p-4 border border-purple-500/30 rounded-lg bg-white/5"
                >
                  <div>
                    <p className="font-black text-white text-lg">{item.packageName}</p>
                    <p className="text-purple-300 font-semibold">
                      {item.gameName} - 🎯 {item.points.toLocaleString()} Points
                    </p>
                    {item.bonusDescription && (
                      <p className="text-yellow-400 text-sm font-bold">🎁 {item.bonusDescription}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-white">
                      {item.price} EGP x {item.quantity}
                    </p>
                    <p className="text-green-400 font-black text-lg">{(item.price * item.quantity).toFixed(2)} EGP</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="border-t border-purple-500/30 pt-3">
              <div className="flex justify-between items-center text-2xl font-black">
                <span className="text-white">💰 Total:</span>
                <span className="text-green-400">{state.total.toFixed(2)} EGP</span>
              </div>
            </div>
            <Button
              onClick={() => setStep(2)}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-black py-4 text-lg"
            >
              Continue to Customer Information 👤
            </Button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <h3 className="text-xl font-black text-purple-300">👤 Customer Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name" className="text-white font-bold">
                  Full Name *
                </Label>
                <Input
                  id="name"
                  value={customerInfo.name}
                  onChange={(e) => setCustomerInfo({ ...customerInfo, name: e.target.value })}
                  required
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  placeholder="Enter your full name"
                />
              </div>
              <div>
                <Label htmlFor="phone" className="text-white font-bold">
                  Phone Number *
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
            <div>
              <Label htmlFor="email" className="text-white font-bold">
                Email (Optional)
              </Label>
              <Input
                id="email"
                type="email"
                value={customerInfo.email}
                onChange={(e) => setCustomerInfo({ ...customerInfo, email: e.target.value })}
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                placeholder="your.email@example.com"
              />
            </div>
            <div>
              <Label htmlFor="notes" className="text-white font-bold">
                Additional Notes (Optional)
              </Label>
              <Textarea
                id="notes"
                value={customerInfo.notes}
                onChange={(e) => setCustomerInfo({ ...customerInfo, notes: e.target.value })}
                placeholder="Any special instructions or notes..."
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setStep(1)}
                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
              >
                ← Back
              </Button>
              <Button
                onClick={() => setStep(3)}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-black"
                disabled={!customerInfo.name || !customerInfo.phone}
              >
                Continue to Payment 💳
              </Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <h3 className="text-xl font-black text-purple-300">💳 Select Payment Method</h3>
            <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
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
                        width={32}
                        height={32}
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
              <h4 className="font-black text-blue-300 mb-2 text-lg">📋 Order Summary</h4>
              <p className="text-blue-200 font-bold">
                Total: <span className="font-black text-green-400">{state.total.toFixed(2)} EGP</span>
              </p>
              <p className="text-blue-200 font-bold">
                Payment:{" "}
                <span className="text-white">
                  {paymentMethods.find((m) => m.id === paymentMethod)?.name || "Not selected"}
                </span>
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setStep(2)}
                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
              >
                ← Back
              </Button>
              <Button
                onClick={handleCheckout}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-black py-4 text-lg"
                disabled={!paymentMethod}
              >
                🚀 Complete Order via WhatsApp
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
