import type { NextRequest } from "next/server"
import jwt from "jsonwebtoken"

export async function verifyAdminToken(request: NextRequest) {
  try {
    const token = request.cookies.get("admin-token")?.value

    if (!token) {
      return null
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET || "demo-secret") as any
    return decoded
  } catch (error) {
    return null
  }
}
