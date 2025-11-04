import { Card } from "@/components/ui/card";
import { Target, Users, Lightbulb, Shield } from "lucide-react";

const About = () => {
  const team = [
    { name: "Alex Chen", role: "Project Lead", description: "Visionary behind NeuroMate's mission" },
    { name: "Maya Patel", role: "AI Specialist", description: "Leading our machine learning innovations" },
    { name: "Jordan Smith", role: "Developer", description: "Building the core platform" },
    { name: "Sam Rivera", role: "UI Designer", description: "Crafting the calm, beautiful experience" }
  ];

  const values = [
    { icon: Target, title: "Empathy", description: "Understanding your unique mental health journey" },
    { icon: Shield, title: "Privacy", description: "Your data stays yours, always encrypted" },
    { icon: Lightbulb, title: "Innovation", description: "Pushing AI boundaries for human benefit" },
    { icon: Users, title: "Trust", description: "Building relationships, not just software" }
  ];

  return (
    <div className="min-h-screen pt-24">
      {/* Mission Statement */}
      <section className="py-20 px-6 bg-gradient-hero">
        <div className="container mx-auto text-center max-w-4xl">
          <h1 className="text-5xl md:text-6xl font-heading font-bold mb-8 animate-fade-in">
            Our Mission is to Revolutionize Mental Wellness with AI 
          </h1>
          <p className="text-2xl text-muted-foreground leading-relaxed animate-fade-in">
            We believe AI can enhance human mental well-being, not replace it. 
            NeuroMate is your companion on the journey to a healthier mind.
          </p>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Meet Our Team
            </h2>
            <p className="text-xl text-muted-foreground">
              Passionate minds building the future of mental wellness
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member, index) => (
              <Card key={index} className="glass-card p-6 text-center hover-glow">
                <div className="w-24 h-24 rounded-full bg-gradient-primary mx-auto mb-4" />
                <h3 className="text-xl font-heading font-semibold mb-2">{member.name}</h3>
                <p className="text-primary font-semibold mb-2">{member.role}</p>
                <p className="text-muted-foreground text-sm">{member.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Journey Timeline */}
      <section className="py-20 px-6 bg-gradient-hero">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Our Journey
            </h2>
          </div>
          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {[
                { year: "2024", title: "Concept", description: "The idea of an AI mental wellness companion was born" },
                { year: "2025", title: "Prototype", description: "Beta version launched with 100 early adopters" },
                { year: "2026", title: "Launch", description: "Full public release with all five modules" }
              ].map((milestone, index) => (
                <div key={index} className="flex gap-8 items-center">
                  <div className="text-5xl font-heading font-bold gradient-text w-32 text-right">
                    {milestone.year}
                  </div>
                  <div className="flex-1 glass-card p-6 rounded-2xl">
                    <h3 className="text-2xl font-heading font-semibold mb-2">{milestone.title}</h3>
                    <p className="text-muted-foreground">{milestone.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Our Core Values
            </h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <Card key={index} className="glass-card p-8 text-center hover-glow">
                <div className="p-4 rounded-full bg-gradient-primary w-fit mx-auto mb-4">
                  <value.icon className="h-8 w-8 text-foreground" />
                </div>
                <h3 className="text-xl font-heading font-semibold mb-3">{value.title}</h3>
                <p className="text-muted-foreground">{value.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
