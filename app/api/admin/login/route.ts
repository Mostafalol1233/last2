import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase"
import jwt from "jsonwebtoken"

export async function POST(request: NextRequest) {
  try {
    const { username, password } = await request.json()

    if (!username || !password) {
      return NextResponse.json({ error: "Username and password required" }, { status: 400 })
    }

    const supabase = createClient()

    const { data: admin, error } = await supabase.from("admin_users").select("*").eq("username", username).single()

    if (error || !admin) {
      return NextResponse.json({ error: "Invalid credentials" }, { status: 401 })
    }

    // For demo purposes, we'll use simple password comparison
    // In production, use proper bcrypt comparison
    const isValidPassword = password === "admin123" // Simplified for demo

    if (!isValidPassword) {
      return NextResponse.json({ error: "Invalid credentials" }, { status: 401 })
    }

    // Create JWT token
    const token = jwt.sign({ adminId: admin.id, username: admin.username }, process.env.JWT_SECRET || "demo-secret", {
      expiresIn: "24h",
    })

    const response = NextResponse.json({ success: true })
    response.cookies.set("admin-token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 86400, // 24 hours
    })

    return response
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
