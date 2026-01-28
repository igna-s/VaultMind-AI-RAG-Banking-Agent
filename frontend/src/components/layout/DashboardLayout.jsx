import { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LayoutDashboard, MessageSquare, Settings, LogOut, User, Menu, Database, Users } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const DashboardLayout = () => {
  const { signOut, user } = useAuth();
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  const navItems = user?.role === 'admin' ? [
    { icon: LayoutDashboard, label: 'Overview', path: '/dashboard' },
    { icon: Database, label: 'Knowledge Base', path: '/dashboard/documents' },
    { icon: Users, label: 'Users', path: '/dashboard/users' },
  ] : [
    { icon: MessageSquare, label: 'My Chat', path: '/dashboard/chat' },
    { icon: LayoutDashboard, label: 'History', path: '/dashboard' },
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
            <span className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              VaultMind AI
            </span>
          )}
          <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-white/10 rounded-lg">
            <Menu className="w-5 h-5 text-white/70" />
          </button>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          {navItems.map((item) => (
            <NavLink
              key={item.label}
              to={item.path}
              end={item.path === '/dashboard'}
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
          {/* Breadcrumbs or Title could go here, for now empty or simple branding */}
          <div className="flex items-center gap-2 text-white/40 text-sm">
            <span>Dashboard</span>
            <span>/</span>
            <span className="text-white/80">Overview</span>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8 relative">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
