import { useAuth } from '@/hooks/useAuth';
import { useProfile } from '@/hooks/useProfile';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import {
  Settings,
  Briefcase,
  BarChart3,
  DollarSign,
  Users,
  Power,
  User,
  LogOut,
  ChevronRight,
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

type PersonalSectionPanelProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

const PersonalSectionPanel = ({ open, onOpenChange }: PersonalSectionPanelProps) => {
  const { user, signOut } = useAuth();
  const { profile, loading } = useProfile(user?.id);
  const navigate = useNavigate();

  console.log('PersonalSectionPanel - user:', user?.id);
  console.log('PersonalSectionPanel - profile:', profile);
  console.log('PersonalSectionPanel - loading:', loading);

  const handleSignOut = async () => {
    const { error } = await signOut();
    if (error) {
      toast.error('Error signing out');
    } else {
      toast.success('Signed out successfully');
      onOpenChange(false);
      navigate('/');
    }
  };

  const menuItems = [
    { icon: User, label: 'Profile Info', path: '/profile' },
    { icon: Settings, label: 'Settings', path: '/settings' },
    { icon: Briefcase, label: 'Productivity Tools', path: '/productivity' },
    { icon: BarChart3, label: 'Dashboard Analytics', path: '/dashboard' },
    { icon: DollarSign, label: 'Pricing', path: '/pricing' },
    { icon: Users, label: 'Community', path: '/community' },
    { icon: Power, label: 'Kill Switch', path: '/kill-switch' },
  ];

  const statusColors = {
    online: 'bg-green-500',
    focusing: 'bg-yellow-500',
    'do not disturb': 'bg-red-500',
  };

  const getStatusColor = () => {
    const status = profile?.status || 'online';
    return statusColors[status as keyof typeof statusColors] || statusColors.online;
  };

  if (!user) return null;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:w-[400px] p-0 flex flex-col">
        <SheetHeader className="p-6 pb-4 border-b">
          <SheetTitle>Personal Menu</SheetTitle>
        </SheetHeader>

        {/* Menu Items */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => onOpenChange(false)}
              className="flex items-center justify-between p-3 rounded-lg glass-card hover:bg-accent transition-colors group"
            >
              <div className="flex items-center gap-3">
                <item.icon className="h-5 w-5 text-primary" />
                <span className="font-medium">{item.label}</span>
              </div>
              <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
            </Link>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="p-6 border-t space-y-4">
          <Button
            variant="destructive"
            className="w-full"
            onClick={handleSignOut}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Log Out
          </Button>
          <p className="text-xs text-center text-muted-foreground">
            NeuroMate v1.0 – Beta
          </p>
        </div>
      </SheetContent>
    </Sheet>
  );
};

export default PersonalSectionPanel;
