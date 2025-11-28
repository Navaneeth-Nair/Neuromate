import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useProfile } from "@/hooks/useProfile";
import { useTheme } from "@/hooks/useTheme";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "@/components/ui/use-toast";
// Settings no longer uses Supabase - all data is stored locally or via API
import { 
  Palette, 
  Shield, 
  Monitor,
  Sun,
  Moon,
  Bell,
  Mic,
  Volume2,
  Accessibility,
  Type,
  BookOpen,
  Keyboard,
  Sliders,
  Settings as SettingsIcon,
  HardDrive,
  Code,
  Sparkles,
  Download,
  Trash2,
  Eye,
  EyeOff
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

type Theme = "light" | "dark" | "system";

const Settings = () => {
  const { user, signOut } = useAuth();
  const { profile } = useProfile(user?.id);
  const { theme, setTheme } = useTheme();
  
  const [isExporting, setIsExporting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const [fontSize, setFontSize] = useState(() => localStorage.getItem("fontSize") || "medium");
  const [layoutMode, setLayoutMode] = useState(() => localStorage.getItem("layoutMode") || "spacious");
  const [animationsEnabled, setAnimationsEnabled] = useState(() => 
    localStorage.getItem("animationsEnabled") !== "false"
  );

  const [aiDataUsage, setAiDataUsage] = useState(() => 
    localStorage.getItem("aiDataUsage") !== "false"
  );
  const [activityTracking, setActivityTracking] = useState(() => 
    localStorage.getItem("activityTracking") !== "false"
  );
  const [profileVisibility, setProfileVisibility] = useState(() => 
    localStorage.getItem("profileVisibility") || "public"
  );

  // AI Behavior Settings
  const [aiResponseStyle, setAiResponseStyle] = useState(() => 
    localStorage.getItem("aiResponseStyle") || "friendly"
  );
  const [aiTone, setAiTone] = useState(() => 
    localStorage.getItem("aiTone") || "neutral"
  );
  const [emotionDetection, setEmotionDetection] = useState(() => 
    localStorage.getItem("emotionDetection") !== "false"
  );
  const [voiceMode, setVoiceMode] = useState(() => 
    localStorage.getItem("voiceMode") === "true"
  );
  const [ttsVoice, setTtsVoice] = useState(() => 
    localStorage.getItem("ttsVoice") || "default"
  );

  // Productivity Settings
  const [defaultTaskPriority, setDefaultTaskPriority] = useState(() => 
    localStorage.getItem("defaultTaskPriority") || "medium"
  );
  const [plannerView, setPlannerView] = useState(() => 
    localStorage.getItem("plannerView") || "week"
  );
  const [pomodoroTime, setPomodoroTime] = useState(() => 
    localStorage.getItem("pomodoroTime") || "25"
  );
  const [focusMode, setFocusMode] = useState(() => 
    localStorage.getItem("focusMode") === "true"
  );

  // Notifications Settings
  const [browserNotifications, setBrowserNotifications] = useState(() => 
    localStorage.getItem("browserNotifications") !== "false"
  );
  const [emailNotifications, setEmailNotifications] = useState(() => 
    localStorage.getItem("emailNotifications") !== "false"
  );
  const [soundNotifications, setSoundNotifications] = useState(() => 
    localStorage.getItem("soundNotifications") !== "false"
  );
  const [taskReminders, setTaskReminders] = useState(() => 
    localStorage.getItem("taskReminders") !== "false"
  );
  const [moodCheckIns, setMoodCheckIns] = useState(() => 
    localStorage.getItem("moodCheckIns") !== "false"
  );

  // Accessibility Settings
  const [highContrast, setHighContrast] = useState(() => 
    localStorage.getItem("highContrast") === "true"
  );
  const [dyslexiaFont, setDyslexiaFont] = useState(() => 
    localStorage.getItem("dyslexiaFont") === "true"
  );
  const [readerMode, setReaderMode] = useState(() => 
    localStorage.getItem("readerMode") === "true"
  );
  const [keyboardNav, setKeyboardNav] = useState(() => 
    localStorage.getItem("keyboardNav") === "true"
  );
  const [textSpacing, setTextSpacing] = useState(() => 
    localStorage.getItem("textSpacing") || "normal"
  );
  const [voiceInputSensitivity, setVoiceInputSensitivity] = useState(() => 
    localStorage.getItem("voiceInputSensitivity") || "medium"
  );

  // System Settings
  const [autoLaunch, setAutoLaunch] = useState(() => 
    localStorage.getItem("autoLaunch") === "true"
  );
  const [hardwareAcceleration, setHardwareAcceleration] = useState(() => 
    localStorage.getItem("hardwareAcceleration") !== "false"
  );
  const [defaultMicrophone, setDefaultMicrophone] = useState(() => 
    localStorage.getItem("defaultMicrophone") || "default"
  );
  const [defaultSpeaker, setDefaultSpeaker] = useState(() => 
    localStorage.getItem("defaultSpeaker") || "default"
  );
  const [developerMode, setDeveloperMode] = useState(() => 
    localStorage.getItem("developerMode") === "true"
  );
  const [betaFeatures, setBetaFeatures] = useState(() => 
    localStorage.getItem("betaFeatures") === "true"
  );

  const handleFontSizeChange = (value: string) => {
    setFontSize(value);
    localStorage.setItem("fontSize", value);
    document.documentElement.style.fontSize = 
      value === "small" ? "14px" : value === "large" ? "18px" : "16px";
    toast({
      title: "Font size updated",
      description: `Font size set to ${value}`,
    });
  };

  const handleLayoutModeChange = (value: string) => {
    setLayoutMode(value);
    localStorage.setItem("layoutMode", value);
    toast({
      title: "Layout updated",
      description: `Layout mode set to ${value}`,
    });
  };

  const handleAnimationsToggle = (checked: boolean) => {
    setAnimationsEnabled(checked);
    localStorage.setItem("animationsEnabled", String(checked));
    document.documentElement.style.setProperty(
      "--animation-duration",
      checked ? "0.3s" : "0s"
    );
    toast({
      title: checked ? "Animations enabled" : "Animations disabled",
    });
  };

  const handleAiDataUsageToggle = (checked: boolean) => {
    setAiDataUsage(checked);
    localStorage.setItem("aiDataUsage", String(checked));
    toast({
      title: checked ? "AI personalization enabled" : "AI personalization disabled",
      description: checked 
        ? "AI will use your data to provide personalized responses" 
        : "AI will not use your data for personalization",
    });
  };

  const handleActivityTrackingToggle = (checked: boolean) => {
    setActivityTracking(checked);
    localStorage.setItem("activityTracking", String(checked));
    toast({
      title: checked ? "Activity tracking enabled" : "Activity tracking disabled",
    });
  };

  const handleProfileVisibilityChange = (value: string) => {
    setProfileVisibility(value);
    localStorage.setItem("profileVisibility", value);
    toast({
      title: "Profile visibility updated",
      description: `Your profile is now ${value}`,
    });
  };

  const handleExportData = async () => {
    setIsExporting(true);
    try {
      const userData = {
        profile: profile,
        email: user?.email,
        created_at: user?.created_at,
        settings: {
          theme,
          fontSize,
          layoutMode,
          animationsEnabled,
          aiDataUsage,
          activityTracking,
          profileVisibility,
        }
      };

      const dataStr = JSON.stringify(userData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `neuromate-data-${new Date().toISOString()}.json`;
      link.click();
      URL.revokeObjectURL(url);

      toast({
        title: "Data exported",
        description: "Your data has been downloaded",
      });
    } catch (error) {
      toast({
        title: "Export failed",
        description: "Failed to export your data",
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      toast({
        title: "Account deletion requested",
        description: "Please contact support to complete account deletion",
      });
      await signOut();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete account",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  // AI Behavior Handlers
  const handleAiResponseStyleChange = (value: string) => {
    setAiResponseStyle(value);
    localStorage.setItem("aiResponseStyle", value);
    toast({
      title: "AI response style updated",
      description: `AI will now respond in a ${value} manner`,
    });
  };

  const handleAiToneChange = (value: string) => {
    setAiTone(value);
    localStorage.setItem("aiTone", value);
    toast({
      title: "AI tone updated",
      description: `Tone set to ${value}`,
    });
  };

  const handleEmotionDetectionToggle = (checked: boolean) => {
    setEmotionDetection(checked);
    localStorage.setItem("emotionDetection", String(checked));
    toast({
      title: checked ? "Emotion detection enabled" : "Emotion detection disabled",
    });
  };

  const handleVoiceModeToggle = (checked: boolean) => {
    setVoiceMode(checked);
    localStorage.setItem("voiceMode", String(checked));
    toast({
      title: checked ? "Voice mode enabled" : "Voice mode disabled",
    });
  };

  const handleTtsVoiceChange = (value: string) => {
    setTtsVoice(value);
    localStorage.setItem("ttsVoice", value);
    toast({
      title: "Voice updated",
      description: `TTS voice set to ${value}`,
    });
  };

  // Productivity Handlers
  const handleDefaultTaskPriorityChange = (value: string) => {
    setDefaultTaskPriority(value);
    localStorage.setItem("defaultTaskPriority", value);
    toast({
      title: "Default task priority updated",
      description: `New tasks will default to ${value} priority`,
    });
  };

  const handlePlannerViewChange = (value: string) => {
    setPlannerView(value);
    localStorage.setItem("plannerView", value);
    toast({
      title: "Planner view updated",
      description: `View set to ${value}`,
    });
  };

  const handlePomodoroTimeChange = (value: string) => {
    setPomodoroTime(value);
    localStorage.setItem("pomodoroTime", value);
    toast({
      title: "Pomodoro timer updated",
      description: `Focus time set to ${value} minutes`,
    });
  };

  const handleFocusModeToggle = (checked: boolean) => {
    setFocusMode(checked);
    localStorage.setItem("focusMode", String(checked));
    toast({
      title: checked ? "Focus mode enabled" : "Focus mode disabled",
      description: checked ? "Notifications will be muted during focus sessions" : "",
    });
  };

  // Notifications Handlers
  const handleBrowserNotificationsToggle = (checked: boolean) => {
    setBrowserNotifications(checked);
    localStorage.setItem("browserNotifications", String(checked));
    if (checked && "Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
    toast({
      title: checked ? "Browser notifications enabled" : "Browser notifications disabled",
    });
  };

  const handleEmailNotificationsToggle = (checked: boolean) => {
    setEmailNotifications(checked);
    localStorage.setItem("emailNotifications", String(checked));
    toast({
      title: checked ? "Email notifications enabled" : "Email notifications disabled",
    });
  };

  const handleSoundNotificationsToggle = (checked: boolean) => {
    setSoundNotifications(checked);
    localStorage.setItem("soundNotifications", String(checked));
    toast({
      title: checked ? "Sound notifications enabled" : "Sound notifications disabled",
    });
  };

  const handleTaskRemindersToggle = (checked: boolean) => {
    setTaskReminders(checked);
    localStorage.setItem("taskReminders", String(checked));
    toast({
      title: checked ? "Task reminders enabled" : "Task reminders disabled",
    });
  };

  const handleMoodCheckInsToggle = (checked: boolean) => {
    setMoodCheckIns(checked);
    localStorage.setItem("moodCheckIns", String(checked));
    toast({
      title: checked ? "Mood check-ins enabled" : "Mood check-ins disabled",
    });
  };

  // Accessibility Handlers
  const handleHighContrastToggle = (checked: boolean) => {
    setHighContrast(checked);
    localStorage.setItem("highContrast", String(checked));
    if (checked) {
      document.documentElement.classList.add("high-contrast");
    } else {
      document.documentElement.classList.remove("high-contrast");
    }
    toast({
      title: checked ? "High contrast mode enabled" : "High contrast mode disabled",
    });
  };

  const handleDyslexiaFontToggle = (checked: boolean) => {
    setDyslexiaFont(checked);
    localStorage.setItem("dyslexiaFont", String(checked));
    if (checked) {
      document.documentElement.style.fontFamily = "OpenDyslexic, Arial, sans-serif";
    } else {
      document.documentElement.style.fontFamily = "";
    }
    toast({
      title: checked ? "Dyslexia-friendly font enabled" : "Standard font restored",
    });
  };

  const handleReaderModeToggle = (checked: boolean) => {
    setReaderMode(checked);
    localStorage.setItem("readerMode", String(checked));
    if (checked) {
      document.documentElement.classList.add("reader-mode");
    } else {
      document.documentElement.classList.remove("reader-mode");
    }
    toast({
      title: checked ? "Reader mode enabled" : "Reader mode disabled",
      description: checked ? "Content optimized for reading" : "",
    });
  };

  const handleKeyboardNavToggle = (checked: boolean) => {
    setKeyboardNav(checked);
    localStorage.setItem("keyboardNav", String(checked));
    if (checked) {
      document.documentElement.classList.add("keyboard-nav");
    } else {
      document.documentElement.classList.remove("keyboard-nav");
    }
    toast({
      title: checked ? "Keyboard navigation enhanced" : "Standard navigation restored",
    });
  };

  const handleTextSpacingChange = (value: string) => {
    setTextSpacing(value);
    localStorage.setItem("textSpacing", value);
    
    const spacingMap = {
      compact: { lineHeight: "1.4", letterSpacing: "0" },
      normal: { lineHeight: "1.6", letterSpacing: "0.01em" },
      relaxed: { lineHeight: "1.8", letterSpacing: "0.02em" },
      spacious: { lineHeight: "2", letterSpacing: "0.05em" }
    };
    
    const spacing = spacingMap[value as keyof typeof spacingMap];
    document.documentElement.style.lineHeight = spacing.lineHeight;
    document.documentElement.style.letterSpacing = spacing.letterSpacing;
    
    toast({
      title: "Text spacing updated",
      description: `Spacing set to ${value}`,
    });
  };

  const handleVoiceInputSensitivityChange = (value: string) => {
    setVoiceInputSensitivity(value);
    localStorage.setItem("voiceInputSensitivity", value);
    toast({
      title: "Voice input sensitivity updated",
      description: `Sensitivity set to ${value}`,
    });
  };

  // System Settings Handlers
  const handleAutoLaunchToggle = (checked: boolean) => {
    setAutoLaunch(checked);
    localStorage.setItem("autoLaunch", String(checked));
    toast({
      title: checked ? "Auto launch enabled" : "Auto launch disabled",
      description: checked ? "App will launch on system startup" : "",
    });
  };

  const handleHardwareAccelerationToggle = (checked: boolean) => {
    setHardwareAcceleration(checked);
    localStorage.setItem("hardwareAcceleration", String(checked));
    toast({
      title: checked ? "Hardware acceleration enabled" : "Hardware acceleration disabled",
      description: "Restart the app for changes to take effect",
    });
  };

  const handleDefaultMicrophoneChange = (value: string) => {
    setDefaultMicrophone(value);
    localStorage.setItem("defaultMicrophone", value);
    toast({
      title: "Default microphone updated",
      description: `Set to ${value}`,
    });
  };

  const handleDefaultSpeakerChange = (value: string) => {
    setDefaultSpeaker(value);
    localStorage.setItem("defaultSpeaker", value);
    toast({
      title: "Default speaker updated",
      description: `Set to ${value}`,
    });
  };

  const handleClearCache = () => {
    localStorage.clear();
    toast({
      title: "Cache cleared",
      description: "Local cache has been cleared. Please refresh the page.",
    });
  };

  const handleDeveloperModeToggle = (checked: boolean) => {
    setDeveloperMode(checked);
    localStorage.setItem("developerMode", String(checked));
    toast({
      title: checked ? "Developer mode enabled" : "Developer mode disabled",
      description: checked ? "Advanced options are now available" : "",
    });
  };

  const handleBetaFeaturesToggle = (checked: boolean) => {
    setBetaFeatures(checked);
    localStorage.setItem("betaFeatures", String(checked));
    toast({
      title: checked ? "Beta features enabled" : "Beta features disabled",
      description: checked ? "You now have access to experimental features" : "",
    });
  };

  return (
    <div className="container mx-auto px-6 py-24">
      <h1 className="text-4xl font-heading font-bold gradient-text mb-8">Settings</h1>
      
      <Tabs defaultValue="personalization" className="w-full">
        <TabsList className="grid w-full grid-cols-2 md:grid-cols-3 lg:grid-cols-5 mb-8">
          <TabsTrigger value="personalization" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Personalization
          </TabsTrigger>
          <TabsTrigger value="privacy" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Privacy & Security
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="accessibility" className="flex items-center gap-2">
            <Accessibility className="h-4 w-4" />
            Accessibility
          </TabsTrigger>
          <TabsTrigger value="system" className="flex items-center gap-2">
            <SettingsIcon className="h-4 w-4" />
            System
          </TabsTrigger>
        </TabsList>

        <TabsContent value="personalization" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Theme</CardTitle>
              <CardDescription>Choose your preferred color scheme</CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup value={theme} onValueChange={(value: Theme) => setTheme(value)}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="light" id="light" />
                  <Label htmlFor="light" className="flex items-center gap-2 cursor-pointer">
                    <Sun className="h-4 w-4" />
                    Light
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="dark" id="dark" />
                  <Label htmlFor="dark" className="flex items-center gap-2 cursor-pointer">
                    <Moon className="h-4 w-4" />
                    Dark
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="system" id="system" />
                  <Label htmlFor="system" className="flex items-center gap-2 cursor-pointer">
                    <Monitor className="h-4 w-4" />
                    System
                  </Label>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Font Size</CardTitle>
              <CardDescription>Adjust text size across the app</CardDescription>
            </CardHeader>
            <CardContent>
              <Select value={fontSize} onValueChange={handleFontSizeChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="small">Small</SelectItem>
                  <SelectItem value="medium">Medium (Default)</SelectItem>
                  <SelectItem value="large">Large</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>App Layout</CardTitle>
              <CardDescription>Choose between compact or spacious layout</CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup value={layoutMode} onValueChange={handleLayoutModeChange}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="compact" id="compact" />
                  <Label htmlFor="compact" className="cursor-pointer">Compact</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="spacious" id="spacious" />
                  <Label htmlFor="spacious" className="cursor-pointer">Spacious</Label>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Animations</CardTitle>
              <CardDescription>Enable or disable interface animations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <Label htmlFor="animations" className="cursor-pointer">Enable Animations</Label>
                <Switch
                  id="animations"
                  checked={animationsEnabled}
                  onCheckedChange={handleAnimationsToggle}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="privacy" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Personalization</CardTitle>
              <CardDescription>Control how AI uses your data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="ai-data" className="cursor-pointer">Use my data for AI personalization</Label>
                  <p className="text-sm text-muted-foreground">
                    Allow AI to learn from your interactions to provide better responses
                  </p>
                </div>
                <Switch
                  id="ai-data"
                  checked={aiDataUsage}
                  onCheckedChange={handleAiDataUsageToggle}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Activity Tracking</CardTitle>
              <CardDescription>Manage activity and analytics tracking</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="activity" className="cursor-pointer">Allow activity tracking</Label>
                  <p className="text-sm text-muted-foreground">
                    Help us improve by tracking anonymous usage data
                  </p>
                </div>
                <Switch
                  id="activity"
                  checked={activityTracking}
                  onCheckedChange={handleActivityTrackingToggle}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Profile Visibility</CardTitle>
              <CardDescription>Control who can see your profile</CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup value={profileVisibility} onValueChange={handleProfileVisibilityChange}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="public" id="public" />
                  <Label htmlFor="public" className="cursor-pointer">
                    <div className="flex items-center gap-2">
                      <Eye className="h-4 w-4" />
                      Public - Anyone can see your profile
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="private" id="private" />
                  <Label htmlFor="private" className="cursor-pointer">
                    <div className="flex items-center gap-2">
                      <EyeOff className="h-4 w-4" />
                      Private - Only you can see your profile
                    </div>
                  </Label>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          <Separator />

          <Card>
            <CardHeader>
              <CardTitle>Data Management</CardTitle>
              <CardDescription>Export or delete your data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Export Your Data</p>
                  <p className="text-sm text-muted-foreground">
                    Download a copy of your account data
                  </p>
                </div>
                <Button 
                  variant="outline" 
                  onClick={handleExportData}
                  disabled={isExporting}
                >
                  <Download className="mr-2 h-4 w-4" />
                  {isExporting ? "Exporting..." : "Export"}
                </Button>
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-destructive">Delete Account</p>
                  <p className="text-sm text-muted-foreground">
                    Permanently delete your account and all data
                  </p>
                </div>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This action cannot be undone. This will permanently delete your
                        account and remove all your data from our servers.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={handleDeleteAccount}
                        disabled={isDeleting}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      >
                        {isDeleting ? "Deleting..." : "Delete Account"}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Notification Channels</CardTitle>
              <CardDescription>Choose how you want to receive notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="browser-notif" className="cursor-pointer">Browser Notifications</Label>
                  <p className="text-sm text-muted-foreground">Receive notifications in your browser</p>
                </div>
                <Switch
                  id="browser-notif"
                  checked={browserNotifications}
                  onCheckedChange={handleBrowserNotificationsToggle}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="email-notif" className="cursor-pointer">Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">Get updates via email</p>
                </div>
                <Switch
                  id="email-notif"
                  checked={emailNotifications}
                  onCheckedChange={handleEmailNotificationsToggle}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="sound-notif" className="cursor-pointer">Sound Notifications</Label>
                  <p className="text-sm text-muted-foreground">Play sound for notifications</p>
                </div>
                <Switch
                  id="sound-notif"
                  checked={soundNotifications}
                  onCheckedChange={handleSoundNotificationsToggle}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Activity Reminders</CardTitle>
              <CardDescription>Manage reminders for different activities</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="task-reminders" className="cursor-pointer">Task Reminders</Label>
                  <p className="text-sm text-muted-foreground">Get reminded about upcoming tasks</p>
                </div>
                <Switch
                  id="task-reminders"
                  checked={taskReminders}
                  onCheckedChange={handleTaskRemindersToggle}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="mood-checkins" className="cursor-pointer">Mood Check-ins</Label>
                  <p className="text-sm text-muted-foreground">Receive daily mood check-in prompts</p>
                </div>
                <Switch
                  id="mood-checkins"
                  checked={moodCheckIns}
                  onCheckedChange={handleMoodCheckInsToggle}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="accessibility" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Visual Accessibility</CardTitle>
              <CardDescription>Adjust visual settings for better readability</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="high-contrast" className="cursor-pointer flex items-center gap-2">
                    <Eye className="h-4 w-4" />
                    High Contrast Mode
                  </Label>
                  <p className="text-sm text-muted-foreground">Enhanced color contrast for better visibility</p>
                </div>
                <Switch
                  id="high-contrast"
                  checked={highContrast}
                  onCheckedChange={handleHighContrastToggle}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="dyslexia-font" className="cursor-pointer flex items-center gap-2">
                    <Type className="h-4 w-4" />
                    Dyslexia-Friendly Font
                  </Label>
                  <p className="text-sm text-muted-foreground">Use OpenDyslexic font for easier reading</p>
                </div>
                <Switch
                  id="dyslexia-font"
                  checked={dyslexiaFont}
                  onCheckedChange={handleDyslexiaFontToggle}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="reader-mode" className="cursor-pointer flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    Reader Mode
                  </Label>
                  <p className="text-sm text-muted-foreground">Simplified layout for focused reading</p>
                </div>
                <Switch
                  id="reader-mode"
                  checked={readerMode}
                  onCheckedChange={handleReaderModeToggle}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Text Spacing</CardTitle>
              <CardDescription>Adjust line height and letter spacing</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="text-spacing" className="flex items-center gap-2">
                  <Sliders className="h-4 w-4" />
                  Spacing Level
                </Label>
                <RadioGroup value={textSpacing} onValueChange={handleTextSpacingChange}>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="compact" id="compact" />
                    <Label htmlFor="compact" className="cursor-pointer">Compact - Tighter spacing</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="normal" id="normal-spacing" />
                    <Label htmlFor="normal-spacing" className="cursor-pointer">Normal - Standard spacing</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="relaxed" id="relaxed" />
                    <Label htmlFor="relaxed" className="cursor-pointer">Relaxed - Comfortable spacing</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="spacious" id="spacious" />
                    <Label htmlFor="spacious" className="cursor-pointer">Spacious - Maximum spacing</Label>
                  </div>
                </RadioGroup>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Navigation</CardTitle>
              <CardDescription>Customize how you navigate the app</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="keyboard-nav" className="cursor-pointer flex items-center gap-2">
                    <Keyboard className="h-4 w-4" />
                    Enhanced Keyboard Navigation
                  </Label>
                  <p className="text-sm text-muted-foreground">Improved focus indicators and keyboard shortcuts</p>
                </div>
                <Switch
                  id="keyboard-nav"
                  checked={keyboardNav}
                  onCheckedChange={handleKeyboardNavToggle}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Voice Input</CardTitle>
              <CardDescription>Adjust voice recognition sensitivity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="voice-sensitivity" className="flex items-center gap-2">
                  <Mic className="h-4 w-4" />
                  Sensitivity Level
                </Label>
                <Select value={voiceInputSensitivity} onValueChange={handleVoiceInputSensitivityChange}>
                  <SelectTrigger id="voice-sensitivity">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low - Less sensitive</SelectItem>
                    <SelectItem value="medium">Medium - Balanced</SelectItem>
                    <SelectItem value="high">High - More sensitive</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground mt-2">
                  Higher sensitivity picks up softer voices but may increase false triggers
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Audio Devices</CardTitle>
              <CardDescription>Select your preferred microphone and speaker</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="default-mic" className="flex items-center gap-2">
                  <Mic className="h-4 w-4" />
                  Default Microphone
                </Label>
                <Select value={defaultMicrophone} onValueChange={handleDefaultMicrophoneChange}>
                  <SelectTrigger id="default-mic">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">System Default</SelectItem>
                    <SelectItem value="built-in">Built-in Microphone</SelectItem>
                    <SelectItem value="external">External Microphone</SelectItem>
                    <SelectItem value="bluetooth">Bluetooth Headset</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label htmlFor="default-speaker" className="flex items-center gap-2">
                  <Volume2 className="h-4 w-4" />
                  Default Speaker
                </Label>
                <Select value={defaultSpeaker} onValueChange={handleDefaultSpeakerChange}>
                  <SelectTrigger id="default-speaker">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">System Default</SelectItem>
                    <SelectItem value="built-in">Built-in Speakers</SelectItem>
                    <SelectItem value="external">External Speakers</SelectItem>
                    <SelectItem value="bluetooth">Bluetooth Audio</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Cache & Storage</CardTitle>
              <CardDescription>Manage app data and cache</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="flex items-center gap-2">
                    <HardDrive className="h-4 w-4" />
                    Clear Local Cache
                  </Label>
                  <p className="text-sm text-muted-foreground">Remove cached data to free up space</p>
                </div>
                <Button variant="outline" onClick={handleClearCache}>
                  Clear Cache
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Advanced Options</CardTitle>
              <CardDescription>Enable experimental and developer features</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="developer-mode" className="cursor-pointer flex items-center gap-2">
                    <Code className="h-4 w-4" />
                    Developer Mode
                  </Label>
                  <p className="text-sm text-muted-foreground">Enable debugging tools and advanced settings</p>
                </div>
                <Switch
                  id="developer-mode"
                  checked={developerMode}
                  onCheckedChange={handleDeveloperModeToggle}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="beta-features" className="cursor-pointer flex items-center gap-2">
                    <Sparkles className="h-4 w-4" />
                    Beta Features
                  </Label>
                  <p className="text-sm text-muted-foreground">Try experimental features before official release</p>
                </div>
                <Switch
                  id="beta-features"
                  checked={betaFeatures}
                  onCheckedChange={handleBetaFeaturesToggle}
                />
              </div>

              {developerMode && (
                <>
                  <Separator />
                  <div className="p-4 bg-muted rounded-lg">
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <Code className="h-4 w-4" />
                      Developer Information
                    </h4>
                    <div className="space-y-1 text-sm font-mono">
                      <p>App Version: 1.0.0</p>
                      <p>Environment: Production</p>
                      <p>Build: {new Date().toISOString().split('T')[0]}</p>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Settings;
