import { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) {
        setLoading(false);
        return;
    }

    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signInWithGoogle = async (email, password) => {
    try {
        setLoading(true);
        // Using relative path to use Vite Proxy
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) {
            throw new Error('Login failed');
        }

        const data = await response.json();
        setUser({ email, token: data.access_token });
    } catch (error) {
        console.error('Error logging in:', error);
        alert('Login failed: ' + error.message);
    } finally {
        setLoading(false);
    }
  };
  
  const registerUser = async (email, password) => {
      try {
        setLoading(true);
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Registration failed');
        }
        
        // Success - no auto login
        setLoading(false);
        return true;
      } catch (error) {
         console.error('Error registering:', error);
         alert('Registration failed: ' + error.message);
         setLoading(false);
         throw error;
      }
  };

  const signOut = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, signInWithGoogle, registerUser, signOut }}>
      {children}
    </AuthContext.Provider>
  );

};

export const useAuth = () => useContext(AuthContext);
