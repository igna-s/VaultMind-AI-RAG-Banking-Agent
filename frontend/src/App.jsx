import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/auth/Login';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { Profile, Settings } from './pages/dashboard/Placeholders';
import Overview from './pages/dashboard/Overview';
import ChatPage from './pages/dashboard/ChatPage';

import { ProtectedRoute } from './components/auth/ProtectedRoute';

import UserManagement from './pages/admin/UserManagement';
import KnowledgeManagement from './pages/admin/KnowledgeManagement';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Overview />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="documents" element={<KnowledgeManagement />} />
            <Route path="users" element={<UserManagement />} />
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
