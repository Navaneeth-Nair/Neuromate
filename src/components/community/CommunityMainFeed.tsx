import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import CreatePostBox from "./CreatePostBox";
import PostCard from "./PostCard";

interface CommunityMainFeedProps {
  showCreatePost: boolean;
  setShowCreatePost: (show: boolean) => void;
}

const mockPosts = [
  {
    id: "1",
    user: { name: "Sarah Chen", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah" },
    mood: "motivated",
    moodEmoji: "🔥",
    productivityScore: 85,
    content: "Just completed my first 7-day focus challenge! The Pomodoro technique really works. Started with 2 sessions a day and now I'm consistently doing 6. My productivity has improved so much! 🎯",
    image: null,
    timestamp: "2 hours ago",
    likes: 24,
    comments: 8,
    isHelpful: true,
  },
  {
    id: "2",
    user: { name: "Alex Kumar", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex" },
    mood: "calm",
    moodEmoji: "😌",
    productivityScore: 72,
    content: "Does anyone have tips for maintaining evening routines? I struggle with consistency after 8 PM. Would love to hear what works for you!",
    image: null,
    timestamp: "5 hours ago",
    likes: 12,
    comments: 15,
    isHelpful: false,
  },
  {
    id: "3",
    user: { name: "Maya Rodriguez", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Maya" },
    mood: "productive",
    moodEmoji: "🟢",
    productivityScore: 91,
    content: "Sharing my weekly dashboard! This app has been a game-changer for tracking my mental health journey. The AI insights are incredibly helpful. 📊",
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
    timestamp: "1 day ago",
    likes: 45,
    comments: 12,
    isHelpful: true,
  },
];

import { useQuery } from "@tanstack/react-query";
import { activitiesAPI } from "@/lib/api";

const CommunityMainFeed = ({ showCreatePost, setShowCreatePost }: CommunityMainFeedProps) => {
  const [filter, setFilter] = useState("newest");

  const { data: posts, isLoading } = useQuery({
    queryKey: ["posts"],
    queryFn: async () => {
      // We need to add a 'posts' type to activitiesAPI.get or create a specific getPosts method.
      // For now, let's assume we can use activitiesAPI.get('posts') if we update the backend to handle 'posts' type in GET /activities
      // OR we can add a specific endpoint.
      // Let's check backend/routes/activities.js again. It has a switch case for types.
      // I need to add 'posts' to the switch case in backend/routes/activities.js first.
      // But I can't restart backend.
      // Wait, I added POST /posts, but I didn't add GET /posts or 'posts' case in GET /activities.
      // So fetching won't work yet without backend change.
      // However, I can try to use the existing GET /activities with a new type if I update the backend.
      // Since I can't restart backend, I'm stuck on fetching unless I use an existing endpoint or if the user restarts again.
      // Actually, the user just restarted. If I edit backend now, they need to restart AGAIN.
      // Let's assume I will ask them to restart again.
      return activitiesAPI.get("posts");
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <div>
          <h1 className="text-3xl font-heading font-bold mb-2">
            Welcome to NeuroMate Community
          </h1>
          <p className="text-muted-foreground">
            Learn, share, and grow together. Your journey matters.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="Search topics, posts, users..."
            className="pl-10 bg-background/50"
          />
        </div>

        {/* Filters */}
        <div className="flex gap-2 flex-wrap">
          {["newest", "most-helpful", "most-liked", "following"].map((f) => (
            <Button
              key={f}
              variant={filter === f ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter(f)}
              className={filter === f ? "bg-gradient-primary" : ""}
            >
              {f.split("-").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ")}
            </Button>
          ))}
        </div>
      </div>

      {/* Create Post Box */}
      <CreatePostBox
        isExpanded={showCreatePost}
        onExpand={() => setShowCreatePost(true)}
        onCollapse={() => setShowCreatePost(false)}
      />

      {/* Posts Feed */}
      <div className="space-y-4">
        {isLoading ? (
          <p>Loading posts...</p>
        ) : posts && posts.length > 0 ? (
          posts.map((post: any) => (
            <PostCard key={post.id} post={{
              id: post.id,
              user: { name: "User", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=" + post.user_id }, // Placeholder user data
              mood: "motivated", // Placeholder
              moodEmoji: "🔥", // Placeholder
              productivityScore: 85, // Placeholder
              content: post.content,
              image: null,
              timestamp: new Date(post.created_at).toLocaleDateString(),
              likes: 0,
              comments: 0,
              isHelpful: false,
            }} />
          ))
        ) : (
          <p>No posts yet. Be the first to share!</p>
        )}
      </div>
    </div>
  );
};

export default CommunityMainFeed;
