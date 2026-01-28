import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if we have a stored user from a previous session
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);

    // Listen for global logout events (e.g. 401 from API)
    const handleLogout = () => {
      setUser(null);
      localStorage.removeItem('user');
    };

    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);
      // Backend expects application/x-www-form-urlencoded for OAuth2PasswordRequestForm
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      // Using api.post which handles Base URL and Cookies automatically
      const data = await api.post('auth/token', params);

      // Token is in HttpOnly cookie, store user info locally
      const userData = data.user;

      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      console.error('Error logging in:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const registerUser = async (email, password) => {
    try {
      setLoading(true);
      await api.post('auth/register', { email, password });
      return true;
    } catch (error) {
      console.error('Error registering:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signOut = () => {
    setUser(null);
    localStorage.removeItem('user');
    // Clear cookie by making a logout request (optional endpoint, not implemented in backend yet)
    // api.post('auth/logout').catch(() => {}); 
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, registerUser, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
