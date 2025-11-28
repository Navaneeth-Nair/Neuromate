import { useState, useEffect } from 'react';
import { authAPI, getToken, removeAuthToken } from '@/lib/api';

export type User = {
  id: string;
  email: string;
  username?: string;
  [key: string]: any;
};

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const checkAuth = async () => {
      try {
        const currentUser = await authAPI.getCurrentUser();
        setUser(currentUser);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const signUp = async (email: string, password: string, username?: string) => {
    try {
      const { user: newUser, error } = await authAPI.signUp(email, password, username);
      if (error) {
        return { error: { message: error } };
      }
      setUser(newUser);
      return { error: null };
    } catch (error: any) {
      return { error: { message: error.message || 'Failed to sign up' } };
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const { user: signedInUser, error } = await authAPI.signIn(email, password);
      if (error) {
        return { error: { message: error } };
      }
      setUser(signedInUser);
      return { error: null };
    } catch (error: any) {
      return { error: { message: error.message || 'Failed to sign in' } };
    }
  };

  const signOut = async () => {
    try {
      await authAPI.signOut();
      setUser(null);
      return { error: null };
    } catch (error: any) {
      return { error: { message: error.message || 'Failed to sign out' } };
    }
  };

  return {
    user,
    session: user ? { user } : null,
    loading,
    signUp,
    signIn,
    signOut,
  };
};
