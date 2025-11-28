import { useQuery } from "@tanstack/react-query";
import { activitiesAPI } from "@/lib/api";
import { startOfYear, endOfYear } from "date-fns";

interface Activity {
  type: 'task' | 'mood' | 'focus' | 'journal' | 'routine' | 'meditation';
  title: string;
  time: string;
  date: Date;
}

export const useActivityData = (year: number) => {
  return useQuery({
    queryKey: ["activities", year],
    queryFn: async () => {
      const yearStart = startOfYear(new Date(year, 0, 1));
      const yearEnd = endOfYear(new Date(year, 0, 1));

      // Fetch all activity types in parallel
      const [tasks, moods, focusSessions, journals, routines, meditations] = await Promise.all([
        activitiesAPI.get('tasks', yearStart.toISOString(), yearEnd.toISOString()).catch(() => []),
        activitiesAPI.get('moods', yearStart.toISOString(), yearEnd.toISOString()).catch(() => []),
        activitiesAPI.get('focus', yearStart.toISOString(), yearEnd.toISOString()).catch(() => []),
        activitiesAPI.get('journals', yearStart.toISOString(), yearEnd.toISOString()).catch(() => []),
        activitiesAPI.get('routines', yearStart.toISOString(), yearEnd.toISOString()).catch(() => []),
        activitiesAPI.get('meditations', yearStart.toISOString(), yearEnd.toISOString()).catch(() => []),
      ]);

      const activities: Activity[] = [];

      // Process tasks (filter completed ones)
      tasks
        .filter((task: any) => task.completed && task.completed_at)
        .forEach((task: any) => {
          activities.push({
            type: 'task',
            title: task.title,
            time: new Date(task.completed_at).toLocaleTimeString('en-US', { 
              hour: 'numeric', 
              minute: '2-digit', 
              hour12: true 
            }),
            date: new Date(task.completed_at),
          });
        });

      // Process mood check-ins
      moods.forEach((mood: any) => {
        const moodLabels = ['😢 Very Sad', '😕 Sad', '😐 Neutral', '😊 Happy', '😄 Very Happy'];
        activities.push({
          type: 'mood',
          title: `Mood: ${moodLabels[mood.mood_level - 1] || 'Unknown'}`,
          time: new Date(mood.created_at).toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit', 
            hour12: true 
          }),
          date: new Date(mood.created_at),
        });
      });

      // Process focus sessions
      focusSessions.forEach((session: any) => {
        activities.push({
          type: 'focus',
          title: `Focus: ${session.activity} (${session.duration_minutes}m)`,
          time: new Date(session.started_at).toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit', 
            hour12: true 
          }),
          date: new Date(session.started_at),
        });
      });

      // Process journal entries
      journals.forEach((journal: any) => {
        activities.push({
          type: 'journal',
          title: journal.title,
          time: new Date(journal.created_at).toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit', 
            hour12: true 
          }),
          date: new Date(journal.created_at),
        });
      });

      // Process routines (filter completed ones)
      routines
        .filter((routine: any) => routine.completed && routine.completed_at)
        .forEach((routine: any) => {
          activities.push({
            type: 'routine',
            title: routine.name,
            time: new Date(routine.completed_at).toLocaleTimeString('en-US', { 
              hour: 'numeric', 
              minute: '2-digit', 
              hour12: true 
            }),
            date: new Date(routine.completed_at),
          });
        });

      // Process meditation sessions
      meditations.forEach((meditation: any) => {
        activities.push({
          type: 'meditation',
          title: `${meditation.type} meditation (${meditation.duration_minutes}m)`,
          time: new Date(meditation.started_at).toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit', 
            hour12: true 
          }),
          date: new Date(meditation.started_at),
        });
      });

      return activities;
    },
    enabled: true,
  });
};
