"use client";

import { createContext, useContext, useMemo, useState } from "react";
import type { User } from "@/features/auth/types";
import { clearAuthToken, getAuthToken, setAuthToken } from "@/lib/auth-token";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getAuthToken());
  const [user, setUser] = useState<User | null>(null);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      login: (nextToken, nextUser) => {
        setAuthToken(nextToken);
        setToken(nextToken);
        setUser(nextUser);
      },
      logout: () => {
        clearAuthToken();
        setToken(null);
        setUser(null);
      },
    }),
    [token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
}
