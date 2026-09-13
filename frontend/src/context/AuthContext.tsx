import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { UserProfile, UserRole, AuthResponse } from '../types';
import {
  api,
  clearSession,
  getStoredToken,
  storeSession,
  REFRESH_TOKEN_KEY,
  USER_KEY,
} from '../services/api';

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  /** True until the cached session has been revalidated against the server. */
  isLoading: boolean;
  loginWithResponse: (data: AuthResponse) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const readCachedUser = (): UserProfile | null => {
  try {
    const saved = localStorage.getItem(USER_KEY);
    return saved ? (JSON.parse(saved) as UserProfile) : null;
  } catch {
    return null;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [user, setUser] = useState<UserProfile | null>(readCachedUser);
  const [isLoading, setIsLoading] = useState<boolean>(() => Boolean(getStoredToken()));

  const applyUser = useCallback((next: UserProfile | null) => {
    setUser(next);
    try {
      if (next) localStorage.setItem(USER_KEY, JSON.stringify(next));
      else localStorage.removeItem(USER_KEY);
    } catch {
      /* storage unavailable; state still holds for this page */
    }
  }, []);

  const logout = useCallback(() => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    // Revoke server-side so a stolen refresh token dies with the session
    // rather than outliving it. Best-effort: local state clears regardless.
    if (refreshToken) {
      api.logout(refreshToken).catch(() => undefined);
    }
    clearSession();
    setToken(null);
    setUser(null);
  }, []);

  /**
   * Re-resolve the caller's identity from the server.
   *
   * The cached user object is a rendering convenience only. Roles can change or
   * be revoked after login, so the role that drives which dashboard renders is
   * confirmed against /auth/me rather than read from localStorage - which the
   * user can edit freely in any case.
   */
  const refreshUser = useCallback(async () => {
    if (!getStoredToken()) {
      setIsLoading(false);
      return;
    }
    try {
      const { data } = await api.getMe();
      applyUser({
        id: data.user_id,
        email: data.email,
        role: data.role,
        full_name: data.full_name,
      });
    } catch {
      // The interceptor already attempted a refresh; reaching here means the
      // session is genuinely gone.
      clearSession();
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [applyUser]);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  const loginWithResponse = useCallback(
    (data: AuthResponse) => {
      storeSession(data.access_token, data.refresh_token ?? null);
      setToken(data.access_token);
      applyUser({
        id: data.user_id,
        email: data.email,
        role: data.role,
        full_name: data.full_name,
      });
      setIsLoading(false);
    },
    [applyUser]
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role: user?.role ?? null,
        isAuthenticated: Boolean(token && user),
        isLoading,
        loginWithResponse,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
