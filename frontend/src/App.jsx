import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/auth/Login';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { Profile, Settings } from './pages/dashboard/Placeholders';

import Overview from './pages/dashboard/Overview';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<DashboardLayout />}>
             <Route index element={<Overview />} />
             <Route path="profile" element={<Profile />} />
             <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
