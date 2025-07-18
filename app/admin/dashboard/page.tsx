import { redirect } from "next/navigation"
import { cookies } from "next/headers"
import { AdminDashboard } from "@/components/admin/admin-dashboard"

export default async function AdminDashboardPage() {
  const cookieStore = await cookies()
  const adminToken = cookieStore.get("admin-token")

  if (!adminToken) {
    redirect("/admin")
  }

  return <AdminDashboard />
}
