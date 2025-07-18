import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase"
import { verifyAdminToken } from "@/lib/auth"

export async function GET(request: NextRequest) {
  try {
    const adminData = await verifyAdminToken(request)
    if (!adminData) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const supabase = createClient()

    const { data: packages, error } = await supabase
      .from("card_packages")
      .select(`
        *,
        games (
          id,
          name,
          slug
        )
      `)
      .order("sort_order")

    if (error) {
      return NextResponse.json({ error: "Failed to fetch packages" }, { status: 500 })
    }

    return NextResponse.json(packages)
  } catch (error) {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const adminData = await verifyAdminToken(request)
    if (!adminData) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { game_id, name, points, price_egp, bonus_description, is_active, sort_order } = await request.json()

    const supabase = createClient()

    const { data: package_data, error } = await supabase
      .from("card_packages")
      .insert({
        game_id,
        name,
        points,
        price_egp,
        bonus_description,
        is_active: is_active ?? true,
        sort_order: sort_order ?? 0,
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: "Failed to create package" }, { status: 500 })
    }

    return NextResponse.json(package_data)
  } catch (error) {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
