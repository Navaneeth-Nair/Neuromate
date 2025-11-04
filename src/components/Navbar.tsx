import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Brain } from "lucide-react";

const Navbar = () => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  const navLinks = [
    { name: "Home", path: "/" },
    { name: "About", path: "/about" },
    { name: "Features", path: "/features" },
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
            
            <Button variant="default" className="bg-gradient-primary hover-glow">
              Download Now
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
