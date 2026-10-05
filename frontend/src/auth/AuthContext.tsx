import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    logoutAllSessions,
    logoutSession,
    refreshSession,
} from "../api/authApi";
import {
    AuthContext,
    LOCAL_DEMO_MODE,
    type AuthContextValue,
    type AuthUser,
} from "./AuthState";

const DEMO_USER: AuthUser = {
    id: "local-demo",
    full_name: "Local Demo",
    email: "demo@localhost",
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(
        LOCAL_DEMO_MODE ? DEMO_USER : null,
    );
    const [accessToken, setAccessToken] = useState<string | null>(
        LOCAL_DEMO_MODE ? "local-demo-token" : null,
    );
    const [isLoading, setIsLoading] = useState(!LOCAL_DEMO_MODE);

    useEffect(() => {
        if (LOCAL_DEMO_MODE) {
            return;
        }

        void refreshSession()
            .then((result) => {
                setUser(result.user);
                setAccessToken(result.access_token);
            })
            .catch(() => {
                setUser(null);
                setAccessToken(null);
            })
            .finally(() => setIsLoading(false));
    }, []);

    const value = useMemo<AuthContextValue>(
        () => ({
            user,
            accessToken,
            isLoading,
            setAuthentication: (token, authenticatedUser) => {
                setAccessToken(token);
                setUser(authenticatedUser);
            },
            logout: async () => {
                try {
                    await logoutSession();
                } finally {
                    setAccessToken(null);
                    setUser(null);
                }
            },
            logoutAll: async () => {
                try {
                    await logoutAllSessions();
                } finally {
                    setAccessToken(null);
                    setUser(null);
                }
            },
        }),
        [user, accessToken, isLoading],
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
