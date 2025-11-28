import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const Productivity = () => {
  return (
    <div className="container mx-auto px-6 py-24">
      <h1 className="text-4xl font-heading font-bold gradient-text mb-8">Productivity Tools</h1>
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Task Manager</CardTitle>
            <CardDescription>Organize your daily tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Coming soon...</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Focus Timer</CardTitle>
            <CardDescription>Pomodoro technique timer</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Coming soon...</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Productivity;
