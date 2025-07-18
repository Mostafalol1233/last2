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
    const { game_id, name, points, price_egp, bonus_description, is_active, sort_order } = await request.json()

    if (!id) {
      return NextResponse.json({ error: "Package ID is required" }, { status: 400 })
    }

    const supabase = createClient()

    const { data: package_data, error } = await supabase
      .from("card_packages")
      .update({
        game_id,
        name,
        points,
        price_egp,
        bonus_description,
        is_active,
        sort_order,
        updated_at: new Date().toISOString(),
      })
      .eq("id", id)
      .select()
      .single()

    if (error) {
      console.error("Error updating package:", error)
      return NextResponse.json({ error: error.message || "Failed to update package" }, { status: 500 })
    }

    return NextResponse.json(package_data)
  } catch (error: any) {
    console.error("Error in PUT /api/admin/packages/[id]:", error)
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
      return NextResponse.json({ error: "Package ID is required" }, { status: 400 })
    }

    const supabase = createClient()

    const { error } = await supabase.from("card_packages").delete().eq("id", id)

    if (error) {
      console.error("Error deleting package:", error)
      return NextResponse.json({ error: error.message || "Failed to delete package" }, { status: 500 })
    }

    return NextResponse.json({ message: "Package deleted successfully" })
  } catch (error: any) {
    console.error("Error in DELETE /api/admin/packages/[id]:", error)
    return NextResponse.json({ error: error.message || "Internal server error" }, { status: 500 })
  }
}
