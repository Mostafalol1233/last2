"use client"

import { useState } from "react"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ShoppingCart, Plus, Minus, Trash2, CreditCard } from "lucide-react"
import { useCart } from "./cart-provider"
import { CheckoutModal } from "./checkout-modal"

export function CartSidebar() {
  const { state, dispatch } = useCart()
  const [isOpen, setIsOpen] = useState(false)
  const [showCheckout, setShowCheckout] = useState(false)

  const updateQuantity = (id: string, quantity: number) => {
    dispatch({ type: "UPDATE_QUANTITY", payload: { id, quantity } })
  }

  const removeItem = (id: string) => {
    dispatch({ type: "REMOVE_ITEM", payload: id })
  }

  return (
    <>
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            className="relative bg-white/10 border-white/20 hover:bg-white/20 text-white"
          >
            <ShoppingCart className="h-4 w-4" />
            {state.items.length > 0 && (
              <Badge className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs bg-red-500 text-white border-0">
                {state.items.reduce((sum, item) => sum + item.quantity, 0)}
              </Badge>
            )}
          </Button>
        </SheetTrigger>

        <SheetContent className="w-[400px] sm:w-[540px] bg-slate-900 border-purple-500/30 text-white">
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2 text-white">
              <ShoppingCart className="h-5 w-5 text-purple-400" />🛒 Shopping Cart ({state.items.length})
            </SheetTitle>
          </SheetHeader>

          <div className="mt-6 space-y-4">
            {state.items.length === 0 ? (
              <div className="text-center py-8">
                <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-400 text-lg font-semibold">Your cart is empty</p>
                <p className="text-gray-500">Add some game cards to get started!</p>
              </div>
            ) : (
              <>
                <div className="space-y-4 max-h-[400px] overflow-y-auto">
                  {state.items.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center space-x-4 p-4 border border-purple-500/30 rounded-lg bg-white/5 backdrop-blur-sm"
                    >
                      <div className="flex-1">
                        <h4 className="font-bold text-white text-lg">{item.packageName}</h4>
                        <p className="text-purple-300 font-semibold">{item.gameName}</p>
                        <p className="text-gray-300 font-medium">🎯 {item.points.toLocaleString()} Points</p>
                        {item.bonusDescription && (
                          <p className="text-yellow-400 text-sm font-bold">🎁 {item.bonusDescription}</p>
                        )}
                        <p className="font-black text-green-400 text-lg">{item.price} EGP each</p>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                        >
                          <Minus className="h-3 w-3" />
                        </Button>
                        <span className="w-8 text-center font-bold text-white">{item.quantity}</span>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                        >
                          <Plus className="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => removeItem(item.id)}
                          className="bg-red-600 hover:bg-red-700 text-white"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="border-t border-purple-500/30 pt-4">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xl font-black text-white">💰 Total:</span>
                    <span className="text-3xl font-black text-green-400">{state.total.toFixed(2)} EGP</span>
                  </div>

                  <Button
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-black py-4 text-lg"
                    onClick={() => setShowCheckout(true)}
                  >
                    <CreditCard className="mr-2 h-5 w-5" />🚀 Proceed to Checkout
                  </Button>
                </div>
              </>
            )}
          </div>
        </SheetContent>
      </Sheet>

      <CheckoutModal
        isOpen={showCheckout}
        onClose={() => setShowCheckout(false)}
        onComplete={() => {
          setShowCheckout(false)
          setIsOpen(false)
        }}
      />
    </>
  )
}
