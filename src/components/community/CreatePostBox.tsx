import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Image, Tag, HelpCircle, X } from "lucide-react";
import { activitiesAPI } from "@/lib/api";
import { toast } from "sonner";

interface CreatePostBoxProps {
  isExpanded: boolean;
  onExpand: () => void;
  onCollapse: () => void;
}

const moodTags = [
  { emoji: "🔥", label: "Motivated" },
  { emoji: "😌", label: "Calm" },
  { emoji: "😣", label: "Struggling" },
  { emoji: "🟢", label: "Productive" },
];

const CreatePostBox = ({ isExpanded, onExpand, onCollapse }: CreatePostBoxProps) => {
  const [content, setContent] = useState("");
  const [selectedMood, setSelectedMood] = useState<string | null>(null);

  const handlePost = async () => {
    if (!content.trim()) return;

    try {
      await activitiesAPI.createPost(content, selectedMood || undefined);
      toast.success("Post created successfully!");
      setContent("");
      setSelectedMood(null);
      onCollapse();
    } catch (error) {
      console.error("Failed to post:", error);
      toast.error("Failed to create post. Please try again.");
    }
  };

  if (!isExpanded) {
    return (
      <div
        className="glass-card rounded-2xl p-4 cursor-pointer hover:bg-muted/50 transition-colors"
        onClick={onExpand}
      >
        <div className="flex items-center gap-3">
          <Avatar>
            <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=User" />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
          <div className="flex-1 text-muted-foreground">
            Share your experience today...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-2xl p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Avatar>
            <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=User" />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
          <div>
            <p className="font-semibold">Create Post</p>
            <p className="text-xs text-muted-foreground">Share with the community</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onCollapse}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <Textarea
        placeholder="Share your experience today..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="min-h-[120px] resize-none bg-background/50"
      />

      {/* Mood Tags */}
      <div className="space-y-2">
        <p className="text-sm font-medium">How are you feeling?</p>
        <div className="flex gap-2 flex-wrap">
          {moodTags.map((mood) => (
            <Button
              key={mood.label}
              variant={selectedMood === mood.label ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedMood(mood.label)}
              className={selectedMood === mood.label ? "bg-gradient-primary" : ""}
            >
              {mood.emoji} {mood.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t">
        <div className="flex gap-2">
          <Button variant="ghost" size="sm">
            <Image className="h-4 w-4 mr-2" />
            Photo
          </Button>
          <Button variant="ghost" size="sm">
            <Tag className="h-4 w-4 mr-2" />
            Tag
          </Button>
          <Button variant="ghost" size="sm">
            <HelpCircle className="h-4 w-4 mr-2" />
            Ask Q&A
          </Button>
        </div>

        <Button
          onClick={handlePost}
          disabled={!content.trim()}
          className="bg-gradient-primary hover-glow"
        >
          Post
        </Button>
      </div>
    </div>
  );
};

export default CreatePostBox;
