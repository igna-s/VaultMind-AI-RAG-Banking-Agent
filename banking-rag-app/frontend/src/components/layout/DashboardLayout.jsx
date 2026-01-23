import { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, MessageSquare, Settings, LogOut, User, Menu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { ChatPanel } from '../feedback/ChatPanel';

export const DashboardLayout = () => {
  const { signOut, user } = useAuth();
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isChatOpen, setChatOpen] = useState(true);

  const navItems = [
    { icon: LayoutDashboard, label: 'Overview', path: '/dashboard' },
    { icon: User, label: 'Profile', path: '/dashboard/profile' },
    { icon: Settings, label: 'Settings', path: '/dashboard/settings' },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-[rgb(var(--bg-deep))]">
      {/* Sidebar */}
      <motion.aside 
        initial={{ width: 280 }}
        animate={{ width: isSidebarOpen ? 280 : 80 }}
        className="glass-panel border-r border-white/5 relative z-20 flex flex-col transition-all duration-300"
      >
        <div className="p-6 flex items-center justify-between">
            {isSidebarOpen && (
                <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                  SecureBank
                </span>
            )}
            <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-white/10 rounded-lg">
                <Menu className="w-5 h-5 text-white/70" />
            </button>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-xl transition-all
                ${isActive ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30' : 'text-white/60 hover:bg-white/5 hover:text-white'}
              `}
            >
              <item.icon className="w-5 h-5" />
              {isSidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-white/5">
          <button 
            onClick={signOut}
            className="flex items-center gap-3 w-full px-4 py-3 text-red-400 hover:bg-red-500/10 rounded-xl transition-all"
          >
            <LogOut className="w-5 h-5" />
            {isSidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full relative overflow-hidden">
        {/* Topbar */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-black/20 backdrop-blur-sm">
            <h2 className="text-white/80 font-medium">Welcome back, {user?.email}</h2>
            <button 
                onClick={() => setChatOpen(!isChatOpen)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${isChatOpen ? 'bg-indigo-600 shadow-indigo-500/20 shadow-lg text-white' : 'bg-white/5 text-white/70'}`}
            >
                <MessageSquare className="w-4 h-4" />
                <span>AI Assistant</span>
            </button>
        </header>

        <div className="flex-1 overflow-auto p-8 relative">
           <Outlet />
        </div>

        {/* Chat Panel Overlay/Sidebar */}
        <AnimatePresence>
            {isChatOpen && (
                <motion.div
                    initial={{ x: 400, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: 400, opacity: 0 }}
                    transition={{ type: "spring", damping: 25, stiffness: 200 }}
                    className="absolute top-0 right-0 h-full w-[400px] glass-panel border-l border-white/10 shadow-2xl z-30 flex flex-col"
                >
                    <ChatPanel onClose={() => setChatOpen(false)} />
                </motion.div>
            )}
        </AnimatePresence>
      </main>
    </div>
  );
};
