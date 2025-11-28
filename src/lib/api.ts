// API Client for NeuroMate Backend
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

// Get auth token from localStorage
const getToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Set auth token in localStorage
export const setAuthToken = (token: string): void => {
  localStorage.setItem('auth_token', token);
};

// Remove auth token from localStorage
export const removeAuthToken = (): void => {
  localStorage.removeItem('auth_token');
};

// API request helper
const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.error || error.message || errorMessage;
      } catch (e) {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return response;
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('fetch') || error.message.includes('Failed to parse')) {
        throw new Error('Failed to connect to server. Please make sure the backend is running.');
      }
    }
    throw error;
  }
};

// Auth API
export const authAPI = {
  signUp: async (email: string, password: string, username?: string) => {
    const response = await apiRequest('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, username }),
    });
    const data = await response.json();
    if (data.token) {
      setAuthToken(data.token);
    }
    return { user: data.user, error: null };
  },

  signIn: async (email: string, password: string) => {
    const response = await apiRequest('/auth/signin', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (data.token) {
      setAuthToken(data.token);
    }
    return { user: data.user, error: null };
  },

  signOut: async () => {
    removeAuthToken();
    return { error: null };
  },

  changePassword: async (newPassword: string) => {
    try {
      const response = await apiRequest('/auth/password', {
        method: 'PUT',
        body: JSON.stringify({ newPassword }),
      });
      await response.json();
      return { error: null };
    } catch (error) {
      return { error: error instanceof Error ? error : new Error(String(error)) };
    }
  },

  getCurrentUser: async () => {
    try {
      const token = getToken();
      if (!token) return null;

      // Get user profile (which includes user info)
      const response = await apiRequest('/profile');
      const profile = await response.json();
      return profile;
    } catch {
      return null;
    }
  },
};

// Profile API
export const profileAPI = {
  get: async (userId: string) => {
    const response = await apiRequest('/profile');
    return await response.json();
  },

  update: async (updates: Record<string, string | number | boolean | null>) => {
    try {
      const response = await apiRequest('/profile', {
        method: 'PUT',
        body: JSON.stringify(updates),
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  },
};

// Activities API
export const activitiesAPI = {
  get: async (type: string, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams({ type });
    if (startDate) params.append('startDate', startDate);
    if (endDate) params.append('endDate', endDate);

    const response = await apiRequest(`/activities?${params.toString()}`);
    return await response.json();
  },

  createTask: async (title: string, description?: string, completed?: boolean) => {
    const response = await apiRequest('/activities/tasks', {
      method: 'POST',
      body: JSON.stringify({ title, description, completed }),
    });
    return await response.json();
  },

  createMood: async (mood_level: number, mood_type?: string, notes?: string) => {
    const response = await apiRequest('/activities/moods', {
      method: 'POST',
      body: JSON.stringify({ mood_level, mood_type, notes }),
    });
    return await response.json();
  },

  createFocusSession: async (activity: string, duration_minutes: number, notes?: string) => {
    const response = await apiRequest('/activities/focus', {
      method: 'POST',
      body: JSON.stringify({ activity, duration_minutes, notes }),
    });
    return await response.json();
  },

  createJournal: async (title: string, content: string, mood?: string) => {
    const response = await apiRequest('/activities/journals', {
      method: 'POST',
      body: JSON.stringify({ title, content, mood }),
    });
    return await response.json();
  },

  createRoutine: async (name: string, description?: string, completed?: boolean) => {
    const response = await apiRequest('/activities/routines', {
      method: 'POST',
      body: JSON.stringify({ name, description, completed }),
    });
    return await response.json();
  },

  createMeditation: async (type: string, duration_minutes: number, notes?: string) => {
    const response = await apiRequest('/activities/meditations', {
      method: 'POST',
      body: JSON.stringify({ type, duration_minutes, notes }),
    });
    return await response.json();
  },

  createPost: async (content: string, mood?: string) => {
    const response = await apiRequest('/activities/posts', {
      method: 'POST',
      body: JSON.stringify({ content, mood }),
    });
    return await response.json();
  },
};

// Beta signup API (for Contact page)
export const betaAPI = {
  signup: async (name: string, email: string, phone: string) => {
    const response = await apiRequest('/beta/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, phone }),
    });
    return await response.json();
  },
};

// Contact API
export const contactAPI = {
  sendMessage: async (name: string, email: string, message: string) => {
    const response = await apiRequest('/contact', {
      method: 'POST',
      body: JSON.stringify({ name, email, message }),
    });
    return await response.json();
  },
};

