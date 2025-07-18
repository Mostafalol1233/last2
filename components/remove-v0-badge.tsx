"use client"

import { useEffect } from "react"

export function RemoveV0Badge() {
  useEffect(() => {
    // 🛠️ 1. منع التحميل المبدئي لشعار v0.dev (قبل ما يدخل DOM)
    if (typeof document !== "undefined") {
      const blockV0Script = () => {
        try {
          const originalInsertBefore = Element.prototype.insertBefore
          const originalAppendChild = Element.prototype.appendChild

          Element.prototype.insertBefore = function (newNode, referenceNode) {
            try {
              if (
                newNode?.tagName === "SCRIPT" &&
                newNode?.src &&
                (newNode.src.includes("v0.dev") || newNode.src.includes("vercel"))
              ) {
                console.log("🚫 Blocked v0 script:", newNode.src)
                return newNode // تجاهل الإدراج
              }

              // فحص العناصر الأخرى
              if (newNode?.id && (newNode.id.includes("v0-built-with-button") || newNode.id.includes("8038256c"))) {
                console.log("🚫 Blocked v0 element:", newNode.id)
                return newNode
              }
            } catch (e) {
              // تجاهل الأخطاء
            }

            return originalInsertBefore.call(this, newNode, referenceNode)
          }

          Element.prototype.appendChild = function (newNode) {
            try {
              if (
                newNode?.tagName === "SCRIPT" &&
                newNode?.src &&
                (newNode.src.includes("v0.dev") || newNode.src.includes("vercel"))
              ) {
                console.log("🚫 Blocked v0 script via appendChild:", newNode.src)
                return newNode
              }

              if (newNode?.id && (newNode.id.includes("v0-built-with-button") || newNode.id.includes("8038256c"))) {
                console.log("🚫 Blocked v0 element via appendChild:", newNode.id)
                return newNode
              }
            } catch (e) {
              // تجاهل الأخطاء
            }

            return originalAppendChild.call(this, newNode)
          }
        } catch (error) {
          console.log("Error setting up v0 blocking:", error)
        }
      }

      blockV0Script()
    }

    const removeV0Elements = () => {
      try {
        if (typeof document === "undefined") return

        // 🧹 3. مسح السكربت الرئيسي لـ v0.dev
        document.querySelectorAll('script[src*="v0.dev"]').forEach((el) => {
          try {
            console.log("🗑️ Removing v0.dev script:", el.src)
            el.remove()
          } catch {}
        })

        document.querySelectorAll('script[src*="vercel"]').forEach((el) => {
          try {
            if (el.src.includes("v0") || el.textContent?.includes("v0")) {
              console.log("🗑️ Removing vercel script:", el.src)
              el.remove()
            }
          } catch {}
        })

        // قائمة شاملة بجميع الـ selectors للعناصر المراد إزالتها
        const selectors = [
          // العناصر العامة
          "[data-v0]",
          '[class*="v0"]',
          '[id*="v0"]',
          'div[style*="v0"]',
          'a[href*="v0.dev"]',

          // العناصر المحددة من الصورة
          "#v0-built-with-button-8038256c-a203-44b8-b45a-6e74a2af3357",
          '[id^="v0-built-with-button"]',
          '[id*="built-with-button"]',
          '[id*="8038256c-a203-44b8-b45a-6e74a2af3357"]',
          '[id*="8038256c"]',
          '[id*="a203-44b8"]',
          '[id*="b45a-6e74a2af3357"]',

          // عناصر إضافية
          '[class^="v0-"]',
          '[data-testid*="v0"]',
          'button[onclick*="v0-built-with-button"]',
          'div[onclick*="v0-built-with-button"]',
        ]

        // إزالة العناصر باستخدام selectors
        selectors.forEach((selector) => {
          try {
            const elements = document.querySelectorAll(selector)
            elements.forEach((element) => {
              try {
                // 🛡️ prevent removing <html>, <body>, <head>
                const isRoot =
                  element === document.documentElement ||
                  element === document.body ||
                  element.tagName === "HTML" ||
                  element.tagName === "BODY" ||
                  element.tagName === "HEAD"

                if (!isRoot) {
                  element.style.display = "none"
                  element.style.visibility = "hidden"
                  element.style.opacity = "0"
                  element.style.height = "0"
                  element.style.width = "0"
                  element.style.overflow = "hidden"
                  element.style.position = "absolute"
                  element.style.left = "-9999px"
                  element.style.top = "-9999px"
                  element.style.zIndex = "-9999"
                  element.style.pointerEvents = "none"

                  element.remove()
                  console.log("🗑️ Removed v0 element:", selector)
                }
              } catch (e) {
                // تجاهل أخطاء العناصر الفردية
              }
            })
          } catch (error) {
            // تجاهل أخطاء الـ selector
          }
        })

        // البحث في النصوص والمحتوى
        try {
          const allElements = document.querySelectorAll("*")
          allElements.forEach((element) => {
            try {
              const text = element.textContent || element.innerText || ""
              const html = element.innerHTML || ""
              const id = element.id || ""
              const className = element.className || ""

              // فحص النصوص والمحتوى
              if (
                text.includes("Built with v0") ||
                text.includes("v0.dev") ||
                text.includes("Powered by v0") ||
                html.includes("v0-built-with-button") ||
                html.includes("8038256c-a203-44b8-b45a-6e74a2af3357") ||
                id.includes("v0-built-with-button") ||
                className.includes("v0-")
              ) {
                // 🛡️ guard again
                const isRoot =
                  element === document.documentElement ||
                  element === document.body ||
                  element.tagName === "HTML" ||
                  element.tagName === "BODY" ||
                  element.tagName === "HEAD"

                if (!isRoot) {
                  element.style.display = "none"
                  element.style.visibility = "hidden"
                  element.style.opacity = "0"
                  element.remove()
                  console.log("🗑️ Removed v0 text element")
                }
              }
            } catch (e) {
              // تجاهل
            }
          })
        } catch (error) {
          // تجاهل
        }

        // إزالة iframes المتعلقة بـ v0
        try {
          const iframes = document.querySelectorAll("iframe")
          iframes.forEach((iframe) => {
            try {
              const src = iframe.src || ""
              if (src.includes("v0") || src.includes("vercel")) {
                iframe.style.display = "none"
                iframe.remove()
                console.log("🗑️ Removed v0 iframe:", src)
              }
            } catch (e) {
              // تجاهل
            }
          })
        } catch (error) {
          // تجاهل
        }

        // البحث عن أي عناصر تحتوي على onclick handlers متعلقة بـ v0
        try {
          const clickableElements = document.querySelectorAll("[onclick]")
          clickableElements.forEach((element) => {
            try {
              const onclick = element.getAttribute("onclick") || ""
              if (onclick.includes("v0-built-with-button") || onclick.includes("8038256c")) {
                element.style.display = "none"
                element.remove()
                console.log("🗑️ Removed v0 clickable element")
              }
            } catch (e) {
              // تجاهل
            }
          })
        } catch (error) {
          // تجاهل
        }
      } catch (error) {
        console.log("V0 removal error:", error)
      }
    }

    const removeV0 = () => {
      try {
        // إزالة بسيطة للعناصر
        const elements = document.querySelectorAll('[id*="v0-built-with-button"]')
        elements.forEach((el) => {
          if (el) {
            el.style.display = "none"
            el.remove()
            console.log("🗑️ Simple removal of v0 element")
          }
        })
      } catch (error) {
        // مش مهم لو فيه خطأ
      }
    }

    // تشغيل فوري ومتعدد المراحل
    const executeRemoval = () => {
      // تشغيل فوري
      removeV0Elements()

      // تشغيل مع تأخيرات مختلفة للتأكد من الإزالة
      setTimeout(removeV0Elements, 50)
      setTimeout(removeV0Elements, 200)
      setTimeout(removeV0Elements, 500)
      setTimeout(removeV0Elements, 1000)
      setTimeout(removeV0Elements, 2000)

      // تشغيل بسيط
      setTimeout(removeV0, 1000)
    }

    // تشغيل فوري
    executeRemoval()

    // تشغيل عند الأحداث المختلفة
    if (typeof document !== "undefined") {
      // عند تحميل DOM
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", executeRemoval)
      }

      // عند تحميل الصفحة كاملة
      window.addEventListener("load", executeRemoval)

      // 🛠️ 2. إضافة حماية في observer ضد إدراج عناصر غير صالحة
      let observer: MutationObserver | null = null

      try {
        if (typeof MutationObserver !== "undefined" && document.body) {
          observer = new MutationObserver((mutations) => {
            let shouldRemove = false

            mutations.forEach((mutation) => {
              // فحص العقد المضافة حديثاً
              if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach((node) => {
                  if (node.nodeType === 1) {
                    const element = node as Element
                    const id = element.id || ""
                    const className = element.className || ""
                    const innerHTML = element.innerHTML || ""

                    // 🛠️ 2. حماية ضد إدراج عناصر v0
                    if (
                      node.nodeType === 1 &&
                      node instanceof HTMLElement &&
                      (node.id?.includes("v0") ||
                        node.id?.includes("built-with-button") ||
                        node.id?.includes("8038256c"))
                    ) {
                      try {
                        console.log("🚫 Observer blocked v0 element:", node.id)
                        node.remove()
                        return
                      } catch {}
                    }

                    if (
                      id.includes("v0") ||
                      id.includes("built-with-button") ||
                      id.includes("8038256c") ||
                      className.includes("v0") ||
                      innerHTML.includes("v0-built-with-button")
                    ) {
                      shouldRemove = true
                    }
                  }
                })
              }

              // فحص تغييرات الخصائص
              if (mutation.type === "attributes") {
                const element = mutation.target as Element
                const id = element.id || ""
                const className = element.className || ""

                if (id.includes("v0") || id.includes("built-with-button") || className.includes("v0")) {
                  shouldRemove = true
                }
              }
            })

            if (shouldRemove) {
              // تأخير قصير قبل الإزالة
              setTimeout(removeV0Elements, 10)
            }
          })

          observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ["id", "class", "style", "onclick"],
          })
        }
      } catch (error) {
        console.log("Observer setup failed:", error)
      }

      // تشغيل دوري أقل تكراراً
      const interval = setInterval(() => {
        try {
          removeV0Elements()
        } catch (error) {
          // تجاهل
        }
      }, 5000) // كل 5 ثواني

      // تنظيف عند إلغاء تحميل المكون
      return () => {
        try {
          document.removeEventListener("DOMContentLoaded", executeRemoval)
          window.removeEventListener("load", executeRemoval)
          if (observer) {
            observer.disconnect()
          }
          clearInterval(interval)
        } catch (error) {
          // تجاهل أخطاء التنظيف
        }
      }
    }
  }, [])

  return null
}
