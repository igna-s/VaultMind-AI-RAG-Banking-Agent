import { createContext, useContext, useState, useEffect } from 'react';

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
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);
      // Backend expects application/x-www-form-urlencoded for OAuth2PasswordRequestForm
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const response = await fetch('/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params,
        credentials: 'include' // Important for cookies
      });

      // Read response text first to avoid JSON parse errors on empty responses
      const responseText = await response.text();

      if (!response.ok) {
        let errorMessage = 'Login failed';
        if (responseText) {
          try {
            const err = JSON.parse(responseText);
            errorMessage = err.detail || errorMessage;
          } catch {
            errorMessage = responseText || errorMessage;
          }
        }
        throw new Error(errorMessage);
      }

      // Token is in HttpOnly cookie, store user info locally
      const userData = { email };
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      console.error('Error logging in:', error);
      // Don't alert on 500 if handled by UI, but for now specific alert
      if (error.message.includes('500')) {
        alert('Server Error (500). Please check backend connection.');
      } else {
        alert('Login failed: ' + error.message);
      }
      throw error;
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

      return true;
    } catch (error) {
      console.error('Error registering:', error);
      alert('Registration failed: ' + error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signOut = () => {
    setUser(null);
    localStorage.removeItem('user');
    // Clear cookie by making a logout request (optional endpoint)
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, registerUser, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
