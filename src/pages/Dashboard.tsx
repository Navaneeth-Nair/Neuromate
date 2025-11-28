import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Clock, Flame, TrendingUp, Brain, Heart, Target, Calendar, Sparkles, ListChecks } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from "recharts";
import ContributionCalendar from "@/components/ContributionCalendar";
import { AddActivityDialog } from "@/components/activities/AddActivityDialog";
import { useActivityData } from "@/hooks/useActivityData";

const Dashboard = () => {
  const { data: activities, isLoading } = useActivityData(new Date().getFullYear());

  // Mock data for charts (keeping these for now as they require more complex aggregation)
  const taskCompletionData = [
    { day: "Mon", completed: 8, pending: 2 },
    { day: "Tue", completed: 6, pending: 4 },
    { day: "Wed", completed: 9, pending: 1 },
    { day: "Thu", completed: 7, pending: 3 },
    { day: "Fri", completed: 10, pending: 2 },
    { day: "Sat", completed: 5, pending: 1 },
    { day: "Sun", completed: 4, pending: 2 },
  ];

  const moodTrendData = [
    { day: "Mon", mood: 7 },
    { day: "Tue", mood: 6 },
    { day: "Wed", mood: 8 },
    { day: "Thu", mood: 5 },
    { day: "Fri", mood: 9 },
    { day: "Sat", mood: 8 },
    { day: "Sun", mood: 7 },
  ];

  const categoryData = [
    { name: "Study", value: 35, color: "hsl(258 100% 83%)" }, // Primary purple
    { name: "Coding", value: 30, color: "hsl(258 80% 70%)" }, // Darker purple
    { name: "Fitness", value: 20, color: "hsl(258 70% 75%)" }, // Medium purple
    { name: "Personal", value: 15, color: "hsl(258 60% 80%)" }, // Light purple
  ];

  const recentActivities = activities?.slice(0, 5) || [];

  return (
    <div className="container mx-auto px-6 py-24 space-y-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-4xl font-heading font-bold gradient-text">Dashboard</h1>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="text-sm">Last updated: Just now</Badge>
          <AddActivityDialog />
        </div>
      </div>

      {/* 1️⃣ DAILY SNAPSHOT - Top Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-primary" />
          Today's Snapshot
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Tasks Today
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">8/10</div>
              <p className="text-xs text-muted-foreground mt-1">80% completed</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Heart className="w-4 h-4" />
                Mood Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">😊</div>
              <p className="text-xs text-muted-foreground mt-1">Happy & Focused</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-purple-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Brain className="w-4 h-4" />
                Productivity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">82</div>
              <p className="text-xs text-muted-foreground mt-1">Above average</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-orange-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Focus Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">3h 20m</div>
              <p className="text-xs text-muted-foreground mt-1">12 interruptions</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-red-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Flame className="w-4 h-4" />
                Current Streak
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">7 days</div>
              <p className="text-xs text-muted-foreground mt-1">Keep it up!</p>
            </CardContent>
          </Card>
        </div>
      </section>

      <Separator />

      {/* 2️⃣ ANALYTICS MODULES - Middle Section */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold flex items-center gap-2">
          <Target className="w-6 h-6 text-primary" />
          Analytics & Insights
        </h2>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Module A - Productivity Analytics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ListChecks className="w-5 h-5" />
                Productivity Analytics
              </CardTitle>
              <CardDescription>Your task completion trends this week</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ChartContainer
                config={{
                  completed: { label: "Completed", color: "hsl(var(--primary))" },
                  pending: { label: "Pending", color: "hsl(var(--muted))" },
                }}
                className="h-[250px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={taskCompletionData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis dataKey="day" className="text-xs" />
                    <YAxis className="text-xs" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="completed" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="pending" fill="hsl(var(--muted))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Weekly Completion Rate</span>
                  <span className="font-semibold">78%</span>
                </div>
                <Progress value={78} className="h-2" />
              </div>
            </CardContent>
          </Card>

          {/* Module B - Mood & Wellbeing Analytics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="w-5 h-5" />
                Mood & Wellbeing
              </CardTitle>
              <CardDescription>Your emotional patterns this week</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ChartContainer
                config={{
                  mood: { label: "Mood Score", color: "hsl(var(--chart-2))" },
                }}
                className="h-[250px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={moodTrendData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis dataKey="day" className="text-xs" />
                    <YAxis domain={[0, 10]} className="text-xs" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Line
                      type="monotone"
                      dataKey="mood"
                      stroke="#000000"
                      strokeWidth={1}
                      strokeOpacity={1}
                      dot={{ fill: "hsl(var(--chart-2))", r: 5, strokeWidth: 2, stroke: "#fff" }}
                      activeDot={{ r: 7 }}
                      connectNulls={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartContainer>
              <div className="flex gap-4 text-sm">
                <div className="flex-1">
                  <div className="text-muted-foreground">Average Mood</div>
                  <div className="text-2xl font-bold">7.1/10</div>
                </div>
                <div className="flex-1">
                  <div className="text-muted-foreground">Most Common</div>
                  <div className="text-2xl">😊</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Module C - AI Insights & Recommendations */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                AI Insights & Recommendations
              </CardTitle>
              <CardDescription>Smart suggestions based on your patterns</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                <p className="text-sm">
                  <span className="font-semibold">💡 Peak Performance:</span> Your productivity is 40% higher in the morning.
                  Try scheduling complex tasks before noon.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-chart-2/5 border border-chart-2/20">
                <p className="text-sm">
                  <span className="font-semibold">😌 Wellbeing Tip:</span> Your mood dips on Thursdays.
                  Consider scheduling lighter tasks or breaks mid-week.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-chart-3/5 border border-chart-3/20">
                <p className="text-sm">
                  <span className="font-semibold">🎯 Consistency Win:</span> You've maintained a 7-day streak!
                  Keep this momentum to build lasting habits.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-chart-4/5 border border-chart-4/20">
                <p className="text-sm">
                  <span className="font-semibold">📊 Tomorrow's Forecast:</span> Based on patterns, tomorrow's productivity score: 85.
                  Great conditions for tackling important work!
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Module D - Habit & Routine Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Habit & Routine Metrics
              </CardTitle>
              <CardDescription>Your consistency and growth</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <Flame className="w-4 h-4 text-orange-500" />
                    <span className="text-sm">Task Streak</span>
                  </div>
                  <Badge>7 days</Badge>
                </div>
                <Progress value={70} className="h-2" />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-sm">Weekly Consistency</span>
                  </div>
                  <Badge>85%</Badge>
                </div>
                <Progress value={85} className="h-2" />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-purple-500" />
                    <span className="text-sm">Focus Sessions</span>
                  </div>
                  <Badge>24 this week</Badge>
                </div>
                <Progress value={60} className="h-2" />
              </div>
            </CardContent>
          </Card>

          {/* Work Category Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Work Distribution</CardTitle>
              <CardDescription>Time spent by category</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  study: { label: "Study", color: "hsl(258 100% 83%)" },
                  coding: { label: "Coding", color: "hsl(258 80% 70%)" },
                  fitness: { label: "Fitness", color: "hsl(258 70% 75%)" },
                  personal: { label: "Personal", color: "hsl(258 60% 80%)" },
                }}
                className="h-[200px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="hsl(var(--primary))"
                      dataKey="value"
                      stroke="#000000"
                      strokeWidth={1}
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <ChartTooltip content={<ChartTooltipContent />} />
                  </PieChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </div>

        {/* Activity Heatmap - Full width */}
        <ContributionCalendar />
      </section>

      <Separator />

      {/* 3️⃣ ACTIVITY LOGS - Bottom Section */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold flex items-center gap-2">
          <Clock className="w-6 h-6 text-primary" />
          Recent Activity
        </h2>
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {recentActivities.map((activity, index) => (
                <div key={index} className="flex items-start gap-4 pb-4 border-b border-border last:border-0">
                  <div className={`w-2 h-2 rounded-full mt-2 ${activity.type === 'task' ? 'bg-green-500' :
                    activity.type === 'journal' ? 'bg-blue-500' : 'bg-gray-500'
                    }`} />
                  <div className="flex-1">
                    <p className="font-medium">{activity.title}</p>
                    <p className="text-sm text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
};

export default Dashboard;
