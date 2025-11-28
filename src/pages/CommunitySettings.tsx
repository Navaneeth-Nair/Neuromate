import { useState } from "react";
import {
    User, Bell, Shield, Heart, MessageSquare, Ban,
    Eye, EyeOff, Lock, Globe, Moon, Sun, Smartphone, Mail,
    AlertTriangle, Save, Check
} from "lucide-react";
import CommunityLeftSidebar from "@/components/community/CommunityLeftSidebar";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";

const CommunitySettings = () => {
    // Mock State for Toggles
    const [visibility, setVisibility] = useState({
        showUsername: true,
        showAvatar: true,
        showJoinedDate: true,
        showStats: true,
        anonymousMode: false,
    });

    const [notifications, setNotifications] = useState({
        replies: true,
        likes: true,
        mentions: true,
        followedTopics: true,
        dailyDigest: true,
        weeklyDigest: false,
        push: true,
        email: false,
    });

    const [content, setContent] = useState({
        filterHarmful: true,
        hideTriggering: false,
        hideNSFW: true,
        hidePolitical: true,
        profanityFilter: true,
    });

    const [topics, setTopics] = useState([
        { id: "productivity", label: "Productivity", selected: true },
        { id: "motivation", label: "Motivation", selected: true },
        { id: "study", label: "Study Techniques", selected: false },
        { id: "anxiety", label: "Anxiety Support", selected: true },
        { id: "sleep", label: "Sleep", selected: false },
        { id: "fitness", label: "Fitness", selected: true },
        { id: "cbt", label: "CBT", selected: false },
        { id: "mindfulness", label: "Mindfulness", selected: true },
    ]);

    const toggleTopic = (id: string) => {
        setTopics(topics.map(t => t.id === id ? { ...t, selected: !t.selected } : t));
    };

    const blockedUsers = [
        { id: 1, name: "SpamBot99", date: "Blocked on Nov 12, 2024" },
        { id: 2, name: "NegativeVibes", date: "Blocked on Oct 24, 2024" },
    ];

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
                    <main className="lg:col-span-8 xl:col-span-8 space-y-6">
                        {/* Header */}
                        <div className="glass-card rounded-2xl p-8 bg-gradient-to-r from-primary/10 to-purple-500/10 border-primary/20">
                            <h1 className="text-3xl font-heading font-bold mb-2 gradient-text flex items-center gap-2">
                                <Shield className="h-8 w-8 text-purple-500" />
                                Community Settings
                            </h1>
                            <p className="text-muted-foreground text-lg">
                                Manage your privacy, notifications, and safety preferences.
                            </p>
                        </div>

                        {/* Profile & Visibility */}
                        <section className="glass-card rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2 rounded-lg bg-blue-500/10">
                                    <User className="h-6 w-6 text-blue-500" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold">Profile & Visibility</h2>
                                    <p className="text-sm text-muted-foreground">Control what others see about you.</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label className="text-base">Show Username Publicly</Label>
                                        <p className="text-sm text-muted-foreground">Your username will be visible on your posts.</p>
                                    </div>
                                    <Switch checked={visibility.showUsername} onCheckedChange={(c) => setVisibility({ ...visibility, showUsername: c })} />
                                </div>
                                <Separator />
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label className="text-base">Show Avatar</Label>
                                        <p className="text-sm text-muted-foreground">Display your profile picture next to your name.</p>
                                    </div>
                                    <Switch checked={visibility.showAvatar} onCheckedChange={(c) => setVisibility({ ...visibility, showAvatar: c })} />
                                </div>
                                <Separator />
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label className="text-base">Anonymous Mode</Label>
                                        <p className="text-sm text-muted-foreground">Hide your identity on all future posts (visible to mods).</p>
                                    </div>
                                    <Switch checked={visibility.anonymousMode} onCheckedChange={(c) => setVisibility({ ...visibility, anonymousMode: c })} />
                                </div>
                            </div>
                        </section>

                        {/* Notification Settings */}
                        <section className="glass-card rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2 rounded-lg bg-yellow-500/10">
                                    <Bell className="h-6 w-6 text-yellow-500" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold">Notifications</h2>
                                    <p className="text-sm text-muted-foreground">Choose how and when you want to be notified.</p>
                                </div>
                            </div>

                            <div className="grid md:grid-cols-2 gap-6">
                                <div className="space-y-4">
                                    <h3 className="font-semibold flex items-center gap-2"><Bell className="h-4 w-4" /> Activity</h3>
                                    <div className="flex items-center justify-between">
                                        <Label>Replies to your posts</Label>
                                        <Switch checked={notifications.replies} onCheckedChange={(c) => setNotifications({ ...notifications, replies: c })} />
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <Label>Likes on your posts</Label>
                                        <Switch checked={notifications.likes} onCheckedChange={(c) => setNotifications({ ...notifications, likes: c })} />
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <Label>Mentions</Label>
                                        <Switch checked={notifications.mentions} onCheckedChange={(c) => setNotifications({ ...notifications, mentions: c })} />
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <h3 className="font-semibold flex items-center gap-2"><Mail className="h-4 w-4" /> Digests & Channels</h3>
                                    <div className="flex items-center justify-between">
                                        <Label>Daily Digest</Label>
                                        <Switch checked={notifications.dailyDigest} onCheckedChange={(c) => setNotifications({ ...notifications, dailyDigest: c })} />
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <Label>Push Notifications</Label>
                                        <Switch checked={notifications.push} onCheckedChange={(c) => setNotifications({ ...notifications, push: c })} />
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <Label>Email Notifications</Label>
                                        <Switch checked={notifications.email} onCheckedChange={(c) => setNotifications({ ...notifications, email: c })} />
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* Content Filtering */}
                        <section className="glass-card rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2 rounded-lg bg-green-500/10">
                                    <Shield className="h-6 w-6 text-green-500" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold">Content & Safety</h2>
                                    <p className="text-sm text-muted-foreground">Customize your feed for a safe experience.</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label className="text-base">Filter Harmful Content</Label>
                                        <p className="text-sm text-muted-foreground">AI-based flagging of toxic or harmful posts.</p>
                                    </div>
                                    <Switch checked={content.filterHarmful} onCheckedChange={(c) => setContent({ ...content, filterHarmful: c })} />
                                </div>
                                <Separator />
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label className="text-base">Hide Triggering Content</Label>
                                        <p className="text-sm text-muted-foreground">Blur posts containing common triggers (anxiety, trauma).</p>
                                    </div>
                                    <Switch checked={content.hideTriggering} onCheckedChange={(c) => setContent({ ...content, hideTriggering: c })} />
                                </div>
                                <Separator />
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label className="text-base">Profanity Filter</Label>
                                        <p className="text-sm text-muted-foreground">Hide offensive language.</p>
                                    </div>
                                    <Switch checked={content.profanityFilter} onCheckedChange={(c) => setContent({ ...content, profanityFilter: c })} />
                                </div>
                            </div>
                        </section>

                        {/* Topic Preferences */}
                        <section className="glass-card rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2 rounded-lg bg-pink-500/10">
                                    <Heart className="h-6 w-6 text-pink-500" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold">Topic Preferences</h2>
                                    <p className="text-sm text-muted-foreground">Select topics to customize your feed.</p>
                                </div>
                            </div>

                            <div className="flex flex-wrap gap-2">
                                {topics.map((topic) => (
                                    <Badge
                                        key={topic.id}
                                        variant={topic.selected ? "default" : "outline"}
                                        className={`cursor-pointer px-4 py-2 text-sm transition-all ${topic.selected ? "hover:bg-primary/90" : "hover:bg-muted"}`}
                                        onClick={() => toggleTopic(topic.id)}
                                    >
                                        {topic.label}
                                        {topic.selected && <Check className="ml-2 h-3 w-3" />}
                                    </Badge>
                                ))}
                            </div>
                        </section>

                        {/* Blocked Users */}
                        <section className="glass-card rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2 rounded-lg bg-red-500/10">
                                    <Ban className="h-6 w-6 text-red-500" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold">Blocked Users</h2>
                                    <p className="text-sm text-muted-foreground">Manage users you have blocked.</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                {blockedUsers.map((user) => (
                                    <div key={user.id} className="flex items-center justify-between p-3 rounded-lg border bg-background/50">
                                        <div className="flex items-center gap-3">
                                            <Avatar className="h-10 w-10">
                                                <AvatarFallback>BL</AvatarFallback>
                                            </Avatar>
                                            <div>
                                                <p className="font-medium">{user.name}</p>
                                                <p className="text-xs text-muted-foreground">{user.date}</p>
                                            </div>
                                        </div>
                                        <Button variant="outline" size="sm" className="text-red-500 hover:text-red-600 hover:bg-red-50">
                                            Unblock
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        </section>

                        {/* Save Button */}
                        <div className="flex justify-end pb-10">
                            <Button size="lg" className="gap-2 shadow-lg">
                                <Save className="h-5 w-5" /> Save Changes
                            </Button>
                        </div>

                    </main>
                </div>
            </div>
        </div>
    );
};

export default CommunitySettings;
