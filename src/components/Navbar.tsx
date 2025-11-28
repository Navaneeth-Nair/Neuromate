import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Brain } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useProfile } from "@/hooks/useProfile";
import PersonalSectionPanel from "./PersonalSectionPanel";

const Navbar = () => {
  const location = useLocation();
  const { user } = useAuth();
  const { profile } = useProfile(user?.id);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  
  const isActive = (path: string) => location.pathname === path;
  
  const statusColors = {
    online: 'bg-green-500',
    focusing: 'bg-yellow-500',
    'do not disturb': 'bg-red-500',
  };

  const getStatusColor = () => {
    const status = profile?.status || 'online';
    return statusColors[status as keyof typeof statusColors] || statusColors.online;
  };
  
  const navLinks = [
    { name: "Home", path: "/" },
    { name: "About", path: "/about" },
    { name: "Features", path: "/features" },
    { name: "Community", path: "/community" },
    { name: "Download", path: "/download" },
    { name: "Contact", path: "/contact" },
  ];
  
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <Brain className="h-8 w-8 text-primary transition-transform group-hover:scale-110" />
            <span className="text-2xl font-heading font-bold gradient-text">NeuroMate</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`font-heading font-semibold transition-colors ${
                  isActive(link.path)
                    ? "text-primary"
                    : "text-foreground hover:text-primary"
                }`}
              >
                {link.name}
              </Link>
            ))}
            
            {user ? (
              <button
                onClick={() => setIsPanelOpen(true)}
                className="relative group"
                aria-label="Open profile"
              >
                <Avatar className="h-10 w-10 hover:ring-2 hover:ring-primary/50 transition-all cursor-pointer">
                  <AvatarImage src={profile?.avatar_url || ''} />
                  <AvatarFallback>
                    {profile?.username?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-background ${getStatusColor()} group-hover:scale-110 transition-transform`} />
              </button>
            ) : (
              <>
                <Button variant="ghost" asChild>
                  <Link to="/auth">Sign In</Link>
                </Button>
                <Button variant="default" className="bg-gradient-primary hover-glow" asChild>
                  <a href="https://github.com/Navaneeth-Nair/Neuromate" target="_blank" rel="noopener noreferrer">
                    Download Now
                  </a>
                </Button>
              </>
            )}
          </div>
          
          <PersonalSectionPanel open={isPanelOpen} onOpenChange={setIsPanelOpen} />
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
