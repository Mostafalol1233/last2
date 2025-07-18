"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Plus, Edit, Trash } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface Game {
  id: string
  name: string
  slug: string
}

interface CardPackage {
  id: string
  game_id: string
  name: string
  points: number
  price_egp: number
  bonus_description: string
  is_active: boolean
  sort_order: number
  games?: Game
}

export function PackageManagement() {
  const [games, setGames] = useState<Game[]>([])
  const [packages, setPackages] = useState<CardPackage[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingPackage, setEditingPackage] = useState<CardPackage | null>(null)
  const [formData, setFormData] = useState({
    game_id: "",
    name: "",
    points: 0,
    price_egp: 0,
    bonus_description: "",
    is_active: true,
    sort_order: 0,
  })
  const { toast } = useToast()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [gamesResponse, packagesResponse] = await Promise.all([
        fetch("/api/admin/games"),
        fetch("/api/admin/packages"),
      ])

      const gamesData = await gamesResponse.json()
      const packagesData = await packagesResponse.json()

      setGames(gamesData)
      setPackages(packagesData)
    } catch (error) {
      console.error("Error fetching data:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const url = editingPackage ? `/api/admin/packages/${editingPackage.id}` : "/api/admin/packages"
      const method = editingPackage ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        toast({
          title: "Success",
          description: `Package ${editingPackage ? "updated" : "created"} successfully`,
        })
        handleCancel()
        fetchData()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to save package")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to save package",
        variant: "destructive",
      })
    }
  }

  const handleEdit = (pkg: CardPackage) => {
    setEditingPackage(pkg)
    setFormData({
      game_id: pkg.game_id,
      name: pkg.name,
      points: pkg.points,
      price_egp: pkg.price_egp,
      bonus_description: pkg.bonus_description,
      is_active: pkg.is_active,
      sort_order: pkg.sort_order,
    })
    setShowForm(true)
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingPackage(null)
    setFormData({
      game_id: "",
      name: "",
      points: 0,
      price_egp: 0,
      bonus_description: "",
      is_active: true,
      sort_order: 0,
    })
  }

  const handleDelete = async (packageId: string) => {
    if (!window.confirm("Are you sure you want to delete this package? This action cannot be undone.")) {
      return
    }
    try {
      const response = await fetch(`/api/admin/packages/${packageId}`, {
        method: "DELETE",
      })

      if (response.ok) {
        toast({
          title: "Success",
          description: "Package deleted successfully",
        })
        fetchData()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to delete package")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to delete package",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return <div>Loading packages...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Package Management</h2>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Package
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>{editingPackage ? "Edit Package" : "Add New Package"}</CardTitle>
            <CardDescription>
              {editingPackage ? "Update package information" : "Create a new card package"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="game_id">Game</Label>
                <Select
                  value={formData.game_id}
                  onValueChange={(value) => setFormData({ ...formData, game_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a game" />
                  </SelectTrigger>
                  <SelectContent>
                    {games.map((game) => (
                      <SelectItem key={game.id} value={game.id}>
                        {game.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Package Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="points">Points</Label>
                  <Input
                    id="points"
                    type="number"
                    value={formData.points}
                    onChange={(e) => setFormData({ ...formData, points: Number.parseInt(e.target.value) })}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="price_egp">Price (EGP)</Label>
                  <Input
                    id="price_egp"
                    type="number"
                    step="0.01"
                    value={formData.price_egp}
                    onChange={(e) => setFormData({ ...formData, price_egp: Number.parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sort_order">Sort Order</Label>
                  <Input
                    id="sort_order"
                    type="number"
                    value={formData.sort_order}
                    onChange={(e) => setFormData({ ...formData, sort_order: Number.parseInt(e.target.value) })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="bonus_description">Bonus Description</Label>
                <Input
                  id="bonus_description"
                  value={formData.bonus_description}
                  onChange={(e) => setFormData({ ...formData, bonus_description: e.target.value })}
                  placeholder="e.g., Get 50% extra points"
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                />
                <Label htmlFor="is_active">Active</Label>
              </div>

              <div className="flex space-x-2">
                <Button type="submit">{editingPackage ? "Update Package" : "Create Package"}</Button>
                <Button type="button" variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {packages.map((pkg) => (
          <Card key={pkg.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {pkg.name}
                    <Badge variant={pkg.is_active ? "default" : "secondary"}>
                      {pkg.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </CardTitle>
                  <CardDescription>{games.find((g) => g.id === pkg.game_id)?.name}</CardDescription>
                </div>
                <Button size="sm" variant="outline" onClick={() => handleEdit(pkg)}>
                  <Edit className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="destructive" onClick={() => handleDelete(pkg.id)}>
                  <Trash className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="font-medium">Points</p>
                  <p>{pkg.points.toLocaleString()}</p>
                </div>
                <div>
                  <p className="font-medium">Price</p>
                  <p>{pkg.price_egp} EGP</p>
                </div>
                <div>
                  <p className="font-medium">Bonus</p>
                  <p>{pkg.bonus_description || "None"}</p>
                </div>
                <div>
                  <p className="font-medium">Sort Order</p>
                  <p>{pkg.sort_order}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
