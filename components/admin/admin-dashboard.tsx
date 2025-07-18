"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { GameManagement } from "./game-management"
import { PackageManagement } from "./package-management"
import { LogOut, Gamepad2, Package, BarChart3 } from "lucide-react"
import { useRouter } from "next/navigation"

export function AdminDashboard() {
  const [stats, setStats] = useState({
    totalGames: 0,
    totalPackages: 0,
    activeGames: 0,
  })
  const router = useRouter()

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch("/api/admin/games")
      const games = await response.json()

      const totalPackages = games.reduce((sum: number, game: any) => sum + (game.card_packages?.length || 0), 0)

      setStats({
        totalGames: games.length,
        totalPackages,
        activeGames: games.filter((game: any) => game.is_active).length,
      })
    } catch (error) {
      console.error("Error fetching stats:", error)
    }
  }

  const handleLogout = async () => {
    try {
      await fetch("/api/admin/logout", { method: "POST" })
      router.push("/admin")
    } catch (error) {
      console.error("Logout error:", error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
            <Button onClick={handleLogout} variant="outline">
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Games</CardTitle>
              <Gamepad2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalGames}</div>
              <p className="text-xs text-muted-foreground">{stats.activeGames} active</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Card Packages</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalPackages}</div>
              <p className="text-xs text-muted-foreground">Across all games</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Games</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeGames}</div>
              <p className="text-xs text-muted-foreground">Currently visible</p>
            </CardContent>
          </Card>
        </div>

        {/* Management Tabs */}
        <Tabs defaultValue="games" className="space-y-4">
          <TabsList>
            <TabsTrigger value="games">Games</TabsTrigger>
            <TabsTrigger value="packages">Card Packages</TabsTrigger>
          </TabsList>

          <TabsContent value="games">
            <GameManagement onUpdate={fetchStats} />
          </TabsContent>

          <TabsContent value="packages">
            <PackageManagement />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
