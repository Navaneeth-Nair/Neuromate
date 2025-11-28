import { Flame, TrendingUp, Hash, ArrowUpRight } from "lucide-react";
import CommunityLeftSidebar from "@/components/community/CommunityLeftSidebar";
import CommunityRightSidebar from "@/components/community/CommunityRightSidebar";
import TrendingTopicCard from "@/components/community/TrendingTopicCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// Mock Data
const trendingTopics = [
    {
        id: 1,
        tag: "#DeepWorkRoutine",
        title: "How do you maintain 2h focus blocks without burnout?",
        description: "Discussing the Pomodoro technique vs. 90-minute ultradian rhythms for maximum output.",
        replies: 247,
        views: 1200,
        growth: 142,
        isHot: true,
    },
    {
        id: 2,
        tag: "#MorningAnxiety",
        title: "I finally fixed my morning anxiety with this 10-min habit stack",
        description: "Sharing my routine involving cold water, gratitude journaling, and no phone for 30 mins.",
        replies: 482,
        views: 5600,
        growth: 86,
        isHot: true,
    },
    {
        id: 3,
        tag: "#SleepHealth",
        title: "Does magnesium glycinate actually help with deep sleep?",
        description: "Looking for community experiences with supplements for improving sleep quality.",
        replies: 118,
        views: 3400,
        growth: 45,
        isHot: false,
    },
    {
        id: 4,
        tag: "#DigitalMinimalism",
        title: "Challenge: 24 hours without social media. Who's in?",
        description: "A collective challenge to reset our dopamine receptors this weekend.",
        replies: 320,
        views: 2100,
        growth: 210,
        isHot: true,
    },
    {
        id: 5,
        tag: "#StudyHacks",
        title: "The Feynman Technique explained simply",
        description: "How to learn anything faster by teaching it to a 5-year-old (or your rubber duck).",
        replies: 95,
        views: 1800,
        growth: 32,
        isHot: false,
    },
    {
        id: 6,
        tag: "#JournalingPrompts",
        title: "Stoic evening reflection prompts",
        description: "5 questions to ask yourself every night to build resilience and clarity.",
        replies: 156,
        views: 2900,
        growth: 67,
        isHot: false,
    },
];

const topTags = [
    "#DeepWork", "#StudyHacks", "#MoodBoosters", "#NightRoutine", "#AnxietyTips", "#Minimalism", "#Focus", "#CBT"
];

const CommunityTrending = () => {
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
                        <div className="glass-card rounded-2xl p-8 bg-gradient-to-r from-primary/10 to-red-500/10 border-primary/20">
                            <h1 className="text-3xl font-heading font-bold mb-2 gradient-text flex items-center gap-2">
                                <Flame className="h-8 w-8 text-red-500" />
                                Trending Topics
                            </h1>
                            <p className="text-muted-foreground text-lg">
                                Discover what the community is talking about right now.
                            </p>
                        </div>

                        {/* Trending Bar */}
                        <div className="glass-card p-4 rounded-xl flex items-center gap-4 overflow-x-auto scrollbar-hide">
                            <div className="flex items-center gap-2 font-bold whitespace-nowrap text-sm text-muted-foreground">
                                <TrendingUp className="h-4 w-4" /> Trending:
                            </div>
                            <div className="flex gap-2">
                                {topTags.map((tag) => (
                                    <Badge
                                        key={tag}
                                        variant="secondary"
                                        className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors px-3 py-1 text-sm"
                                    >
                                        {tag}
                                    </Badge>
                                ))}
                            </div>
                        </div>

                        {/* Trending Grid */}
                        <div className="grid md:grid-cols-2 gap-6">
                            {trendingTopics.map((topic) => (
                                <TrendingTopicCard key={topic.id} topic={topic} />
                            ))}
                        </div>
                    </main>

                    {/* Right Sidebar */}
                    <aside className="lg:col-span-3 xl:col-span-3 hidden lg:block space-y-6">
                        <div className="sticky top-24 space-y-6">
                            <CommunityRightSidebar />

                            {/* Rising Keywords Widget */}
                            <div className="glass-card p-4 rounded-xl space-y-4">
                                <div className="flex items-center gap-2 font-semibold">
                                    <TrendingUp className="h-5 w-5 text-green-500" />
                                    <h3>Fastest Rising</h3>
                                </div>
                                <div className="space-y-3">
                                    {[
                                        { tag: "#DopamineDetox", growth: "+340%" },
                                        { tag: "#ExamSeason", growth: "+210%" },
                                        { tag: "#WinterBlues", growth: "+180%" }
                                    ].map((item, i) => (
                                        <div key={i} className="flex items-center justify-between text-sm group cursor-pointer">
                                            <div className="flex items-center gap-2">
                                                <Hash className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                                                <span className="group-hover:text-primary transition-colors">{item.tag}</span>
                                            </div>
                                            <span className="font-mono text-green-600 text-xs font-bold">{item.growth}</span>
                                        </div>
                                    ))}
                                </div>
                                <Button variant="ghost" size="sm" className="w-full text-xs text-muted-foreground">
                                    View Analytics <ArrowUpRight className="h-3 w-3 ml-1" />
                                </Button>
                            </div>
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    );
};

export default CommunityTrending;
