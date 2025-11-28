import { useState } from "react";
import CommunityLeftSidebar from "@/components/community/CommunityLeftSidebar";
import CommunityMainFeed from "@/components/community/CommunityMainFeed";
import CommunityRightSidebar from "@/components/community/CommunityRightSidebar";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

const Community = () => {
  const [showCreatePost, setShowCreatePost] = useState(false);

  return (
    <div className="min-h-screen pt-20 bg-gradient-hero">
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar - Navigation */}
          <aside className="lg:col-span-2 xl:col-span-2">
            <div className="sticky top-24">
              <CommunityLeftSidebar />
            </div>
          </aside>

          {/* Main Feed */}
          <main className="lg:col-span-7 xl:col-span-7">
            <CommunityMainFeed 
              showCreatePost={showCreatePost}
              setShowCreatePost={setShowCreatePost}
            />
          </main>

          {/* Right Sidebar - Leaderboard & Stats */}
          <aside className="lg:col-span-3 xl:col-span-3 hidden lg:block">
            <div className="sticky top-24">
              <CommunityRightSidebar />
            </div>
          </aside>
        </div>
      </div>

      {/* Floating Quick-Action Button */}
      <Button
        onClick={() => setShowCreatePost(true)}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg bg-gradient-primary hover-glow z-50"
        size="icon"
      >
        <Plus className="h-6 w-6" />
      </Button>
    </div>
  );
};

export default Community;
