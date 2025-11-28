import { useState } from "react";
import { Search, Filter, Plus, MessageCircleQuestion } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import CommunityLeftSidebar from "@/components/community/CommunityLeftSidebar";
import CommunityRightSidebar from "@/components/community/CommunityRightSidebar";
import QuestionCard from "@/components/community/QuestionCard";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

// Mock Data
const questions = [
    {
        id: 1,
        title: "How do I stay consistent in my study routine?",
        description: "I start strong every week but by Wednesday I lose motivation. Does anyone use a specific tracking method that works?",
        tags: ["Productivity", "Study"],
        author: "User123",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=User123",
        timeAgo: "2 hours ago",
        upvotes: 12,
        answers: 5,
        isAnswered: true,
    },
    {
        id: 2,
        title: "Best CBT techniques for imposter syndrome?",
        description: "I just started a new job and feel like I don't belong. Looking for quick CBT exercises I can do at my desk.",
        tags: ["Wellness", "CBT", "Career"],
        author: "DevSarah",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        timeAgo: "4 hours ago",
        upvotes: 24,
        answers: 8,
        isAnswered: false,
    },
    {
        id: 3,
        title: "Can I sync NeuroMate tasks with Google Calendar?",
        description: "I love the app but I need my tasks to show up on my main calendar. Is this feature available or planned?",
        tags: ["App Feature", "Tech"],
        author: "MikeT",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike",
        timeAgo: "1 day ago",
        upvotes: 8,
        answers: 1,
        isAnswered: false,
    },
    {
        id: 4,
        title: "Morning routine ideas for non-morning people",
        description: "I struggle to wake up. What are some gentle routines to get the brain moving without caffeine overload?",
        tags: ["Wellness", "Routine"],
        author: "SleepyHead",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sleepy",
        timeAgo: "2 days ago",
        upvotes: 45,
        answers: 12,
        isAnswered: true,
    },
];

const CommunityQA = () => {
    const [isAskModalOpen, setIsAskModalOpen] = useState(false);

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
                        <div className="glass-card rounded-2xl p-8 bg-gradient-to-r from-primary/10 to-blue-500/10 border-primary/20">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h1 className="text-3xl font-heading font-bold mb-2 gradient-text flex items-center gap-2">
                                        <MessageCircleQuestion className="h-8 w-8" />
                                        Community Q&A
                                    </h1>
                                    <p className="text-muted-foreground text-lg">
                                        Ask questions → Get answers → Improve together.
                                    </p>
                                </div>
                                <Dialog open={isAskModalOpen} onOpenChange={setIsAskModalOpen}>
                                    <DialogTrigger asChild>
                                        <Button size="lg" className="gap-2 shadow-lg hover:shadow-primary/25">
                                            <Plus className="h-5 w-5" /> Ask Question
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-[600px]">
                                        <DialogHeader>
                                            <DialogTitle>Ask a Question</DialogTitle>
                                            <DialogDescription>
                                                Get help from the NeuroMate community. Be specific for better answers.
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="grid gap-4 py-4">
                                            <div className="grid gap-2">
                                                <Label htmlFor="title">Question Title</Label>
                                                <Input id="title" placeholder="e.g., How do I stay consistent with..." />
                                            </div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="description">Description</Label>
                                                <Textarea id="description" placeholder="Provide more details..." className="min-h-[150px]" />
                                            </div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="tags">Tags</Label>
                                                <Input id="tags" placeholder="e.g., productivity, wellness (comma separated)" />
                                            </div>
                                        </div>
                                        <DialogFooter>
                                            <Button variant="outline" onClick={() => setIsAskModalOpen(false)}>Cancel</Button>
                                            <Button type="submit">Post Question</Button>
                                        </DialogFooter>
                                    </DialogContent>
                                </Dialog>
                            </div>

                            {/* Search & Filter Bar */}
                            <div className="mt-8 flex flex-col sm:flex-row gap-4">
                                <div className="relative flex-1">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        placeholder="Search questions..."
                                        className="pl-10 bg-background/50"
                                    />
                                </div>
                                <Select defaultValue="recent">
                                    <SelectTrigger className="w-[180px] bg-background/50">
                                        <div className="flex items-center gap-2">
                                            <Filter className="h-4 w-4" />
                                            <SelectValue placeholder="Filter by" />
                                        </div>
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="recent">Recent</SelectItem>
                                        <SelectItem value="upvoted">Most Upvoted</SelectItem>
                                        <SelectItem value="unanswered">Unanswered</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        {/* Questions Feed */}
                        <div className="space-y-4">
                            {questions.map((q) => (
                                <QuestionCard key={q.id} question={q} />
                            ))}
                        </div>
                    </main>

                    {/* Right Sidebar */}
                    <aside className="lg:col-span-3 xl:col-span-3 hidden lg:block space-y-6">
                        <div className="sticky top-24">
                            <CommunityRightSidebar />
                            {/* Maybe add a "Trending Tags" widget here later */}
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    );
};

export default CommunityQA;
