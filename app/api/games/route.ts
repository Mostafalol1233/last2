import { NextResponse } from "next/server"
import { createClient } from "@/lib/supabase"

export async function GET() {
  try {
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
      .eq("is_active", true)
      .order("name")

    if (error) {
      console.error("Error fetching games:", error)
      return NextResponse.json({ error: "Failed to fetch games" }, { status: 500 })
    }

    // Filter active packages and sort them
    const gamesWithPackages = games?.map((game) => ({
      ...game,
      card_packages:
        game.card_packages
          ?.filter((pkg: any) => pkg.is_active)
          ?.sort((a: any, b: any) => a.sort_order - b.sort_order) || [],
    }))

    return NextResponse.json(gamesWithPackages)
  } catch (error) {
    console.error("Error in games API:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
