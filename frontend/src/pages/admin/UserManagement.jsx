import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Search, Edit2, Check, X, Shield, FileText, AlertTriangle, Terminal } from 'lucide-react';

export default function UserManagement() {

    const [activeTab, setActiveTab] = useState('users'); // 'users', 'logs', 'errors'

    // Data States
    const [users, setUsers] = useState([]);
    const [kbs, setKbs] = useState([]);
    const [userLogs, setUserLogs] = useState([]);
    const [errorLogs, setErrorLogs] = useState([]);

    const [selectedUser, setSelectedUser] = useState(null);
    const [search, setSearch] = useState('');
    const [isLoading, setIsLoading] = useState(true);

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    const fetchData = useCallback(async () => {
        setIsLoading(true);
        try {
            if (activeTab === 'users') {
                const [usersRes, kbsRes] = await Promise.all([
                    fetch(`${API_URL}/admin/users`, { credentials: 'include' }),
                    fetch(`${API_URL}/admin/knowledge_bases`, { credentials: 'include' })
                ]);
                if (usersRes.ok) setUsers(await usersRes.json());
                if (kbsRes.ok) setKbs(await kbsRes.json());
            } else if (activeTab === 'logs') {
                const res = await fetch(`${API_URL}/admin/logs/users?limit=200`, { credentials: 'include' });
                if (res.ok) setUserLogs(await res.json());
            } else if (activeTab === 'errors') {
                const res = await fetch(`${API_URL}/admin/logs/errors?limit=100`, { credentials: 'include' });
                if (res.ok) setErrorLogs(await res.json());
            }
        } catch (error) {
            console.error("Failed to fetch admin data", error);
        } finally {
            setIsLoading(false);
        }
    }, [activeTab, API_URL]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleSaveUser = async () => {
        if (!selectedUser) return;

        try {
            // Update role if changed
            const roleRes = await fetch(`${API_URL}/admin/users/${selectedUser.id}/role`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ role: selectedUser.role })
            });

            const roleData = roleRes.ok ? await roleRes.json() : null;

            // If admin changed their own role, force logout to clear session
            // Must do this BEFORE KB update since we'll lose admin access
            if (roleData?.self_changed) {
                // Clear local storage and force re-login
                localStorage.removeItem('user');
                window.location.href = '/login';
                return;
            }

            // Update KBs (only if we still have admin access)
            const kbIds = selectedUser.knowledge_bases.map(kb => kb.id);
            const kbRes = await fetch(`${API_URL}/admin/users/${selectedUser.id}/knowledge_bases`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ kb_ids: kbIds })
            });

            if (roleRes.ok && kbRes.ok) {
                fetchData();
                setSelectedUser(null);
            }
        } catch (error) {
            console.error("Failed to update user", error);
        }
    };

    const filteredUsers = users.filter(u => u.email.toLowerCase().includes(search.toLowerCase()));

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Admin Console</h1>
                    <p className="text-white/50 mt-2">Manage users, view logs, and monitor system health.</p>
                </div>
            </header>

            {/* Tabs */}
            <div className="flex space-x-1 bg-white/5 p-1 rounded-xl w-fit border border-white/5">
                {[
                    { id: 'users', label: 'Users', icon: Users },
                    { id: 'logs', label: 'User Logs', icon: FileText },
                    { id: 'errors', label: 'System Errors', icon: AlertTriangle }
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                            ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20'
                            : 'text-white/60 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content Area */}
            <div className="glass-panel overflow-hidden rounded-2xl border border-white/5">

                {/* USERS TAB */}
                {activeTab === 'users' && (
                    <>
                        {/* Search Bar for Users */}
                        <div className="p-4 border-b border-white/5 flex justify-end">
                            <div className="relative">
                                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                                <input
                                    type="text"
                                    placeholder="Search users..."
                                    value={search}
                                    onChange={e => setSearch(e.target.value)}
                                    className="pl-9 pr-4 py-1.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-500/50"
                                />
                            </div>
                        </div>

                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-white/5 border-b border-white/5 text-xs uppercase tracking-wider text-white/40 font-medium">
                                    <th className="p-4">User</th>
                                    <th className="p-4">Role</th>
                                    <th className="p-4">Knowledge Bases</th>
                                    <th className="p-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {isLoading ? (
                                    <tr><td colSpan="4" className="p-8 text-center text-white/40">Loading users...</td></tr>
                                ) : filteredUsers.map(user => (
                                    <tr key={user.id} className="hover:bg-white/5 transition-colors group">
                                        <td className="p-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-xs">
                                                    {user.email[0].toUpperCase()}
                                                </div>
                                                <span className="text-white/80 font-medium">{user.email}</span>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs font-medium border ${user.role === 'admin'
                                                ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                                                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                                }`}>
                                                {user.role}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex flex-wrap gap-2">
                                                {user.knowledge_bases.length === 0 ? (
                                                    <span className="text-white/20 text-xs italic">None</span>
                                                ) : (
                                                    user.knowledge_bases.map(kb => (
                                                        <span key={kb.id} className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs">
                                                            {kb.name}
                                                        </span>
                                                    ))
                                                )}
                                            </div>
                                        </td>
                                        <td className="p-4 text-right">
                                            <button
                                                onClick={() => setSelectedUser(user)}
                                                className="p-2 hover:bg-white/10 rounded-lg text-white/40 hover:text-white transition-colors"
                                            >
                                                <Edit2 className="w-4 h-4" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </>
                )}

                {/* USER LOGS TAB */}
                {activeTab === 'logs' && (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-white/5 border-b border-white/5 text-xs uppercase tracking-wider text-white/40 font-medium">
                                    <th className="p-4">Time</th>
                                    <th className="p-4">User</th>
                                    <th className="p-4">Event</th>
                                    <th className="p-4">Details</th>
                                    <th className="p-4">IP</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {isLoading ? (
                                    <tr><td colSpan="5" className="p-8 text-center text-white/40">Loading logs...</td></tr>
                                ) : userLogs.map((log, idx) => (
                                    <tr key={log.id || idx} className="hover:bg-white/5 transition-colors">
                                        <td className="p-4 text-white/60 text-xs whitespace-nowrap font-mono">{formatDate(log.created_at)}</td>
                                        <td className="p-4 text-white/80 text-sm">{log.user_email}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-0.5 rounded text-xs font-bold border ${log.event === 'LOGIN' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                                log.event === 'TOKEN_USAGE' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                                    'bg-white/5 text-white/60 border-white/10'
                                                }`}>
                                                {log.event}
                                            </span>
                                        </td>
                                        <td className="p-4 text-white/60 text-xs font-mono">
                                            {JSON.stringify(log.details)}
                                        </td>
                                        <td className="p-4 text-white/40 text-xs font-mono">{log.ip_address || '-'}</td>
                                    </tr>
                                ))}
                                {!isLoading && userLogs.length === 0 && (
                                    <tr><td colSpan="5" className="p-8 text-center text-white/40">No logs found.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* SYSTEM ERRORS TAB */}
                {activeTab === 'errors' && (
                    <div className="bg-[#0f0e17] font-mono p-0">
                        <div className="border-b border-white/10 p-2 px-4 flex justify-between items-center bg-white/5">
                            <span className="text-xs text-red-400 font-bold flex items-center gap-2">
                                <Terminal className="w-3 h-3" /> System Exceptions
                            </span>
                            <span className="text-xs text-white/20">Last 100 errors</span>
                        </div>
                        <div className="divide-y divide-white/10">
                            {isLoading ? (
                                <div className="p-8 text-center text-white/40">Loading errors...</div>
                            ) : errorLogs.map(err => (
                                <div key={err.id} className="p-4 hover:bg-white/5 transition-colors group">
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-red-400 font-bold text-sm">{err.error_message}</span>
                                        <span className="text-white/30 text-xs whitespace-nowrap">{formatDate(err.created_at)}</span>
                                    </div>
                                    <div className="flex gap-4 mb-2 text-xs text-white/50">
                                        <span className="bg-white/10 px-1.5 rounded">{err.method}</span>
                                        <span className="text-indigo-400">{err.path}</span>
                                    </div>
                                    <div className="text-[10px] text-white/30 bg-black/30 p-2 rounded overflow-x-auto whitespace-pre font-mono">
                                        {err.stack_trace ? err.stack_trace.split('\n').slice(0, 5).join('\n') + '\n...' : 'No stack trace'}
                                    </div>
                                </div>
                            ))}
                            {!isLoading && errorLogs.length === 0 && (
                                <div className="p-12 text-center flex flex-col items-center">
                                    <Check className="w-12 h-12 text-emerald-500/20 mb-4" />
                                    <p className="text-emerald-500/50">No system errors recorded.</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Edit Modal (Same as before) */}
            <AnimatePresence>
                {selectedUser && (
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
                        onClick={() => setSelectedUser(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }}
                            className="bg-[#161420] border border-white/10 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="p-6 border-b border-white/10 flex justify-between items-center">
                                <h3 className="text-lg font-bold text-white">Edit User Access</h3>
                                <button onClick={() => setSelectedUser(null)} className="text-white/40 hover:text-white"><X className="w-5 h-5" /></button>
                            </div>

                            <div className="p-6 space-y-6">
                                <div>
                                    <label className="block text-xs font-semibold text-white/40 uppercase mb-2">User</label>
                                    <div className="p-3 bg-white/5 rounded-lg text-white/80">{selectedUser.email}</div>
                                </div>

                                <div>
                                    <label className="block text-xs font-semibold text-white/40 uppercase mb-3">Role</label>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => setSelectedUser({ ...selectedUser, role: 'user' })}
                                            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${selectedUser.role === 'user'
                                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                                                : 'bg-white/5 text-white/40 border border-white/10 hover:bg-white/10'
                                                }`}
                                        >
                                            User
                                        </button>
                                        <button
                                            onClick={() => setSelectedUser({ ...selectedUser, role: 'admin' })}
                                            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${selectedUser.role === 'admin'
                                                ? 'bg-purple-500/20 text-purple-400 border border-purple-500/40'
                                                : 'bg-white/5 text-white/40 border border-white/10 hover:bg-white/10'
                                                }`}
                                        >
                                            <Shield className="w-4 h-4 inline-block mr-1" />
                                            Admin
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-semibold text-white/40 uppercase mb-3">Assigned Knowledge Bases</label>
                                    <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                                        {kbs.map(kb => {
                                            const isSelected = selectedUser.knowledge_bases.some(k => k.id === kb.id);
                                            return (
                                                <div
                                                    key={kb.id}
                                                    onClick={() => {
                                                        const currentIds = selectedUser.knowledge_bases.map(k => k.id);
                                                        let newKbs;
                                                        if (currentIds.includes(kb.id)) {
                                                            newKbs = selectedUser.knowledge_bases.filter(k => k.id !== kb.id);
                                                        } else {
                                                            newKbs = [...selectedUser.knowledge_bases, { id: kb.id, name: kb.name }];
                                                        }
                                                        setSelectedUser({ ...selectedUser, knowledge_bases: newKbs });
                                                    }}
                                                    className={`p-3 rounded-xl border cursor-pointer flex items-center justify-between transition-all ${isSelected
                                                        ? 'bg-indigo-600/20 border-indigo-500/50 text-white'
                                                        : 'bg-white/5 border-white/5 text-white/60 hover:bg-white/10'
                                                        }`}
                                                >
                                                    <div className="flex flex-col">
                                                        <span className="font-medium text-sm">{kb.name}</span>
                                                        <span className="text-xs opacity-50">{kb.description || 'No description'}</span>
                                                    </div>
                                                    {isSelected && <Check className="w-4 h-4 text-indigo-400" />}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 border-t border-white/10 bg-white/5 flex justified-end gap-3 flex-row-reverse">
                                <button
                                    onClick={handleSaveUser}
                                    className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                                >
                                    Save Changes
                                </button>
                                <button
                                    onClick={() => setSelectedUser(null)}
                                    className="text-white/60 hover:text-white px-4 py-2 text-sm transition-colors"
                                >
                                    Cancel
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
