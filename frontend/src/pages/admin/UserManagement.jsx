import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Search, Edit2, Check, X, Shield } from 'lucide-react';

export default function UserManagement() {
    const [users, setUsers] = useState([]);
    const [kbs, setKbs] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [search, setSearch] = useState('');
    const [isLoading, setIsLoading] = useState(true);

    const API_URL = import.meta.env.VITE_API_BASE_URL || '';

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const [usersRes, kbsRes] = await Promise.all([
                fetch(`${API_URL}/admin/users`, { credentials: 'include' }),
                fetch(`${API_URL}/admin/knowledge_bases`, { credentials: 'include' })
            ]);

            if (usersRes.ok) setUsers(await usersRes.json());
            if (kbsRes.ok) setKbs(await kbsRes.json());
        } catch (error) {
            console.error("Failed to fetch admin data", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSaveUser = async () => {
        if (!selectedUser) return;

        // Update KBs
        try {
            const kbIds = selectedUser.knowledge_bases.map(kb => kb.id);
            const res = await fetch(`${API_URL}/admin/users/${selectedUser.id}/knowledge_bases`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ kb_ids: kbIds }) // The backend expects kb_ids list, wait, endpoint argument query param?
                // My backend was: def update_user_kbs(user_id: int, kb_ids: List[int], ...)
                // FastAPI body expects JSON with 'kb_ids' key if defined as such, OR query params.
                // Let's check backend implementation.
            });

            if (res.ok) {
                fetchData();
                setSelectedUser(null);
            }
        } catch (error) {
            console.error("Failed to update user", error);
        }
    };

    // Helper to toggle KB in modal
    const toggleKbResponse = (kbId) => {
        // We are modifying selectedUser state object locally before save
        const currentIds = selectedUser.knowledge_bases.map(k => k.id);
        let newKbs;
        if (currentIds.includes(kbId)) {
            newKbs = selectedUser.knowledge_bases.filter(k => k.id !== kbId);
        } else {
            const kbToAdd = kbs.find(k => k.id === kbId);
            newKbs = [...selectedUser.knowledge_bases, { id: kbAdj, name: kbToAdd.name }]; // Helper needed
            // Actually simpler: just re-find from kbs list
            newKbs = [...selectedUser.knowledge_bases, kbs.find(k => k.id === kbId)];
        }
        setSelectedUser({ ...selectedUser, knowledge_bases: newKbs });
    };

    const filteredUsers = users.filter(u => u.email.toLowerCase().includes(search.toLowerCase()));

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">User Management</h1>
                    <p className="text-white/50 mt-2">Manage access and Knowledge Base assignments.</p>
                </div>
                <div className="relative">
                    <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                    <input
                        type="text"
                        placeholder="Search users..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        className="pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-500/50"
                    />
                </div>
            </header>

            <div className="glass-panel overflow-hidden rounded-2xl border border-white/5">
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
                            <tr><td colSpan="4" className="p-8 text-center text-white/40">Loading...</td></tr>
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
            </div>

            {/* Edit Modal */}
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
