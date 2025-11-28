import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Power } from "lucide-react";
import { toast } from "sonner";

const KillSwitch = () => {
  const [isPaused, setIsPaused] = useState(false);

  const toggleKillSwitch = () => {
    setIsPaused(!isPaused);
    if (!isPaused) {
      toast.success("NeuroMate is paused. Take your time.");
    } else {
      toast.success("NeuroMate is active again. Welcome back!");
    }
  };

  return (
    <div className="container mx-auto px-6 py-24 max-w-2xl">
      <h1 className="text-4xl font-heading font-bold gradient-text mb-8 text-center">Kill Switch</h1>
      
      <Card className="text-center">
        <CardHeader>
          <CardTitle>Wellbeing Safety Feature</CardTitle>
          <CardDescription>
            Sometimes you need a break. This feature disables all AI interactions and notifications.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className={`p-8 rounded-lg ${isPaused ? 'bg-destructive/10' : 'bg-muted'}`}>
            <Power className={`h-16 w-16 mx-auto mb-4 ${isPaused ? 'text-destructive' : 'text-muted-foreground'}`} />
            <p className="text-xl font-semibold mb-2">
              {isPaused ? "NeuroMate is Paused" : "NeuroMate is Active"}
            </p>
            <p className="text-muted-foreground">
              {isPaused 
                ? "All AI interactions and notifications are disabled. Resume whenever you're ready." 
                : "All features are currently active and available."}
            </p>
          </div>
          
          <Button
            size="lg"
            variant={isPaused ? "default" : "destructive"}
            onClick={toggleKillSwitch}
            className="w-full"
          >
            {isPaused ? "Resume NeuroMate" : "Pause NeuroMate"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default KillSwitch;
