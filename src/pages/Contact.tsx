import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Mail, Linkedin, Twitter, Github, Send, Users } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

const Contact = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: ""
  });

  const [betaFormData, setBetaFormData] = useState({
    name: "",
    email: "",
    phone: ""
  });

  const [isSubmittingBeta, setIsSubmittingBeta] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.name || !formData.email || !formData.message) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields",
        variant: "destructive"
      });
      return;
    }

    // Simulate form submission
    toast({
      title: "Message Sent!",
      description: "Thank you! We'll reply soon.",
    });
    
    // Reset form
    setFormData({ name: "", email: "", message: "" });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleBetaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBetaFormData({
      ...betaFormData,
      [e.target.name]: e.target.value
    });
  };

  const handleBetaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!betaFormData.name || !betaFormData.email || !betaFormData.phone) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields",
        variant: "destructive"
      });
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(betaFormData.email)) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address",
        variant: "destructive"
      });
      return;
    }

    setIsSubmittingBeta(true);

    try {
      const { error } = await supabase
        .from('beta_signups')
        .insert([
          {
            name: betaFormData.name.trim(),
            email: betaFormData.email.trim(),
            phone: betaFormData.phone.trim()
          }
        ]);

      if (error) throw error;

      toast({
        title: "Welcome to Beta!",
        description: "Thank you for signing up! We'll be in touch soon.",
      });
      
      // Reset form
      setBetaFormData({ name: "", email: "", phone: "" });
    } catch (error: any) {
      console.error('Beta signup error:', error);
      toast({
        title: "Submission Failed",
        description: "There was an error submitting your request. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmittingBeta(false);
    }
  };

  return (
    <div className="min-h-screen pt-24">
      {/* Header */}
      <section className="py-20 px-6 bg-gradient-hero text-center">
        <div className="container mx-auto max-w-4xl">
          <h1 className="text-5xl md:text-6xl font-heading font-bold mb-6 animate-fade-in">
            We'd love to hear from you
          </h1>
          <p className="text-2xl text-muted-foreground animate-fade-in">
            Reach out for feedback, questions, or collaborations
          </p>
        </div>
      </section>

      <section className="py-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12">
            {/* Contact Form */}
            <Card className="glass-card p-8">
              <h2 className="text-3xl font-heading font-bold mb-6">Send us a message</h2>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-semibold mb-2">
                    Name
                  </label>
                  <Input
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Your name"
                    className="glass-card"
                  />
                </div>
                
                <div>
                  <label htmlFor="email" className="block text-sm font-semibold mb-2">
                    Email
                  </label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="your@email.com"
                    className="glass-card"
                  />
                </div>
                
                <div>
                  <label htmlFor="message" className="block text-sm font-semibold mb-2">
                    Message
                  </label>
                  <Textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    placeholder="Tell us what's on your mind..."
                    rows={6}
                    className="glass-card resize-none"
                  />
                </div>
                
                <Button 
                  type="submit" 
                  size="lg" 
                  className="w-full bg-gradient-primary hover-glow text-foreground font-heading font-semibold"
                >
                  <Send className="mr-2 h-5 w-5" />
                  Send Message
                </Button>
              </form>
            </Card>

            {/* Contact Info */}
            <div className="space-y-8">
              <Card className="glass-card p-8 hover-glow">
                <Mail className="h-8 w-8 text-primary mb-4" />
                <h3 className="text-xl font-heading font-semibold mb-2">Email</h3>
                <a href="mailto:support@neuromate.ai" className="text-muted-foreground hover:text-primary transition-colors">
                  support@neuromate.ai
                </a>
              </Card>

              <Card className="glass-card p-8">
                <h3 className="text-xl font-heading font-semibold mb-4">Connect with us</h3>
                <div className="flex gap-4">
                  <a 
                    href="#" 
                    className="p-3 rounded-full bg-gradient-primary hover-glow transition-all"
                    aria-label="Twitter"
                  >
                    <Twitter className="h-6 w-6 text-foreground" />
                  </a>
                  <a 
                    href="#" 
                    className="p-3 rounded-full bg-gradient-primary hover-glow transition-all"
                    aria-label="LinkedIn"
                  >
                    <Linkedin className="h-6 w-6 text-foreground" />
                  </a>
                  <a 
                    href="#" 
                    className="p-3 rounded-full bg-gradient-primary hover-glow transition-all"
                    aria-label="GitHub"
                  >
                    <Github className="h-6 w-6 text-foreground" />
                  </a>
                </div>
              </Card>

              <Card className="glass-card p-8 bg-gradient-hero">
                <h3 className="text-xl font-heading font-semibold mb-4">Office Hours</h3>
                <p className="text-muted-foreground">Monday - Friday</p>
                <p className="text-muted-foreground">9:00 AM - 6:00 PM (PST)</p>
                <p className="text-sm text-muted-foreground mt-4">
                  We typically respond within 24 hours
                </p>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Beta Testing Signup Section */}
      <section className="py-20 px-6 bg-gradient-hero">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-12">
            <Users className="h-16 w-16 text-primary mx-auto mb-4" />
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Join Our Beta Testing Program
            </h2>
            <p className="text-xl text-muted-foreground">
              Be among the first to experience NeuroMate and help shape its future
            </p>
          </div>

          <Card className="glass-card p-8 max-w-2xl mx-auto">
            <form onSubmit={handleBetaSubmit} className="space-y-6">
              <div>
                <label htmlFor="beta-name" className="block text-sm font-semibold mb-2">
                  Full Name
                </label>
                <Input
                  id="beta-name"
                  name="name"
                  value={betaFormData.name}
                  onChange={handleBetaChange}
                  placeholder="John Doe"
                  className="glass-card"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="beta-email" className="block text-sm font-semibold mb-2">
                  Email Address
                </label>
                <Input
                  id="beta-email"
                  name="email"
                  type="email"
                  value={betaFormData.email}
                  onChange={handleBetaChange}
                  placeholder="john@example.com"
                  className="glass-card"
                  required
                />
              </div>

              <div>
                <label htmlFor="beta-phone" className="block text-sm font-semibold mb-2">
                  Phone Number
                </label>
                <Input
                  id="beta-phone"
                  name="phone"
                  type="tel"
                  value={betaFormData.phone}
                  onChange={handleBetaChange}
                  placeholder="+1 (555) 123-4567"
                  className="glass-card"
                  required
                />
              </div>
              
              <Button 
                type="submit" 
                size="lg" 
                className="w-full bg-gradient-primary hover-glow text-foreground font-heading font-semibold"
                disabled={isSubmittingBeta}
              >
                <Users className="mr-2 h-5 w-5" />
                {isSubmittingBeta ? "Submitting..." : "Request Beta Access"}
              </Button>
            </form>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default Contact;
