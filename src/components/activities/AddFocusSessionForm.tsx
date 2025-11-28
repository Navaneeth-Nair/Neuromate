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
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Loader2 } from "lucide-react";

const focusSessionSchema = z.object({
  activity: z.string().trim().min(1, "Activity is required").max(200, "Activity must be less than 200 characters"),
  duration_minutes: z.number().min(1, "Duration must be at least 1 minute").max(480, "Duration cannot exceed 8 hours"),
  notes: z.string().trim().max(500, "Notes must be less than 500 characters").optional(),
});

type FocusSessionFormData = z.infer<typeof focusSessionSchema>;

interface AddFocusSessionFormProps {
  onSuccess?: () => void;
}

export const AddFocusSessionForm = ({ onSuccess }: AddFocusSessionFormProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  const form = useForm<FocusSessionFormData>({
    resolver: zodResolver(focusSessionSchema),
    defaultValues: {
      activity: "",
      duration_minutes: 25,
      notes: "",
    },
  });

  const onSubmit = async (data: FocusSessionFormData) => {
    setIsSubmitting(true);
    try {
      if (!user) {
        toast({
          title: "Error",
          description: "You must be logged in to add focus sessions",
          variant: "destructive",
        });
        return;
      }

      await activitiesAPI.createFocusSession(data.activity, data.duration_minutes, data.notes);

      toast({
        title: "Success",
        description: "Focus session added successfully",
      });

      form.reset();
      onSuccess?.();
    } catch (error) {
      console.error("Error adding focus session:", error);
      toast({
        title: "Error",
        description: "Failed to add focus session. Please try again.",
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
          name="activity"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Activity</FormLabel>
              <FormControl>
                <Input placeholder="What did you focus on?" {...field} />
              </FormControl>
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
                  max="480"
                  placeholder="25"
                  {...field}
                  onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                />
              </FormControl>
              <FormDescription>
                How long did you focus? (1-480 minutes)
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
                  placeholder="Add any notes about this session..."
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
            "Add Focus Session"
          )}
        </Button>
      </form>
    </Form>
  );
};
