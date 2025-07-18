import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase"
import { verifyAdminToken } from "@/lib/auth"

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const adminData = await verifyAdminToken(request)
    if (!adminData) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { id } = params
    const { name, slug, description, image_url, is_active } = await request.json()

    if (!id) {
      return NextResponse.json({ error: "Game ID is required" }, { status: 400 })
    }

    const supabase = createClient()

    const { data: game, error } = await supabase
      .from("games")
      .update({
        name,
        slug,
        description,
        image_url,
        is_active,
        updated_at: new Date().toISOString(),
      })
      .eq("id", id)
      .select()
      .single()

    if (error) {
      console.error("Error updating game:", error)
      // Check for unique constraint violation on slug
      if (error.code === "23505" && error.constraint === "games_slug_key") {
        return NextResponse.json({ error: "Slug already exists. Please choose a different one." }, { status: 409 })
      }
      return NextResponse.json({ error: error.message || "Failed to update game" }, { status: 500 })
    }

    return NextResponse.json(game)
  } catch (error: any) {
    console.error("Error in PUT /api/admin/games/[id]:", error)
    return NextResponse.json({ error: error.message || "Internal server error" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const adminData = await verifyAdminToken(request)
    if (!adminData) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { id } = params

    if (!id) {
      return NextResponse.json({ error: "Game ID is required" }, { status: 400 })
    }

    const supabase = createClient()

    const { error } = await supabase.from("games").delete().eq("id", id)

    if (error) {
      console.error("Error deleting game:", error)
      return NextResponse.json({ error: error.message || "Failed to delete game" }, { status: 500 })
    }

    return NextResponse.json({ message: "Game deleted successfully" })
  } catch (error: any) {
    console.error("Error in DELETE /api/admin/games/[id]:", error)
    return NextResponse.json({ error: error.message || "Internal server error" }, { status: 500 })
  }
}
