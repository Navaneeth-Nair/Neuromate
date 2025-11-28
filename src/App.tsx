import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import About from "./pages/About";
import Features from "./pages/Features";
import Download from "./pages/Download";
import Contact from "./pages/Contact";
import Community from "./pages/Community";
import NotFound from "./pages/NotFound";
import Auth from "./pages/Auth";
import Settings from "./pages/Settings";
import Dashboard from "./pages/Dashboard";
import Productivity from "./pages/Productivity";
import Pricing from "./pages/Pricing";
import KillSwitch from "./pages/KillSwitch";
import CustomizeAvatar from "./pages/CustomizeAvatar";
import Profile from "./pages/Profile";
import MyPosts from "./pages/MyPosts";
import Resources from "./pages/Resources";
import CommunityQA from "./pages/CommunityQA";
import CommunityChallenges from "./pages/CommunityChallenges";
import CommunityTrending from "./pages/CommunityTrending";
import CommunitySettings from "./pages/CommunitySettings";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/features" element={<Features />} />
            <Route path="/download" element={<Download />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/community/*" element={<Community />} />
            <Route path="/community/resources" element={<Resources />} />
            <Route path="/community/qa" element={<CommunityQA />} />
            <Route path="/community/challenges" element={<CommunityChallenges />} />
            <Route path="/community/trending" element={<CommunityTrending />} />
            <Route path="/community/settings" element={<CommunitySettings />} />
            <Route path="/community/my-posts" element={<MyPosts />} />
            <Route path="/auth" element={<Auth />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/productivity" element={<Productivity />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/kill-switch" element={<KillSwitch />} />
            <Route path="/customize-avatar" element={<CustomizeAvatar />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
