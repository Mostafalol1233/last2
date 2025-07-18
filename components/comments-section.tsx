"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { MessageCircle, Send, Heart } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface Comment {
  id: string
  name: string
  message: string
  timestamp: string
  likes: number
}

export function CommentsSection() {
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState({ name: "", message: "" })
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    // Load comments from localStorage on component mount
    const savedComments = localStorage.getItem("gamestore-comments")
    if (savedComments) {
      setComments(JSON.parse(savedComments))
    }
  }, [])

  const saveCommentsToStorage = (updatedComments: Comment[]) => {
    localStorage.setItem("gamestore-comments", JSON.stringify(updatedComments))
  }

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newComment.name.trim() || !newComment.message.trim()) {
      toast({
        title: "Error",
        description: "Please fill in both name and message fields.",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    const comment: Comment = {
      id: Date.now().toString(),
      name: newComment.name.trim(),
      message: newComment.message.trim(),
      timestamp: new Date().toISOString(),
      likes: 0,
    }

    const updatedComments = [comment, ...comments]
    setComments(updatedComments)
    saveCommentsToStorage(updatedComments)

    setNewComment({ name: "", message: "" })
    setLoading(false)

    toast({
      title: "Comment posted!",
      description: "Your comment has been added successfully.",
    })
  }

  const handleLikeComment = (commentId: string) => {
    const updatedComments = comments.map((comment) =>
      comment.id === commentId ? { ...comment, likes: comment.likes + 1 } : comment,
    )
    setComments(updatedComments)
    saveCommentsToStorage(updatedComments)
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) return "Just now"
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return `${Math.floor(diffInMinutes / 1440)}d ago`
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <section className="py-16 px-4">
      <div className="container mx-auto max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center space-x-2 bg-purple-500/10 backdrop-blur-sm rounded-full px-6 py-3 mb-6">
            <MessageCircle className="h-6 w-6 text-purple-400" />
            <span className="text-purple-300 font-medium">Community</span>
          </div>

          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Comments & Reviews
          </h2>

          <p className="text-gray-300 dark:text-gray-400 max-w-2xl mx-auto">
            Share your thoughts, experiences, or ask questions about our game cards!
          </p>
        </div>

        {/* Comment Form */}
        <Card className="mb-8 bg-white/5 backdrop-blur-sm border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <MessageCircle className="h-5 w-5 mr-2 text-purple-400" />
              Leave a Comment
            </CardTitle>
            <CardDescription className="text-gray-400">
              Share your experience or ask any questions about our services
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmitComment} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name" className="text-white">
                  Your Name
                </Label>
                <Input
                  id="name"
                  value={newComment.name}
                  onChange={(e) => setNewComment({ ...newComment, name: e.target.value })}
                  placeholder="Enter your name"
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  maxLength={50}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="message" className="text-white">
                  Your Comment
                </Label>
                <Textarea
                  id="message"
                  value={newComment.message}
                  onChange={(e) => setNewComment({ ...newComment, message: e.target.value })}
                  placeholder="Write your comment here..."
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400 min-h-[100px]"
                  maxLength={500}
                />
                <div className="text-right text-sm text-gray-400">{newComment.message.length}/500</div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
              >
                <Send className="h-4 w-4 mr-2" />
                {loading ? "Posting..." : "Post Comment"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Comments List */}
        <div className="space-y-4">
          {comments.length === 0 ? (
            <Card className="bg-white/5 backdrop-blur-sm border-white/10">
              <CardContent className="py-12 text-center">
                <MessageCircle className="h-12 w-12 text-gray-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-400 mb-2">No comments yet</h3>
                <p className="text-gray-500">Be the first to share your thoughts!</p>
              </CardContent>
            </Card>
          ) : (
            comments.map((comment) => (
              <Card
                key={comment.id}
                className="bg-white/5 backdrop-blur-sm border-white/10 hover:bg-white/10 transition-colors"
              >
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <Avatar className="bg-gradient-to-br from-purple-400 to-pink-400">
                      <AvatarFallback className="bg-transparent text-white font-semibold">
                        {getInitials(comment.name)}
                      </AvatarFallback>
                    </Avatar>

                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-semibold text-white">{comment.name}</h4>
                          <span className="text-sm text-gray-400">{formatTimestamp(comment.timestamp)}</span>
                        </div>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleLikeComment(comment.id)}
                          className="text-gray-400 hover:text-red-400 hover:bg-red-500/10"
                        >
                          <Heart className="h-4 w-4 mr-1" />
                          {comment.likes}
                        </Button>
                      </div>

                      <p className="text-gray-300 leading-relaxed">{comment.message}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Stats */}
        {comments.length > 0 && (
          <div className="mt-8 text-center">
            <div className="inline-flex items-center space-x-4 bg-white/5 backdrop-blur-sm rounded-full px-6 py-3">
              <div className="flex items-center space-x-2">
                <MessageCircle className="h-4 w-4 text-purple-400" />
                <span className="text-sm text-gray-300">{comments.length} Comments</span>
              </div>
              <div className="flex items-center space-x-2">
                <Heart className="h-4 w-4 text-red-400" />
                <span className="text-sm text-gray-300">
                  {comments.reduce((total, comment) => total + comment.likes, 0)} Likes
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
