import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { activitiesAPI } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Loader2 } from "lucide-react";

const moodSchema = z.object({
  mood_level: z.number().min(1).max(5),
  mood_type: z.string().optional(),
  notes: z.string().trim().max(500, "Notes must be less than 500 characters").optional(),
});

type MoodFormData = z.infer<typeof moodSchema>;

interface AddMoodFormProps {
  onSuccess?: () => void;
}

const moodOptions = [
  { value: 1, label: "😢 Very Sad", type: "very_sad" },
  { value: 2, label: "😕 Sad", type: "sad" },
  { value: 3, label: "😐 Neutral", type: "neutral" },
  { value: 4, label: "😊 Happy", type: "happy" },
  { value: 5, label: "😄 Very Happy", type: "very_happy" },
];

export const AddMoodForm = ({ onSuccess }: AddMoodFormProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  const form = useForm<MoodFormData>({
    resolver: zodResolver(moodSchema),
    defaultValues: {
      mood_level: 3,
      mood_type: "neutral",
      notes: "",
    },
  });

  const onSubmit = async (data: MoodFormData) => {
    setIsSubmitting(true);
    try {
      if (!user) {
        toast({
          title: "Error",
          description: "You must be logged in to add mood check-ins",
          variant: "destructive",
        });
        return;
      }

      await activitiesAPI.createMood(data.mood_level, data.mood_type, data.notes);

      toast({
        title: "Success",
        description: "Mood check-in added successfully",
      });

      form.reset();
      onSuccess?.();
    } catch (error) {
      console.error("Error adding mood check-in:", error);
      toast({
        title: "Error",
        description: "Failed to add mood check-in. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="mood_level"
          render={({ field }) => (
            <FormItem className="space-y-3">
              <FormLabel>How are you feeling?</FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={(value) => {
                    const numValue = parseInt(value);
                    field.onChange(numValue);
                    const mood = moodOptions.find(m => m.value === numValue);
                    form.setValue("mood_type", mood?.type || "");
                  }}
                  value={field.value.toString()}
                  className="flex flex-col space-y-2"
                >
                  {moodOptions.map((mood) => (
                    <FormItem
                      key={mood.value}
                      className="flex items-center space-x-3 space-y-0"
                    >
                      <FormControl>
                        <RadioGroupItem value={mood.value.toString()} />
                      </FormControl>
                      <FormLabel className="font-normal text-base cursor-pointer">
                        {mood.label}
                      </FormLabel>
                    </FormItem>
                  ))}
                </RadioGroup>
              </FormControl>
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
                  placeholder="What's on your mind?"
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
            "Add Mood Check-in"
          )}
        </Button>
      </form>
    </Form>
  );
};
