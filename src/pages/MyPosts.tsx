import { useQuery } from "@tanstack/react-query";
import { activitiesAPI } from "@/lib/api";
import PostCard from "@/components/community/PostCard";
import CommunityLeftSidebar from "@/components/community/CommunityLeftSidebar";
import CommunityRightSidebar from "@/components/community/CommunityRightSidebar";

const MyPosts = () => {
    const { data: posts, isLoading } = useQuery({
        queryKey: ["my-posts"],
        queryFn: async () => {
            return activitiesAPI.get("my-posts");
        },
    });

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
                        <div className="space-y-6">
                            <div className="glass-card rounded-2xl p-6">
                                <h1 className="text-3xl font-heading font-bold mb-2">My Posts</h1>
                                <p className="text-muted-foreground">
                                    View and manage your contributions to the community.
                                </p>
                            </div>

                            <div className="space-y-4">
                                {isLoading ? (
                                    <p>Loading your posts...</p>
                                ) : posts && posts.length > 0 ? (
                                    posts.map((post: any) => (
                                        <PostCard key={post.id} post={{
                                            id: post.id,
                                            user: { name: "You", avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=" + post.user_id },
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
                                    <div className="text-center py-10 glass-card rounded-2xl">
                                        <p className="text-muted-foreground">You haven't posted anything yet.</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </main>

                    {/* Right Sidebar - Leaderboard & Stats */}
                    <aside className="lg:col-span-3 xl:col-span-3 hidden lg:block">
                        <div className="sticky top-24">
                            <CommunityRightSidebar />
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    );
};

export default MyPosts;
