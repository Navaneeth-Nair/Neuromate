import { useState } from "react";
import { Target, Trophy, Flame, Zap, Brain, Heart } from "lucide-react";
import CommunityLeftSidebar from "@/components/community/CommunityLeftSidebar";
import CommunityRightSidebar from "@/components/community/CommunityRightSidebar";
import ChallengeCard from "@/components/community/ChallengeCard";
import { Button } from "@/components/ui/button";

// Mock Data
const challenges = [
    {
        id: 1,
        title: "30-Day Productivity Sprint",
        description: "Boost your focus and output with daily micro-tasks designed to build consistency.",
        duration: "30 Days",
        level: "Medium" as const,
        participants: 3244,
        category: "Productivity",
        isJoined: true,
        progress: 60,
        streak: 6,
    },
    {
        id: 2,
        title: "Morning Mindfulness",
        description: "Start your day with 10 minutes of guided meditation and intention setting.",
        duration: "14 Days",
        level: "Easy" as const,
        participants: 1205,
        category: "Wellbeing",
        isJoined: false,
    },
    {
        id: 3,
        title: "Deep Work Week",
        description: "Commit to 2 hours of distraction-free deep work every day for a week.",
        duration: "7 Days",
        level: "Hard" as const,
        participants: 850,
        category: "Productivity",
        isJoined: false,
    },
    {
        id: 4,
        title: "Hydration Hero",
        description: "Track your water intake and hit your daily hydration goals.",
        duration: "21 Days",
        level: "Easy" as const,
        participants: 5600,
        category: "Health",
        isJoined: true,
        progress: 15,
        streak: 3,
    },
    {
        id: 5,
        title: "Learn a New Skill",
        description: "Dedicate 30 minutes daily to learning something completely new.",
        duration: "10 Days",
        level: "Medium" as const,
        participants: 940,
        category: "Skill Growth",
        isJoined: false,
    },
    {
        id: 6,
        title: "Digital Detox Weekend",
        description: "Disconnect from screens and reconnect with the real world.",
        duration: "2 Days",
        level: "Medium" as const,
        participants: 2100,
        category: "Wellbeing",
        isJoined: false,
    },
];

const categories = [
    { id: "all", label: "All Challenges", icon: Target },
    { id: "productivity", label: "Productivity", icon: Zap },
    { id: "wellbeing", label: "Wellbeing", icon: Heart },
    { id: "skill", label: "Skill Growth", icon: Brain },
    { id: "event", label: "Events", icon: Flame },
];

const CommunityChallenges = () => {
    const [activeCategory, setActiveCategory] = useState("all");

    const filteredChallenges = activeCategory === "all"
        ? challenges
        : challenges.filter(c => c.category.toLowerCase().includes(activeCategory) || (activeCategory === "skill" && c.category === "Skill Growth"));

    return (
        <div className="min-h-screen pt-20 bg-gradient-hero">
            <div className="container mx-auto px-4 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left Sidebar */}
                    <aside className="lg:col-span-2 xl:col-span-2">
                        <div className="sticky top-24">
                            <CommunityLeftSidebar />
                        </div>
                    </aside>

                    {/* Main Content */}
                    <main className="lg:col-span-7 xl:col-span-7 space-y-6">
                        {/* Header */}
                        <div className="glass-card rounded-2xl p-8 bg-gradient-to-r from-primary/10 to-orange-500/10 border-primary/20">
                            <h1 className="text-3xl font-heading font-bold mb-2 gradient-text flex items-center gap-2">
                                <Trophy className="h-8 w-8 text-orange-500" />
                                Community Challenges
                            </h1>
                            <p className="text-muted-foreground text-lg">
                                Build habits, stay accountable, and grow with the community.
                            </p>
                        </div>

                        {/* Category Filter */}
                        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                            {categories.map((cat) => {
                                const Icon = cat.icon;
                                return (
                                    <Button
                                        key={cat.id}
                                        variant={activeCategory === cat.id ? "default" : "outline"}
                                        className="gap-2 rounded-full whitespace-nowrap"
                                        onClick={() => setActiveCategory(cat.id)}
                                    >
                                        <Icon className="h-4 w-4" />
                                        {cat.label}
                                    </Button>
                                )
                            })}
                        </div>

                        {/* Challenges Grid */}
                        <div className="grid md:grid-cols-2 gap-6">
                            {filteredChallenges.map((challenge) => (
                                <ChallengeCard key={challenge.id} challenge={challenge} />
                            ))}
                        </div>
                    </main>

                    {/* Right Sidebar */}
                    <aside className="lg:col-span-3 xl:col-span-3 hidden lg:block space-y-6">
                        <div className="sticky top-24 space-y-6">
                            <CommunityRightSidebar />

                            {/* Mini Leaderboard Widget */}
                            <div className="glass-card p-4 rounded-xl space-y-4">
                                <div className="flex items-center gap-2 font-semibold">
                                    <Flame className="h-5 w-5 text-orange-500" />
                                    <h3>Top Streaks</h3>
                                </div>
                                <div className="space-y-3">
                                    {[1, 2, 3].map((i) => (
                                        <div key={i} className="flex items-center justify-between text-sm">
                                            <div className="flex items-center gap-2">
                                                <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center font-bold text-xs">
                                                    {i}
                                                </div>
                                                <span>User{900 + i}</span>
                                            </div>
                                            <span className="font-mono text-muted-foreground">{50 - i * 5} days</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    );
};

export default CommunityChallenges;
