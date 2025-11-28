import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";

const Pricing = () => {
  const plans = [
    {
      name: "Free",
      price: "$0",
      description: "Perfect for getting started",
      features: [
        "Basic AI companion",
        "Community access",
        "Daily mood tracking",
        "Basic analytics",
      ],
    },
    {
      name: "Premium",
      price: "$9.99",
      period: "/month",
      description: "For serious productivity",
      features: [
        "Advanced AI companion",
        "Unlimited focus sessions",
        "Advanced analytics",
        "Priority support",
        "Custom themes",
        "Export data",
      ],
      popular: true,
    },
  ];

  return (
    <div className="container mx-auto px-6 py-24">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-heading font-bold gradient-text mb-4">Pricing Plans</h1>
        <p className="text-muted-foreground text-lg">Choose the plan that's right for you</p>
      </div>
      
      <div className="grid gap-8 md:grid-cols-2 max-w-4xl mx-auto">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.popular ? "border-primary shadow-lg" : ""}>
            <CardHeader>
              {plan.popular && (
                <div className="text-sm font-semibold text-primary mb-2">MOST POPULAR</div>
              )}
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
              <div className="mt-4">
                <span className="text-4xl font-bold">{plan.price}</span>
                {plan.period && <span className="text-muted-foreground">{plan.period}</span>}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-primary flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Button 
                className={plan.popular ? "w-full bg-gradient-primary hover-glow" : "w-full"} 
                variant={plan.popular ? "default" : "outline"}
              >
                {plan.name === "Free" ? "Get Started" : "Upgrade Now"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Pricing;
