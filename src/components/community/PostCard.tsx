import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Heart, MessageCircle, Repeat2, Star, Flag, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

interface Post {
  id: string;
  user: {
    name: string;
    avatar: string;
  };
  mood: string;
  moodEmoji: string;
  productivityScore?: number;
  content: string;
  image?: string | null;
  timestamp: string;
  likes: number;
  comments: number;
  isHelpful: boolean;
}

interface PostCardProps {
  post: Post;
}

const PostCard = ({ post }: PostCardProps) => {
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(post.likes);
  const [showAISummary, setShowAISummary] = useState(false);
  const { toast } = useToast();

  const handleLike = () => {
    setLiked(!liked);
    setLikeCount(liked ? likeCount - 1 : likeCount + 1);
  };

  const handleAISummary = () => {
    setShowAISummary(!showAISummary);
    if (!showAISummary) {
      toast({
        title: "AI Summary Generated",
        description: "Key insight: User shows significant progress in maintaining focus routines.",
      });
    }
  };

  return (
    <div className="glass-card rounded-2xl p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Avatar>
            <AvatarImage src={post.user.avatar} alt={post.user.name} />
            <AvatarFallback>{post.user.name[0]}</AvatarFallback>
          </Avatar>
          <div>
            <div className="flex items-center gap-2">
              <p className="font-semibold">{post.user.name}</p>
              {post.productivityScore && (
                <Badge variant="secondary" className="text-xs">
                  {post.productivityScore} pts
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>{post.moodEmoji} {post.mood}</span>
              <span>•</span>
              <span>{post.timestamp}</span>
            </div>
          </div>
        </div>
        
        {post.isHelpful && (
          <Badge className="bg-accent/20 text-accent border-accent/30">
            <Star className="h-3 w-3 mr-1" />
            Helpful
          </Badge>
        )}
      </div>

      {/* Content */}
      <div className="space-y-3">
        <p className="text-foreground leading-relaxed">{post.content}</p>
        
        {post.image && (
          <img 
            src={post.image} 
            alt="Post attachment"
            className="rounded-xl w-full object-cover max-h-96"
          />
        )}
        
        {/* AI Summary */}
        {showAISummary && (
          <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <Sparkles className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-primary mb-1">AI Insight</p>
                <p className="text-sm text-foreground">
                  This post demonstrates effective use of the Pomodoro technique with measurable progress. 
                  The user's consistency improvement from 2 to 6 sessions shows strong habit formation.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t">
        <div className="flex gap-1">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={handleLike}
            className={liked ? "text-red-500" : ""}
          >
            <Heart className={`h-4 w-4 mr-2 ${liked ? "fill-red-500" : ""}`} />
            {likeCount}
          </Button>
          
          <Button variant="ghost" size="sm">
            <MessageCircle className="h-4 w-4 mr-2" />
            {post.comments}
          </Button>
          
          <Button variant="ghost" size="sm">
            <Repeat2 className="h-4 w-4 mr-2" />
            Share
          </Button>
          
          <Button variant="ghost" size="sm">
            <Star className="h-4 w-4 mr-2" />
            Mark Helpful
          </Button>
        </div>
        
        <div className="flex gap-1">
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleAISummary}
            className="text-primary border-primary/30"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            AI Summary
          </Button>
          
          <Button variant="ghost" size="sm">
            <Flag className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PostCard;
