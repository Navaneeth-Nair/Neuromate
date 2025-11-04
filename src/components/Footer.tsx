import { Link } from "react-router-dom";
import { Brain, Github, Linkedin, Twitter } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-gradient-primary py-12 mt-24">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Brain className="h-6 w-6 text-foreground" />
              <span className="text-xl font-heading font-bold text-foreground">NeuroMate</span>
            </div>
            <p className="text-foreground/80 text-sm">
              Your AI companion for a calmer, more focused you.
            </p>
          </div>
          
          <div>
            <h3 className="font-heading font-semibold mb-4 text-foreground">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link to="/" className="text-foreground/80 hover:text-foreground transition-colors">Home</Link></li>
              <li><Link to="/about" className="text-foreground/80 hover:text-foreground transition-colors">About</Link></li>
              <li><Link to="/features" className="text-foreground/80 hover:text-foreground transition-colors">Features</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-heading font-semibold mb-4 text-foreground">Support</h3>
            <ul className="space-y-2">
              <li><Link to="/download" className="text-foreground/80 hover:text-foreground transition-colors">Download</Link></li>
              <li><Link to="/contact" className="text-foreground/80 hover:text-foreground transition-colors">Contact</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-heading font-semibold mb-4 text-foreground">Connect</h3>
            <div className="flex gap-4">
              <a href="#" className="text-foreground/80 hover:text-foreground transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="text-foreground/80 hover:text-foreground transition-colors">
                <Linkedin className="h-5 w-5" />
              </a>
              <a href="#" className="text-foreground/80 hover:text-foreground transition-colors">
                <Github className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
        
        <div className="border-t border-foreground/20 pt-6 text-center">
          <p className="text-foreground/80 text-sm">
            © 2025 NeuroMate. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
