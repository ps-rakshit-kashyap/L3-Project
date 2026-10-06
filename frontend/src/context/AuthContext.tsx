'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabaseClient';
import { ApiService } from '@/services/api';
import { UserProfile, UserRole } from '@/types/models';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  role: UserRole | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<UserProfile>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const syncBackendProfile = async (accessToken: string, name?: string): Promise<UserProfile | null> => {
    ApiService.setAuthToken(accessToken);
    try {
      // First try to fetch existing profile
      let p = await ApiService.getMe();
      return p;
    } catch {
      // If profile does not exist yet in DB, sync from token
      try {
        const p = await ApiService.syncUser(name);
        return p;
      } catch (e) {
        console.error('Failed to sync user profile with backend:', e);
        return null;
      }
    }
  };

  useEffect(() => {
    let mounted = true;

    // Check active session on load
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      if (!mounted) return;
      setSession(session);
      setUser(session?.user ?? null);

      if (session?.access_token) {
        const p = await syncBackendProfile(session.access_token);
        if (mounted) setProfile(p);
      } else {
        ApiService.setAuthToken(null);
        if (mounted) setProfile(null);
      }
      if (mounted) setLoading(false);
    });

    // Listen for auth state changes (login, logout, refresh)
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (!mounted) return;
      setSession(session);
      setUser(session?.user ?? null);

      if (session?.access_token) {
        const p = await syncBackendProfile(session.access_token);
        if (mounted) setProfile(p);
      } else {
        ApiService.setAuthToken(null);
        if (mounted) setProfile(null);
      }
      if (mounted) setLoading(false);
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const login = async (email: string, password: string): Promise<UserProfile> => {
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (error) {
        throw new Error(error.message);
      }

      if (!data.session) {
        throw new Error('No session returned after login');
      }

      setSession(data.session);
      setUser(data.user);

      const p = await syncBackendProfile(data.session.access_token);
      if (!p) {
        throw new Error('Failed to load application profile from backend');
      }
      setProfile(p);
      return p;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email: string, password: string, name: string): Promise<void> => {
    setLoading(true);
    try {
      // 1. Register candidate via backend (uses Supabase Admin API with auto-confirmed email to avoid SMTP limits/RFC domain blocks)
      try {
        await ApiService.signupUser(name, email, password);
      } catch (backendErr: unknown) {
        console.warn('Backend signup exception, attempting direct Supabase signUp fallback:', backendErr);
        const { error: sbError } = await supabase.auth.signUp({
          email: email.trim(),
          password,
          options: {
            data: { name: name.trim() },
          },
        });
        if (sbError) {
          const msg = backendErr instanceof Error ? backendErr.message : sbError.message;
          throw new Error(msg);
        }
      }

      // 2. Immediately sign in to establish active session and access token
      await login(email, password);
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    setLoading(true);
    try {
      await supabase.auth.signOut();
      ApiService.setAuthToken(null);
      setUser(null);
      setSession(null);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  const refreshProfile = async (): Promise<void> => {
    if (session?.access_token) {
      const p = await syncBackendProfile(session.access_token);
      setProfile(p);
    }
  };

  const role = profile?.role ?? null;

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        profile,
        role,
        loading,
        login,
        signup,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
