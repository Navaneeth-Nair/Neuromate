import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Calendar, CheckCircle, Heart, Brain, BookOpen, Users, Sparkles, Loader2 } from "lucide-react";
import { useActivityData } from "@/hooks/useActivityData";
import { isSameDay } from "date-fns";

interface Activity {
  type: 'task' | 'mood' | 'focus' | 'journal' | 'routine' | 'meditation';
  title: string;
  time: string;
  date: Date;
}

interface ContributionDay {
  date: Date;
  count: number;
  level: 0 | 1 | 2 | 3 | 4;
  activities: Activity[];
}

const activityTypes = [
  { type: 'task' as const, icon: CheckCircle, label: 'Task Completions', color: 'text-green-500' },
  { type: 'mood' as const, icon: Heart, label: 'Mood Check-ins', color: 'text-pink-500' },
  { type: 'focus' as const, icon: Brain, label: 'Focus Sessions', color: 'text-blue-500' },
  { type: 'journal' as const, icon: BookOpen, label: 'Journal Entries', color: 'text-purple-500' },
  { type: 'routine' as const, icon: Users, label: 'Routines', color: 'text-orange-500' },
  { type: 'meditation' as const, icon: Sparkles, label: 'Meditation Sessions', color: 'text-indigo-500' },
];

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const ContributionCalendar = () => {
  const [selectedYear, setSelectedYear] = useState(2025);
  const [selectedDay, setSelectedDay] = useState<ContributionDay | null>(null);
  
  const { data: activities = [], isLoading } = useActivityData(selectedYear);

  // Generate contribution data from real activities - from Jan 1 to today
  const { contributions, weeks, monthLabels } = useMemo(() => {
    const generateContributionData = (year: number) => {
      // Start from January 1st
      const startDate = new Date(year, 0, 1);

      // End at today's date (or year end if viewing past years)
      const today = new Date();
      const currentYearEnd = new Date(year, 11, 31);
      const endDate = today.getFullYear() === year ? today : currentYearEnd;

      // Calculate the Monday of the week containing January 1st (for grid alignment)
      const janFirst = new Date(year, 0, 1);
      const dayOfWeek = janFirst.getDay(); // 0 = Sunday, 1 = Monday, etc.
      const gridStartDate = new Date(janFirst);
      const daysBack = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // Days to go back to Monday
      gridStartDate.setDate(janFirst.getDate() - daysBack);
      
      // Calculate offset: how many days from grid start to actual Jan 1
      const offsetDays = Math.floor((startDate.getTime() - gridStartDate.getTime()) / (1000 * 60 * 60 * 24));

      const days: ContributionDay[] = [];
      const monthMap = new Map<number, number>(); // Track first week of each month

      let dayCount = 0;
      const currentDate = new Date(startDate);

      // Generate days from start date to today
      while (currentDate <= endDate) {
        // Track first week where this month appears
        const monthKey = currentDate.getMonth();
        const weekIndex = Math.floor(dayCount / 7);
        if (!monthMap.has(monthKey)) {
          monthMap.set(monthKey, weekIndex);
        }

        // Filter activities for this specific date
        const dayActivities: Activity[] = activities.filter(activity =>
          isSameDay(activity.date, currentDate)
        );

        const count = dayActivities.length;

        // Determine level based on count
        let level: 0 | 1 | 2 | 3 | 4 = 0;
        if (count >= 6) level = 4;
        else if (count >= 5) level = 3;
        else if (count >= 3) level = 2;
        else if (count > 0) level = 1;

        days.push({ date: new Date(currentDate), count, level, activities: dayActivities });

        // Move to next day
        currentDate.setDate(currentDate.getDate() + 1);
        dayCount++;
      }

      // Calculate weeks needed
      const totalWeeks = Math.ceil(dayCount / 7);

      // Build month labels with correct alignment
      const months: { label: string; weekIndex: number }[] = [];
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      
      monthMap.forEach((weekIndex, monthIndex) => {
        months.push({
          label: monthNames[monthIndex],
          weekIndex: weekIndex
        });
      });

      return { days, totalWeeks, months };
    };

    const { days, totalWeeks, months } = generateContributionData(selectedYear);
    return {
      contributions: days,
      weeks: totalWeeks,
      monthLabels: months
    };
  }, [selectedYear, activities]);

  const totalContributions = contributions.reduce((sum, day) => sum + day.count, 0);

  const handleDayClick = (day: ContributionDay) => {
    setSelectedDay(day);
  };

  const getLevelColor = (level: number, isSelected: boolean = false) => {
    const baseClasses = 'transition-all duration-200 ease-in-out';
    const selectedClasses = isSelected ? 'ring-2 ring-primary ring-offset-2 ring-offset-background scale-110' : '';
    
    switch (level) {
      case 0: return `bg-muted hover:bg-muted/80 hover:scale-110 ${baseClasses} ${selectedClasses}`;
      case 1: return `bg-primary/20 hover:bg-primary/30 hover:scale-110 ${baseClasses} ${selectedClasses}`;
      case 2: return `bg-primary/40 hover:bg-primary/50 hover:scale-110 ${baseClasses} ${selectedClasses}`;
      case 3: return `bg-primary/60 hover:bg-primary/70 hover:scale-110 ${baseClasses} ${selectedClasses}`;
      case 4: return `bg-primary hover:bg-primary/90 hover:scale-110 ${baseClasses} ${selectedClasses}`;
      default: return `bg-muted ${baseClasses} ${selectedClasses}`;
    }
  };

  return (
    <TooltipProvider>
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex-1">
              <CardTitle className="flex items-center gap-2 text-xl md:text-2xl">
                <Calendar className="w-5 h-5 md:w-6 md:h-6" />
                Your Activity in the Last Year
              </CardTitle>
              <CardDescription className="mt-1">
                Track your productivity and wellbeing habits over time
              </CardDescription>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline" className="text-sm">
                {totalContributions} activities
              </Badge>
              <div className="flex gap-1">
                {[2025, 2024, 2023].map((year) => (
                  <Button
                    key={year}
                    variant={selectedYear === year ? "default" : "outline"}
                    size="sm"
                    onClick={() => {
                      setSelectedYear(year);
                      setSelectedDay(null);
                    }}
                    className="h-8"
                  >
                    {year}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : (
            <div className="space-y-3">
              {/* Month labels - dynamically positioned */}
              <div className="flex gap-[3px] pl-12 text-xs text-muted-foreground h-6">
                {monthLabels.map((month, index) => {
                  const prevWeekIndex = index > 0 ? monthLabels[index - 1].weekIndex : 0;
                  const gapWeeks = month.weekIndex - prevWeekIndex;
                  const gapPixels = gapWeeks * 13; // 10px square + 3px gap
                  
                  return (
                    <div
                      key={month.label}
                      style={{
                        marginLeft: index === 0 ? 0 : `${gapPixels}px`,
                        minWidth: '0'
                      }}
                      className="whitespace-nowrap"
                    >
                      {month.label}
                    </div>
                  );
                })}
              </div>

              {/* Calendar grid */}
              <div className="flex gap-[3px]">
                {/* Day labels - Mon through Sun */}
                <div className="flex flex-col gap-[3px] text-xs text-muted-foreground pr-2 py-1">
                  {WEEKDAY_LABELS.map((day, index) => (
                    <div key={day} className="h-[10px] md:h-[12px] flex items-center">
                      {index % 2 === 0 ? day : ''}
                    </div>
                  ))}
                </div>

                {/* Contribution grid - weeks as columns, days as rows */}
                <div className="flex gap-[3px] overflow-x-auto pb-2 scrollbar-thin">
                  {Array.from({ length: weeks }).map((_, weekIndex) => (
                    <div key={weekIndex} className="flex flex-col gap-[3px] flex-shrink-0">
                      {Array.from({ length: 7 }).map((_, dayIndex) => {
                        const contributionIndex = weekIndex * 7 + dayIndex;
                        const contribution = contributions[contributionIndex];
                        
                        const isSelected = selectedDay?.date.toDateString() === contribution?.date.toDateString();
                        
                        return (
                          <Tooltip key={`${weekIndex}-${dayIndex}`}>
                            <TooltipTrigger asChild>
                              <button
                                className={`w-[10px] h-[10px] md:w-[12px] md:h-[12px] rounded-[2px] cursor-pointer ${
                                  contribution
                                    ? getLevelColor(contribution.level, isSelected)
                                    : 'bg-transparent'
                                }`}
                                onClick={() => contribution && handleDayClick(contribution)}
                                aria-label={
                                  contribution
                                    ? `${contribution.date.toLocaleDateString()}: ${contribution.count} activities`
                                    : 'No data'
                                }
                              />
                            </TooltipTrigger>
                            {contribution && (
                              <TooltipContent side="top" className="max-w-xs">
                                <div className="space-y-1">
                                  <p className="font-semibold">{contribution.date.toLocaleDateString('en-US', {
                                    weekday: 'short',
                                    month: 'short',
                                    day: 'numeric',
                                    year: 'numeric'
                                  })}</p>
                                  <p className="text-sm text-muted-foreground">
                                    {contribution.count === 0 ? 'No activities' : `${contribution.count} ${contribution.count === 1 ? 'activity' : 'activities'}`}
                                  </p>
                                  {contribution.activities.length > 0 && (
                                    <div className="text-xs text-muted-foreground mt-1">
                                      Click to view details
                                    </div>
                                  )}
                                </div>
                              </TooltipContent>
                            )}
                          </Tooltip>
                        );
                      })}
                    </div>
                  ))}
                </div>
              </div>

              {/* Legend */}
              <div className="flex items-center justify-end gap-2 text-xs text-muted-foreground pt-2">
                <span>Less</span>
                <div className="flex gap-[3px]">
                  <div className="w-[10px] h-[10px] md:w-[12px] md:h-[12px] rounded-[2px] bg-muted" />
                  <div className="w-[10px] h-[10px] md:w-[12px] md:h-[12px] rounded-[2px] bg-primary/20" />
                  <div className="w-[10px] h-[10px] md:w-[12px] md:h-[12px] rounded-[2px] bg-primary/40" />
                  <div className="w-[10px] h-[10px] md:w-[12px] md:h-[12px] rounded-[2px] bg-primary/60" />
                  <div className="w-[10px] h-[10px] md:w-[12px] md:h-[12px] rounded-[2px] bg-primary" />
                </div>
                <span>More</span>
              </div>

              {/* Selected Day Activities */}
              {selectedDay && selectedDay.activities.length > 0 && (
                <div className="mt-6 pt-6 border-t">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Contribution Activity on {selectedDay.date.toLocaleDateString('en-US', {
                      weekday: 'long',
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </h3>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {selectedDay.activities.map((activity, index) => {
                      const activityType = activityTypes.find(t => t.type === activity.type);
                      const Icon = activityType?.icon || CheckCircle;

                      return (
                        <div
                          key={index}
                          className="flex items-start gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                        >
                          <div className={`mt-0.5 ${activityType?.color || 'text-primary'}`}>
                            <Icon className="w-5 h-5" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm truncate">{activity.title}</p>
                            <p className="text-xs text-muted-foreground mt-0.5">{activity.time}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </TooltipProvider>
  );
};

export default ContributionCalendar;
