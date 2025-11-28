import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { activitiesAPI } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Loader2 } from "lucide-react";

const meditationSchema = z.object({
  type: z.string().min(1, "Meditation type is required"),
  duration_minutes: z.number().min(1, "Duration must be at least 1 minute").max(180, "Duration cannot exceed 3 hours"),
  notes: z.string().trim().max(500, "Notes must be less than 500 characters").optional(),
});

type MeditationFormData = z.infer<typeof meditationSchema>;

interface AddMeditationFormProps {
  onSuccess?: () => void;
}

const meditationTypes = [
  "Mindfulness",
  "Guided",
  "Breathing",
  "Body Scan",
  "Loving-Kindness",
  "Visualization",
  "Transcendental",
  "Movement",
  "Other",
];

export const AddMeditationForm = ({ onSuccess }: AddMeditationFormProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  const form = useForm<MeditationFormData>({
    resolver: zodResolver(meditationSchema),
    defaultValues: {
      type: "",
      duration_minutes: 10,
      notes: "",
    },
  });

  const onSubmit = async (data: MeditationFormData) => {
    setIsSubmitting(true);
    try {
      if (!user) {
        toast({
          title: "Error",
          description: "You must be logged in to add meditation sessions",
          variant: "destructive",
        });
        return;
      }

      await activitiesAPI.createMeditation(data.type, data.duration_minutes, data.notes);

      toast({
        title: "Success",
        description: "Meditation session added successfully",
      });

      form.reset();
      onSuccess?.();
    } catch (error) {
      console.error("Error adding meditation session:", error);
      toast({
        title: "Error",
        description: "Failed to add meditation session. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Meditation Type</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select meditation type" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {meditationTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="duration_minutes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Duration (minutes)</FormLabel>
              <FormControl>
                <Input 
                  type="number" 
                  min="1"
                  max="180"
                  placeholder="10"
                  {...field}
                  onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                />
              </FormControl>
              <FormDescription>
                How long did you meditate? (1-180 minutes)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Notes (Optional)</FormLabel>
              <FormControl>
                <Textarea 
                  placeholder="Reflect on your session..."
                  className="resize-none"
                  rows={3}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Adding...
            </>
          ) : (
            "Add Meditation Session"
          )}
        </Button>
      </form>
    </Form>
  );
};
