import { Link, useLocation } from "react-router-dom";
import { Home, Flame, MessageCircleQuestion, Target, FileText, BookOpen, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { icon: Home, label: "Community Home", path: "/community" },
  { icon: Flame, label: "Trending Topics", path: "/community/trending" },
  { icon: MessageCircleQuestion, label: "Q&A", path: "/community/qa" },
  { icon: Target, label: "Challenges", path: "/community/challenges" },
  { icon: FileText, label: "My Posts", path: "/community/my-posts" },
  { icon: BookOpen, label: "Resources", path: "/community/resources" },
  { icon: Settings, label: "Settings", path: "/community/settings" },
];

const CommunityLeftSidebar = () => {
  const location = useLocation();

  return (
    <nav className="glass-card rounded-2xl p-4 space-y-2">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.path;
        
        return (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-xl transition-all",
              isActive
                ? "bg-primary/20 text-primary font-semibold"
                : "text-foreground hover:bg-muted"
            )}
          >
            <Icon className="h-5 w-5 flex-shrink-0" />
            <span className="text-sm hidden xl:block">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
};

export default CommunityLeftSidebar;
