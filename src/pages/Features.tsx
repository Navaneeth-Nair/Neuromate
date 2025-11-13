import { Card } from "@/components/ui/card";
import { Heart, Focus, BookOpen, TrendingUp, Activity, Check, X } from "lucide-react";

const Features = () => {
  const modules = [
    {
      icon: Heart,
      name: "Mood Tracker",
      description: "Track your emotions with intelligent pattern recognition. NeuroMate analyzes your mood over time and provides personalized insights to help you understand what affects your emotional well-being.",
      benefits: "Identify triggers, celebrate improvements, and gain self-awareness"
    },
    {
      icon: Focus,
      name: "Focus Enhancer",
      description: "Personalized focus sessions tailored to your work style. Using AI-driven techniques, NeuroMate helps you enter deep work states and maintain concentration for longer periods.",
      benefits: "Boost productivity, reduce distractions, achieve flow state"
    },
    {
      icon: BookOpen,
      name: "Guided Reflection",
      description: "Daily prompts and journaling exercises designed to foster mindfulness and self-discovery. Let NeuroMate guide you through meaningful introspection.",
      benefits: "Build mindfulness habits, process emotions, gain clarity"
    },
    {
      icon: TrendingUp,
      name: "Growth Journal",
      description: "Document your personal development journey with structured entries and AI feedback. Track goals, celebrate wins, and learn from challenges.",
      benefits: "Set meaningful goals, track progress, build confidence"
    },
    {
      icon: Activity,
      name: "Wellness Analytics",
      description: "Visualize your mental health journey through beautiful, insightful charts and reports. See patterns, trends, and correlations you might have missed.",
      benefits: "Data-driven insights, visual progress tracking, informed decisions"
    }
  ];

  const comparison = [
    { feature: "AI-Powered Insights", neuromate: true, others: false },
    { feature: "All-in-One Platform", neuromate: true, others: false },
    { feature: "Privacy-First Design", neuromate: true, others: true },
    { feature: "Offline Mode", neuromate: true, others: false },
    { feature: "Customizable Modules", neuromate: true, others: false },
    { feature: "Scientific Backing", neuromate: true, others: true },
  ];

  return (
    <div className="min-h-screen pt-24">
      {/* Intro Header */}
      <section className="py-20 px-6 bg-gradient-hero text-center">
        <div className="container mx-auto max-w-4xl">
          <h1 className="text-5xl md:text-6xl font-heading font-bold mb-6 animate-fade-in">
            Five Intelligent Modules
          </h1>
          <p className="text-2xl text-muted-foreground animate-fade-in">
            One companion to support every aspect of your mental well-being
          </p>
        </div>
      </section>

      {/* Modules Display */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-6xl space-y-16">
          {modules.map((module, index) => (
            <div 
              key={index} 
              className={`grid md:grid-cols-2 gap-12 items-center ${index % 2 === 1 ? 'md:flex-row-reverse' : ''}`}
            >
              <Card className="glass-card p-12 hover-glow">
                <div className="p-6 rounded-full bg-gradient-primary w-fit mb-6">
                  <module.icon className="h-12 w-12 text-foreground" />
                </div>
                <h2 className="text-3xl font-heading font-bold mb-4">{module.name}</h2>
                <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
                  {module.description}
                </p>
                <div className="bg-accent/10 p-4 rounded-xl border border-accent/20">
                  <p className="text-black font-semibold">
                    ✨ {module.benefits}
                  </p>
                </div>
              </Card>
              
              <div className="h-80 bg-gradient-primary rounded-3xl shadow-card flex items-center justify-center">
                <module.icon className="h-32 w-32 text-foreground/30" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Demo Video Placeholder */}
      <section className="py-20 px-6 bg-gradient-hero">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-heading font-bold mb-8">
            See NeuroMate in Action
          </h2>
          <div className="aspect-video bg-gradient-primary rounded-3xl shadow-card flex items-center justify-center">
            <p className="text-2xl font-heading text-foreground/80">Demo Video Coming Soon</p>
          </div>
          <p className="mt-6 text-lg text-muted-foreground">
            A glimpse of how NeuroMate guides you daily
          </p>
        </div>
      </section>

      {/* Comparison Grid */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Why Choose NeuroMate?
            </h2>
            <p className="text-xl text-muted-foreground">
              See how we compare to other mental wellness apps
            </p>
          </div>
          
          <Card className="glass-card overflow-hidden">
            <table className="w-full">
              <thead className="bg-gradient-primary">
                <tr>
                  <th className="p-6 text-left font-heading text-lg">Feature</th>
                  <th className="p-6 text-center font-heading text-lg">NeuroMate</th>
                  <th className="p-6 text-center font-heading text-lg">Others</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((row, index) => (
                  <tr key={index} className="border-t border-border">
                    <td className="p-6 font-semibold">{row.feature}</td>
                    <td className="p-6 text-center">
                      {row.neuromate ? (
                        <Check className="h-6 w-6 text-accent mx-auto" />
                      ) : (
                        <X className="h-6 w-6 text-muted-foreground mx-auto" />
                      )}
                    </td>
                    <td className="p-6 text-center">
                      {row.others ? (
                        <Check className="h-6 w-6 text-accent mx-auto" />
                      ) : (
                        <X className="h-6 w-6 text-muted-foreground mx-auto" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default Features;
