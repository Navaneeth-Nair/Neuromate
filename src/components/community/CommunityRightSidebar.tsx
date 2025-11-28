import { Button } from "@/components/ui/button";
import { Trophy, Star, Users, MessageCircle, Target } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const topUsers = [
  { rank: 1, name: "Jayeed Tamboli", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Jayeed", points: 2850 },
  { rank: 2, name: "James Park", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=James", points: 2640 },
  { rank: 3, name: "Sofia Garcia", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sofia", points: 2430 },
  { rank: 4, name: "Lucas Chen", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Lucas", points: 2210 },
  { rank: 5, name: "Ava Thompson", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Ava", points: 2050 },
];

const challenges = [
  { title: "Focus Sprint", description: "25 min × 4 sessions", icon: Target, participants: 234 },
  { title: "Night Routine", description: "7 days challenge", icon: Star, participants: 187 },
];

const CommunityRightSidebar = () => {
  return (
    <div className="space-y-6">
      {/* Leaderboard */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="h-5 w-5 text-accent" />
          <h3 className="font-heading font-bold">Top Achievers This Week</h3>
        </div>
        
        <div className="space-y-3">
          {topUsers.map((user) => (
            <div key={user.rank} className="flex items-center gap-3">
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                user.rank === 1 ? "bg-yellow-400/20 text-yellow-600" :
                user.rank === 2 ? "bg-gray-400/20 text-gray-600" :
                user.rank === 3 ? "bg-orange-400/20 text-orange-600" :
                "bg-muted text-muted-foreground"
              }`}>
                {user.rank}
              </div>
              <Avatar className="h-8 w-8">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback>{user.name[0]}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user.name}</p>
              </div>
              <span className="text-sm text-muted-foreground">{user.points}</span>
            </div>
          ))}
        </div>

        <Button variant="outline" className="w-full mt-4" size="sm">
          View Full Leaderboard
        </Button>
      </div>

      {/* Daily Stats */}
      <div className="glass-card rounded-2xl p-6">
        <h3 className="font-heading font-bold mb-4">Community Stats Today</h3>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4 text-accent" />
              <span className="text-sm">Helpful Posts</span>
            </div>
            <span className="font-bold">124</span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-accent" />
              <span className="text-sm">Active Users</span>
            </div>
            <span className="font-bold">823</span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-accent" />
              <span className="text-sm">Challenges Done</span>
            </div>
            <span className="font-bold">65</span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4 text-accent" />
              <span className="text-sm">New Comments</span>
            </div>
            <span className="font-bold">340</span>
          </div>
        </div>
      </div>

      {/* Community Challenges */}
      <div className="glass-card rounded-2xl p-6">
        <h3 className="font-heading font-bold mb-4">Active Challenges</h3>
        
        <div className="space-y-3">
          {challenges.map((challenge, idx) => {
            const Icon = challenge.icon;
            return (
              <div key={idx} className="border border-border rounded-xl p-4 space-y-3">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm">{challenge.title}</h4>
                    <p className="text-xs text-muted-foreground">{challenge.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {challenge.participants} participating
                    </p>
                  </div>
                </div>
                <Button size="sm" className="w-full bg-gradient-primary">
                  Join Challenge
                </Button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default CommunityRightSidebar;
