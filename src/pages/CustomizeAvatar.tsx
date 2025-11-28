import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const CustomizeAvatar = () => {
  return (
    <div className="container mx-auto px-6 py-24">
      <h1 className="text-4xl font-heading font-bold gradient-text mb-8">Customize Avatar</h1>
      <Card>
        <CardHeader>
          <CardTitle>Avatar Customization</CardTitle>
          <CardDescription>Personalize your profile appearance</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Avatar customization coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default CustomizeAvatar;
