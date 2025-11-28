import { useState } from "react";
import { Search, BookOpen, Headphones, PenTool, Download, Bookmark, Heart, MessageSquare, Filter, Play, FileText } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import CommunityLeftSidebar from "@/components/community/CommunityLeftSidebar";
import CommunityRightSidebar from "@/components/community/CommunityRightSidebar";

// Mock Data
const guides = [
    {
        id: 1,
        title: "Mastering the Floating Avatar",
        description: "Learn how to customize and interact with your AI companion effectively.",
        category: "App Guide",
        readTime: "5 min read",
        image: "/resources/floating-avatar.png",
    },
    {
        id: 2,
        title: "The Eisenhower Matrix Explained",
        description: "A deep dive into prioritizing tasks for maximum productivity.",
        category: "Productivity",
        readTime: "8 min read",
        image: "/resources/eisenhower-matrix.png",
    },
    {
        id: 3,
        title: "CBT Basics for Daily Stress",
        description: "Simple cognitive behavioral techniques to manage work anxiety.",
        category: "Wellness",
        readTime: "10 min read",
        image: "/resources/cbt-basics.png",
    },
    {
        id: 4,
        title: "Building Healthy Habits",
        description: "A step-by-step guide to creating and sticking to positive daily routines.",
        category: "Lifestyle",
        readTime: "6 min read",
        image: "/resources/healthy-habits.png",
    },
];

const audioResources = [
    {
        id: 1,
        title: "Deep Focus Playlist",
        author: "NeuroMate Team",
        duration: "45 min",
        type: "Audio",
        image: "/resources/deep-focus.png",
    },
    {
        id: 2,
        title: "Morning Mindfulness Meditation",
        author: "Dr. Sarah Calm",
        duration: "15 min",
        type: "Meditation",
        image: "/resources/mindfulness.png",
    },
    {
        id: 3,
        title: "Productivity Workshop: Time Blocking",
        author: "Productivity Pro",
        duration: "30 min",
        type: "Webinar",
        image: "/resources/productivity-workshop.png",
    },
];

const tools = [
    {
        id: 1,
        title: "Daily Planner Template",
        description: "A structured PDF for planning your day efficiently.",
        type: "PDF",
        downloads: 1240,
    },
    {
        id: 2,
        title: "Habit Tracker Sheet",
        description: "Excel sheet to track your habits over 30 days.",
        type: "Excel",
        downloads: 850,
    },
    {
        id: 3,
        title: "AI Prompt Collection",
        description: "Copy-paste prompts for brainstorming and writing.",
        type: "Text",
        downloads: 2100,
    },
];

const communityUploads = [
    {
        id: 1,
        user: "Alex Chen",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex",
        title: "My Notion Setup for Students",
        description: "A complete walkthrough of how I organize my semester.",
        likes: 45,
        comments: 12,
        tags: ["Productivity", "Study"],
    },
    {
        id: 2,
        user: "Maria Garcia",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Maria",
        title: "5-Minute Desk Yoga Routine",
        description: "Simple stretches to avoid back pain during long coding sessions.",
        likes: 89,
        comments: 24,
        tags: ["Wellness", "Health"],
    },
    {
        id: 3,
        user: "James Wilson",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=James",
        title: "Ultimate Lo-Fi Coding Playlist",
        description: "A curated list of 50+ tracks for deep work and concentration.",
        likes: 156,
        comments: 42,
        tags: ["Music", "Focus"],
    },
    {
        id: 4,
        user: "Sarah Kim",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        title: "Minimalist Bullet Journal Template",
        description: "Clean and simple PDF template for daily logging and habit tracking.",
        likes: 210,
        comments: 35,
        tags: ["Productivity", "Journaling"],
    },
];

const Resources = () => {
    const [activeTab, setActiveTab] = useState("browse");

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
                        <div className="glass-card rounded-2xl p-8 bg-gradient-to-r from-primary/10 to-purple-500/10 border-primary/20">
                            <h1 className="text-4xl font-heading font-bold mb-2 gradient-text">Resources Hub</h1>
                            <p className="text-muted-foreground text-lg">
                                Curated tools, guides, and insights shared by the NeuroMate community.
                            </p>

                            {/* Search Bar */}
                            <div className="mt-6 relative max-w-xl">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                                <Input
                                    placeholder="Search guides, templates, audio..."
                                    className="pl-10 h-12 bg-background/80 backdrop-blur-sm border-primary/20 focus:border-primary/50 transition-all"
                                />
                            </div>
                        </div>

                        {/* Custom Tabs */}
                        <div className="w-full space-y-6">
                            <div className="grid w-full grid-cols-3 mb-6 bg-muted p-1 rounded-lg">
                                <button
                                    onClick={() => setActiveTab("browse")}
                                    className={`py-2 rounded-md text-sm font-medium transition-all ${activeTab === "browse" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                                >
                                    Browse All
                                </button>
                                <button
                                    onClick={() => setActiveTab("community")}
                                    className={`py-2 rounded-md text-sm font-medium transition-all ${activeTab === "community" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                                >
                                    Community
                                </button>
                                <button
                                    onClick={() => setActiveTab("library")}
                                    className={`py-2 rounded-md text-sm font-medium transition-all ${activeTab === "library" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                                >
                                    My Library
                                </button>
                            </div>

                            {/* Browse Tab Content */}
                            {activeTab === "browse" && (
                                <div id="browse-tab-content" className="space-y-8 animate-in fade-in zoom-in-95 duration-200">
                                    {/* Guides Section */}
                                    <section>
                                        <div className="flex items-center justify-between mb-4">
                                            <h2 className="text-2xl font-bold flex items-center gap-2">
                                                <BookOpen className="h-6 w-6 text-primary" />
                                                Guides & Documentation
                                            </h2>
                                            <Button variant="ghost" size="sm">View All</Button>
                                        </div>
                                        <div className="grid md:grid-cols-2 gap-4">
                                            {guides.map((guide) => (
                                                <Card key={guide.id} className="hover:shadow-lg transition-all cursor-pointer group overflow-hidden">
                                                    <div className="h-32 overflow-hidden">
                                                        <img src={guide.image} alt={guide.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                                                    </div>
                                                    <CardHeader className="pb-2">
                                                        <div className="flex justify-between items-start">
                                                            <Badge variant="secondary" className="mb-2">{guide.category}</Badge>
                                                            <span className="text-xs text-muted-foreground">{guide.readTime}</span>
                                                        </div>
                                                        <CardTitle className="text-lg group-hover:text-primary transition-colors">{guide.title}</CardTitle>
                                                    </CardHeader>
                                                    <CardContent>
                                                        <p className="text-sm text-muted-foreground line-clamp-2">{guide.description}</p>
                                                    </CardContent>
                                                    <CardFooter>
                                                        <Button variant="outline" size="sm" className="w-full gap-2">
                                                            <Bookmark className="h-4 w-4" /> Save to Library
                                                        </Button>
                                                    </CardFooter>
                                                </Card>
                                            ))}
                                        </div>
                                    </section>

                                    {/* Audio/Video Section */}
                                    <section>
                                        <div className="flex items-center justify-between mb-4">
                                            <h2 className="text-2xl font-bold flex items-center gap-2">
                                                <Headphones className="h-6 w-6 text-blue-500" />
                                                Audio & Video
                                            </h2>
                                            <Button variant="ghost" size="sm">View All</Button>
                                        </div>
                                        <div className="grid md:grid-cols-3 gap-4">
                                            {audioResources.map((audio) => (
                                                <Card key={audio.id} className="hover:shadow-lg transition-all cursor-pointer group">
                                                    <div className="relative h-32 overflow-hidden rounded-t-xl">
                                                        <img src={audio.image} alt={audio.title} className="w-full h-full object-cover" />
                                                        <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                                            <div className="bg-white/20 backdrop-blur-md p-3 rounded-full">
                                                                <Play className="h-6 w-6 text-white fill-current" />
                                                            </div>
                                                        </div>
                                                        <Badge className="absolute bottom-2 right-2 bg-black/60">{audio.duration}</Badge>
                                                    </div>
                                                    <CardContent className="pt-4">
                                                        <h3 className="font-semibold line-clamp-1 mb-1">{audio.title}</h3>
                                                        <p className="text-xs text-muted-foreground">{audio.author}</p>
                                                    </CardContent>
                                                </Card>
                                            ))}
                                        </div>
                                    </section>

                                    {/* Tools Section */}
                                    <section>
                                        <div className="flex items-center justify-between mb-4">
                                            <h2 className="text-2xl font-bold flex items-center gap-2">
                                                <PenTool className="h-6 w-6 text-green-500" />
                                                Tools & Templates
                                            </h2>
                                            <Button variant="ghost" size="sm">View All</Button>
                                        </div>
                                        <div className="grid gap-4">
                                            {tools.map((tool) => (
                                                <div key={tool.id} className="glass-card p-4 rounded-xl flex items-center justify-between hover:bg-muted/50 transition-colors">
                                                    <div className="flex items-center gap-4">
                                                        <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                                            <FileText className="h-6 w-6" />
                                                        </div>
                                                        <div>
                                                            <h3 className="font-semibold">{tool.title}</h3>
                                                            <p className="text-sm text-muted-foreground">{tool.description}</p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-4">
                                                        <span className="text-xs text-muted-foreground hidden sm:inline-block">{tool.downloads} downloads</span>
                                                        <Button size="sm" variant="outline" className="gap-2">
                                                            <Download className="h-4 w-4" /> Download
                                                        </Button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </section>
                                </div>
                            )}

                            {/* Community Tab Content */}
                            {activeTab === "community" && (
                                <div id="community-tab-content" className="space-y-6 animate-in fade-in zoom-in-95 duration-200">
                                    <div className="flex justify-between items-center">
                                        <h2 className="text-2xl font-bold">Community Contributions</h2>
                                        <Button className="gap-2">
                                            <PenTool className="h-4 w-4" /> Contribute Resource
                                        </Button>
                                    </div>

                                    <div className="grid gap-6">
                                        {communityUploads.map((item) => (
                                            <Card key={item.id}>
                                                <CardHeader className="pb-2">
                                                    <div className="flex items-center gap-3 mb-2">
                                                        <Avatar className="h-8 w-8">
                                                            <AvatarImage src={item.avatar} />
                                                            <AvatarFallback>{item.user[0]}</AvatarFallback>
                                                        </Avatar>
                                                        <div>
                                                            <p className="text-sm font-medium">{item.user}</p>
                                                            <p className="text-xs text-muted-foreground">Shared 2 hours ago</p>
                                                        </div>
                                                    </div>
                                                    <CardTitle>{item.title}</CardTitle>
                                                    <CardDescription>{item.description}</CardDescription>
                                                </CardHeader>
                                                <CardContent>
                                                    <div className="flex gap-2">
                                                        {item.tags.map(tag => (
                                                            <Badge key={tag} variant="secondary" className="text-xs">#{tag}</Badge>
                                                        ))}
                                                    </div>
                                                </CardContent>
                                                <CardFooter className="border-t pt-4 flex justify-between">
                                                    <div className="flex gap-4">
                                                        <Button variant="ghost" size="sm" className="gap-1 text-muted-foreground">
                                                            <Heart className="h-4 w-4" /> {item.likes}
                                                        </Button>
                                                        <Button variant="ghost" size="sm" className="gap-1 text-muted-foreground">
                                                            <MessageSquare className="h-4 w-4" /> {item.comments}
                                                        </Button>
                                                    </div>
                                                    <Button variant="ghost" size="sm" className="gap-1">
                                                        <Bookmark className="h-4 w-4" /> Save
                                                    </Button>
                                                </CardFooter>
                                            </Card>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Library Tab Content */}
                            {activeTab === "library" && (
                                <div id="library-tab-content" className="animate-in fade-in zoom-in-95 duration-200">
                                    <div className="text-center py-16 glass-card rounded-2xl">
                                        <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                                            <Bookmark className="h-8 w-8 text-muted-foreground" />
                                        </div>
                                        <h3 className="text-xl font-semibold mb-2">Your Library is Empty</h3>
                                        <p className="text-muted-foreground max-w-md mx-auto mb-6">
                                            Save guides, templates, and resources here for quick access later.
                                        </p>
                                        <Button onClick={() => setActiveTab("browse")}>Browse Resources</Button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </main>

                    {/* Right Sidebar */}
                    <aside className="lg:col-span-3 xl:col-span-3 hidden lg:block space-y-6">
                        <div className="sticky top-24 space-y-6">
                            <CommunityRightSidebar />

                            {/* Smart Recommendations Widget */}
                            <Card className="bg-gradient-to-br from-primary/5 to-purple-500/5 border-primary/10">
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2 text-lg">
                                        <span className="text-xl">✨</span> Smart Picks
                                    </CardTitle>
                                    <CardDescription>Recommended for you based on your activity</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="p-3 bg-background/50 rounded-lg hover:bg-background/80 transition-colors cursor-pointer">
                                        <p className="font-medium text-sm mb-1">Focus Playlist #4</p>
                                        <p className="text-xs text-muted-foreground">Because you focused for 2h today</p>
                                    </div>
                                    <div className="p-3 bg-background/50 rounded-lg hover:bg-background/80 transition-colors cursor-pointer">
                                        <p className="font-medium text-sm mb-1">Stress Relief Guide</p>
                                        <p className="text-xs text-muted-foreground">Based on your recent mood check-in</p>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    );
};

export default Resources;
