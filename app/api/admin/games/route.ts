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

    const { data: games, error } = await supabase
      .from("games")
      .select(`
        *,
        card_packages (
          id,
          name,
          points,
          price_egp,
          bonus_description,
          is_active,
          sort_order
        )
      `)
      .order("name")

    if (error) {
      return NextResponse.json({ error: "Failed to fetch games" }, { status: 500 })
    }

    return NextResponse.json(games)
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

    const { name, slug, description, image_url, is_active } = await request.json()

    const supabase = createClient()

    const { data: game, error } = await supabase
      .from("games")
      .insert({
        name,
        slug,
        description,
        image_url,
        is_active: is_active ?? true,
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: "Failed to create game" }, { status: 500 })
    }

    return NextResponse.json(game)
  } catch (error) {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
