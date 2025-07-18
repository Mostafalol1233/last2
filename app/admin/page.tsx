import { redirect } from "next/navigation"
import { cookies } from "next/headers"
import { AdminLoginForm } from "@/components/admin/admin-login-form"

export default async function AdminPage() {
  const cookieStore = await cookies()
  const adminToken = cookieStore.get("admin-token")

  if (adminToken) {
    redirect("/admin/dashboard")
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Admin Login</h2>
          <p className="mt-2 text-center text-sm text-gray-600">Access the admin dashboard</p>
        </div>
        <AdminLoginForm />
      </div>
    </div>
  )
}
