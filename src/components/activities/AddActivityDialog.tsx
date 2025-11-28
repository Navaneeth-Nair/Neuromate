import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AddTaskForm } from "./AddTaskForm";
import { AddMoodForm } from "./AddMoodForm";
import { AddFocusSessionForm } from "./AddFocusSessionForm";
import { AddJournalForm } from "./AddJournalForm";
import { AddRoutineForm } from "./AddRoutineForm";
import { AddMeditationForm } from "./AddMeditationForm";
import { useQueryClient } from "@tanstack/react-query";

export const AddActivityDialog = () => {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState("task");

  const handleSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ["activities"] });
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="lg" className="gap-2">
          <Plus className="w-5 h-5" />
          Add Activity
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Activity</DialogTitle>
          <DialogDescription>
            Track your daily activities to build better habits and see your progress
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6">
            <TabsTrigger value="task">Task</TabsTrigger>
            <TabsTrigger value="mood">Mood</TabsTrigger>
            <TabsTrigger value="focus">Focus</TabsTrigger>
            <TabsTrigger value="journal">Journal</TabsTrigger>
            <TabsTrigger value="routine">Routine</TabsTrigger>
            <TabsTrigger value="meditation">Meditation</TabsTrigger>
          </TabsList>

          <TabsContent value="task" className="mt-6">
            <AddTaskForm onSuccess={handleSuccess} />
          </TabsContent>

          <TabsContent value="mood" className="mt-6">
            <AddMoodForm onSuccess={handleSuccess} />
          </TabsContent>

          <TabsContent value="focus" className="mt-6">
            <AddFocusSessionForm onSuccess={handleSuccess} />
          </TabsContent>

          <TabsContent value="journal" className="mt-6">
            <AddJournalForm onSuccess={handleSuccess} />
          </TabsContent>

          <TabsContent value="routine" className="mt-6">
            <AddRoutineForm onSuccess={handleSuccess} />
          </TabsContent>

          <TabsContent value="meditation" className="mt-6">
            <AddMeditationForm onSuccess={handleSuccess} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
