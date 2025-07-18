"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Plus, Edit, Trash } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface Game {
  id: string
  name: string
  slug: string
  description: string
  image_url: string
  is_active: boolean
  card_packages?: any[]
}

interface GameManagementProps {
  onUpdate: () => void
}

export function GameManagement({ onUpdate }: GameManagementProps) {
  const [games, setGames] = useState<Game[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingGame, setEditingGame] = useState<Game | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    slug: "",
    description: "",
    image_url: "",
    is_active: true,
  })
  const { toast } = useToast()

  useEffect(() => {
    fetchGames()
  }, [])

  const fetchGames = async () => {
    try {
      const response = await fetch("/api/admin/games")
      const data = await response.json()
      setGames(data)
      onUpdate()
    } catch (error) {
      console.error("Error fetching games:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const url = editingGame ? `/api/admin/games/${editingGame.id}` : "/api/admin/games"
      const method = editingGame ? "PUT" : "POST"

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
          description: `Game ${editingGame ? "updated" : "created"} successfully`,
        })
        setShowForm(false)
        setEditingGame(null)
        setFormData({
          name: "",
          slug: "",
          description: "",
          image_url: "",
          is_active: true,
        })
        fetchGames()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to save game")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to save game",
        variant: "destructive",
      })
    }
  }

  const handleEdit = (game: Game) => {
    setEditingGame(game)
    setFormData({
      name: game.name,
      slug: game.slug,
      description: game.description,
      image_url: game.image_url,
      is_active: game.is_active,
    })
    setShowForm(true)
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingGame(null)
    setFormData({
      name: "",
      slug: "",
      description: "",
      image_url: "",
      is_active: true,
    })
  }

  const handleDelete = async (gameId: string) => {
    if (!window.confirm("Are you sure you want to delete this game? This action cannot be undone.")) {
      return
    }
    try {
      const response = await fetch(`/api/admin/games/${gameId}`, {
        method: "DELETE",
      })

      if (response.ok) {
        toast({
          title: "Success",
          description: "Game deleted successfully",
        })
        fetchGames()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to delete game")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to delete game",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return <div>Loading games...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Game Management</h2>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Game
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>{editingGame ? "Edit Game" : "Add New Game"}</CardTitle>
            <CardDescription>{editingGame ? "Update game information" : "Create a new game entry"}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Game Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="slug">Slug</Label>
                  <Input
                    id="slug"
                    value={formData.slug}
                    onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="image_url">Image URL</Label>
                <Input
                  id="image_url"
                  value={formData.image_url}
                  onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                  placeholder="/placeholder.svg?height=200&width=300"
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
                <Button type="submit">{editingGame ? "Update Game" : "Create Game"}</Button>
                <Button type="button" variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {games.map((game) => (
          <Card key={game.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {game.name}
                    <Badge variant={game.is_active ? "default" : "secondary"}>
                      {game.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </CardTitle>
                  <CardDescription>{game.description}</CardDescription>
                </div>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline" onClick={() => handleEdit(game)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="destructive" onClick={() => handleDelete(game.id)}>
                    <Trash className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-gray-600">
                <p>Slug: {game.slug}</p>
                <p>Packages: {game.card_packages?.length || 0}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
