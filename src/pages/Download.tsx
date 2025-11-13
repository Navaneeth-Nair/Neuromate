import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Download as DownloadIcon, MonitorSmartphone, CheckCircle } from "lucide-react";
import { Link } from "react-router-dom";

const Download = () => {
  const systemRequirements = [
    { platform: "Windows", os: "10/11", ram: "4GB+", storage: "1GB", internet: "Optional" },
  ];

  const faqItems = [
    {
      question: "Is NeuroMate free?",
      answer: "NeuroMate offers a free version with core features. Premium features will be available in future updates with a subscription model."
    },
    {
      question: "Does it work offline?",
      answer: "Yes! Most features work offline. However, AI insights and cloud sync require an internet connection."
    },
    {
      question: "Is my data safe?",
      answer: "Absolutely. We use end-to-end encryption and store all data locally on your device. Your privacy is our top priority."
    },
    {
      question: "Can I use it on mobile?",
      answer: "Mobile versions for Android and iOS are currently in development and will be available in 2026."
    },
    {
      question: "How often is it updated?",
      answer: "We release updates monthly with new features, improvements, and bug fixes."
    }
  ];

  return (
    <div className="min-h-screen pt-24">
      {/* Main Download Banner */}
      <section className="py-20 px-6 bg-gradient-hero text-center">
        <div className="container mx-auto max-w-4xl">
          <h1 className="text-5xl md:text-6xl font-heading font-bold mb-6 animate-fade-in">
            Ready to meet your AI Companion?
          </h1>
          <p className="text-2xl text-muted-foreground mb-12 animate-fade-in">
            Download NeuroMate and start your mental wellness journey today
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <Link to="/get-download">
              <Button size="lg" className="bg-gradient-primary hover-glow text-foreground font-heading font-semibold text-lg px-12 py-6 h-auto">
                <DownloadIcon className="mr-3 h-6 w-6" />
                Download for Windows
              </Button>
            </Link>
            <div className="text-muted-foreground">
              <p className="text-sm">Version 1.0.0 • 145 MB</p>
            </div>
          </div>
          
          <p className="mt-8 text-muted-foreground">
            <MonitorSmartphone className="inline h-5 w-5 mr-2" />
            Android & macOS versions coming soon
          </p>
        </div>
      </section>

      {/* System Requirements */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              System Requirements
            </h2>
          </div>
          
          <Card className="glass-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-primary">
                  <tr>
                    <th className="p-4 text-left font-heading">Platform</th>
                    <th className="p-4 text-left font-heading">OS Version</th>
                    <th className="p-4 text-left font-heading">RAM</th>
                    <th className="p-4 text-left font-heading">Storage</th>
                    <th className="p-4 text-left font-heading">Internet</th>
                  </tr>
                </thead>
                <tbody>
                  {systemRequirements.map((req, index) => (
                    <tr key={index} className="border-t border-border">
                      <td className="p-4 font-semibold">{req.platform}</td>
                      <td className="p-4">{req.os}</td>
                      <td className="p-4">{req.ram}</td>
                      <td className="p-4">{req.storage}</td>
                      <td className="p-4">{req.internet}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </section>

      {/* Installation Steps */}
      <section className="py-20 px-6 bg-gradient-hero">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Installation Steps
            </h2>
            <p className="text-xl text-muted-foreground">
              Get started in just 3 simple steps
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Download Installer", desc: "Click the download button and save the installer file" },
              { step: "2", title: "Run Setup", desc: "Double-click the installer and follow the setup wizard" },
              { step: "3", title: "Launch NeuroMate", desc: "Open the app and personalize your AI companion" }
            ].map((item, index) => (
              <Card key={index} className="glass-card p-8 text-center hover-glow">
                <div className="w-16 h-16 rounded-full bg-gradient-primary flex items-center justify-center mx-auto mb-6">
                  <span className="text-2xl font-heading font-bold text-foreground">{item.step}</span>
                </div>
                <h3 className="text-xl font-heading font-semibold mb-3">{item.title}</h3>
                <p className="text-muted-foreground">{item.desc}</p>
                <CheckCircle className="h-8 w-8 text-accent mx-auto mt-4" />
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-4">
              Frequently Asked Questions
            </h2>
          </div>
          
          <Accordion type="single" collapsible className="space-y-4">
            {faqItems.map((item, index) => (
              <AccordionItem key={index} value={`item-${index}`} className="glass-card px-6 rounded-xl border-0">
                <AccordionTrigger className="text-left font-heading font-semibold text-lg hover:text-primary">
                  {item.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  {item.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </section>
    </div>
  );
};

export default Download;
