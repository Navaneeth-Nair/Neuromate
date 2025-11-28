import { useState, useEffect } from 'react';
import { profileAPI } from '@/lib/api';

export type UserProfile = {
  id: string;
  username: string | null;
  email: string | null;
  avatar_url: string | null;
  mood: string | null;
  status: string | null;
  first_name: string | null;
  last_name: string | null;
  phone_number: string | null;
};

export const useProfile = (userId: string | undefined) => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) {
      setProfile(null);
      setLoading(false);
      return;
    }

    const fetchProfile = async () => {
      try {
        const data = await profileAPI.get(userId);
        setProfile(data);
      } catch (error) {
        console.error('Error fetching profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [userId]);

  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!userId) return { error: new Error('No user ID') };

    try {
      const updatedProfile = await profileAPI.update(updates);
      // Ensure the updated profile is properly set
      if (updatedProfile && updatedProfile.id) {
        setProfile(updatedProfile);
      }
      return { error: null };
    } catch (error) {
      console.error('Error updating profile:', error);
      return { error: error as Error };
    }
  };

  return { profile, loading, updateProfile };
};
