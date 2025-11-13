import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import FeatureCard from "@/components/FeatureCard";
import { Heart, Focus, BookOpen, TrendingUp, Activity } from "lucide-react";
import heroImage from "@/assets/hero-ai-companion.jpg";

const Home = () => {
  const features = [
    {
      icon: Heart,
      title: "Mood Tracker",
      description: "Monitor your emotional patterns with AI insights"
    },
    {
      icon: Focus,
      title: "Focus Enhancer",
      description: "Boost productivity with personalized focus sessions"
    },
    {
      icon: BookOpen,
      title: "Guided Reflection",
      description: "Daily prompts for mindfulness and self-awareness"
    },
    {
      icon: TrendingUp,
      title: "Growth Journal",
      description: "Track your personal development journey"
    },
    {
      icon: Activity,
      title: "Wellness Analytics",
      description: "Visualize your mental health progress over time"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6 bg-gradient-hero">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-8 animate-fade-in">
              <h1 className="text-5xl md:text-6xl font-heading font-bold leading-tight">
                Your AI Companion for a{" "}
                <span className="gradient-text">Calmer, More Focused</span> You
              </h1>
              <p className="text-xl text-muted-foreground leading-relaxed">
                NeuroMate helps you manage stress, boost focus, and grow emotionally — powered by AI.
              </p>
              <div className="flex flex-wrap gap-4">
                <Link to="/download">
                  <Button size="lg" className="bg-gradient-primary hover-glow text-foreground font-heading font-semibold">
                    Download Now
                  </Button>
                </Link>
                <Link to="/features">
                  <Button size="lg" variant="outline" className="font-heading font-semibold border-primary text-primary hover:bg-primary/10">
                    Explore Features
                  </Button>
                </Link>
              </div>
            </div>
            <div className="animate-float">
              <img 
                src={heroImage} 
                alt="AI Companion Illustration" 
                className="rounded-3xl shadow-card w-full"
                fetchPriority="high"
                width={1920}
                height={1080}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Preview */}
      <section className="py-20 px-6">
        <div className="container mx-auto">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Five Intelligent Modules
            </h2>
            <p className="text-xl text-muted-foreground">
              One companion to support every aspect of your mental well-being
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="animate-scale-in" style={{ animationDelay: `${index * 0.1}s` }}>
                <FeatureCard {...feature} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 bg-gradient-hero">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Loved by Early Users
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                quote: "NeuroMate has high pontential to revolutionize mental health support.",
                author: "Jayeed Tamboli",
                role: "AIML Engineer"
              },
              {
                quote: "The focus sessions can transform my productivity.",
                author: "Shahid Shaikh",
                role: "Engineering Student"
              },
              {
                quote: "Finally a tool is being made that understands my mental health journey.",
                author: "Abhi Kore",
                role: "Freelancer"
              }
            ].map((testimonial, index) => (
              <div key={index} className="glass-card p-8 rounded-2xl">
                <p className="text-lg italic mb-4 text-foreground/90">"{testimonial.quote}"</p>
                <div>
                  <p className="font-heading font-semibold text-foreground">{testimonial.author}</p>
                  <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              How It Works
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-12">
            {[
              { step: "01", title: "Download & Setup", desc: "Get started in under 2 minutes" },
              { step: "02", title: "Personalize", desc: "Tailor your AI companion to your needs" },
              { step: "03", title: "Daily Guidance", desc: "Receive insights and support every day" }
            ].map((item, index) => (
              <div key={index} className="text-center space-y-4">
                <div className="text-6xl font-heading font-bold gradient-text">{item.step}</div>
                <h3 className="text-2xl font-heading font-semibold">{item.title}</h3>
                <p className="text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-gradient-primary">
        <div className="container mx-auto text-center space-y-8">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-foreground">
            Start your journey to a better mind with NeuroMate
          </h2>
          <Link to="/download">
            <Button size="lg" variant="outline" className="bg-background hover:bg-background/90 border-none text-foreground font-heading font-semibold text-lg px-8">
              Download for Windows
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
