import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, Plus, FileText, Trash2, Folder, Upload, Loader2 } from 'lucide-react';

export default function KnowledgeManagement() {
    const [kbs, setKbs] = useState([]);
    const [selectedKb, setSelectedKb] = useState(null);
    const [documents, setDocuments] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);

    // Create KB Form
    const [newKbName, setNewKbName] = useState('');
    const [newKbDesc, setNewKbDesc] = useState('');

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    const fetchKbs = useCallback(async () => {
        try {
            const res = await fetch(`${API_URL}/admin/knowledge_bases`, { credentials: 'include' });
            if (res.ok) setKbs(await res.json());
        } catch (e) {
            console.error(e);
        } finally {
            setIsLoading(false);
        }
    }, [API_URL]);

    const fetchDocuments = useCallback(async (kbId) => {
        try {
            const res = await fetch(`${API_URL}/admin/knowledge_bases/${kbId}/documents`, { credentials: 'include' });
            if (res.ok) setDocuments(await res.json());
        } catch (e) {
            console.error(e);
        }
    }, [API_URL]);

    useEffect(() => {
        fetchKbs();
    }, [fetchKbs]);

    useEffect(() => {
        if (selectedKb) {
            fetchDocuments(selectedKb.id);
        } else {
            setDocuments([]);
        }
    }, [selectedKb, fetchDocuments]);

    const handleCreateKb = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch(`${API_URL}/admin/knowledge_bases`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: newKbName,
                    description: newKbDesc || null
                })
            });

            if (res.ok) {
                fetchKbs();
                setShowCreateModal(false);
                setNewKbName('');
                setNewKbDesc('');
            }
        } catch (e) {
            console.error(e);
        }
    };

    // --- Uploader Logic ---
    const [uploading, setUploading] = useState(false);
    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file || !selectedKb) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('knowledge_base_id', selectedKb.id);

        try {
            const res = await fetch(`${API_URL}/admin/documents/upload`, {
                method: 'POST',
                credentials: 'include',
                body: formData
            });
            if (res.ok) {
                fetchDocuments(selectedKb.id);
                // Refresh KB list to update counts if we add that later
            }
        } catch (error) {
            console.error("Upload failed", error);
        } finally {
            setUploading(false);
        }
    };

    const toggleDefault = async () => {
        if (!selectedKb) return;
        try {
            const res = await fetch(`${API_URL}/admin/knowledge_bases/${selectedKb.id}/default`, {
                method: 'PATCH',
                credentials: 'include'
            });
            if (res.ok) {
                const updated = await res.json();
                setSelectedKb({ ...selectedKb, is_default: updated.is_default });
                fetchKbs(); // Refresh list
            }
        } catch (error) {
            console.error("Failed to toggle default", error);
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 h-full flex flex-col">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Knowledge Base Management</h1>
                    <p className="text-white/50 mt-2">Organize documents into groups for targeted access.</p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl flex items-center gap-2 font-medium transition-colors shadow-lg shadow-indigo-500/20"
                >
                    <Plus className="w-5 h-5" />
                    New Group
                </button>
            </header>

            <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-8 min-h-0">
                {/* Left: KB List */}
                <div className="glass-panel p-4 rounded-2xl border border-white/5 flex flex-col">
                    <h3 className="text-white/60 text-xs font-bold uppercase tracking-wider mb-4 px-2">Knowledge Groups</h3>
                    <div className="flex-1 overflow-y-auto space-y-2">
                        {kbs.map(kb => (
                            <button
                                key={kb.id}
                                onClick={() => setSelectedKb(kb)}
                                className={`w-full text-left p-4 rounded-xl border transition-all group ${selectedKb?.id === kb.id
                                    ? 'bg-indigo-600/20 border-indigo-500/50 text-white shadow-inner'
                                    : 'bg-white/5 border-transparent text-white/70 hover:bg-white/10'
                                    }`}
                            >
                                <div className="flex items-center gap-3">
                                    <Folder className={`w-5 h-5 ${selectedKb?.id === kb.id ? 'text-indigo-400' : 'text-white/40 group-hover:text-white/60'}`} />
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <h4 className="font-medium truncate">{kb.name}</h4>
                                            {kb.is_default && <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 rounded">Default</span>}
                                        </div>
                                        <p className="text-xs opacity-50 truncate">{kb.description || 'No description'}</p>
                                    </div>
                                    <span className="text-xs bg-black/20 px-2 py-1 rounded text-white/40">{kb.document_count || 0}</span>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Right: details */}
                <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/5 flex flex-col">
                    {!selectedKb ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-white/20">
                            <Database className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg">Select a Knowledge Group to manage</p>
                        </div>
                    ) : (
                        <>
                            <div className="flex items-center justify-between mb-6 pb-6 border-b border-white/5">
                                <div>
                                    <div className="flex items-center gap-3 mb-1">
                                        <h2 className="text-2xl font-bold text-white">{selectedKb.name}</h2>
                                        <button
                                            onClick={toggleDefault}
                                            className={`px-2 py-1 text-xs font-medium rounded transition-colors ${selectedKb.is_default
                                                ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
                                                : 'bg-white/10 text-white/40 hover:bg-white/20 hover:text-white/60'
                                                }`}
                                        >
                                            {selectedKb.is_default ? '★ Default' : '☆ Set as Default'}
                                        </button>
                                    </div>
                                    <p className="text-white/50">{selectedKb.description}</p>
                                </div>
                                <div className="relative overflow-hidden group">
                                    <input
                                        type="file"
                                        id="docUpload"
                                        className="hidden"
                                        onChange={handleFileUpload}
                                        disabled={uploading}
                                    />
                                    <label
                                        htmlFor="docUpload"
                                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium cursor-pointer transition-all ${uploading
                                            ? 'bg-white/10 text-white/40 cursor-wait'
                                            : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                                            }`}
                                    >
                                        {uploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
                                        {uploading ? 'Uploading...' : 'Upload Document'}
                                    </label>
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto">
                                {documents.length === 0 ? (
                                    <div className="text-center py-20">
                                        <p className="text-white/30 text-sm">No documents in this group yet.</p>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 gap-3">
                                        {documents.map(doc => (
                                            <div key={doc.id} className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/5 group hover:border-white/10 transition-colors">
                                                <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                                                    <FileText className="w-5 h-5" />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <h5 className="text-white/90 font-medium truncate">{doc.title}</h5>
                                                    <p className="text-xs text-white/40">{new Date(doc.created_at).toLocaleDateString()}</p>
                                                </div>
                                                {/* Delete button (not working yet but UI ready) */}
                                                <button className="p-2 text-white/20 hover:text-red-400 transition-colors">
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* Create Modal */}
            <AnimatePresence>
                {showCreateModal && (
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
                        onClick={() => setShowCreateModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }}
                            className="bg-[#161420] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4"
                            onClick={e => e.stopPropagation()}
                        >
                            <h3 className="text-xl font-bold text-white">New Knowledge Group</h3>
                            <form onSubmit={handleCreateKb} className="space-y-4">
                                <div>
                                    <label className="block text-xs font-semibold text-white/40 uppercase mb-2">Name</label>
                                    <input
                                        autoFocus
                                        type="text"
                                        value={newKbName}
                                        onChange={e => setNewKbName(e.target.value)}
                                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500/50"
                                        placeholder="e.g. Legal Documents"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-white/40 uppercase mb-2">Description</label>
                                    <input
                                        type="text"
                                        value={newKbDesc}
                                        onChange={e => setNewKbDesc(e.target.value)}
                                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500/50"
                                        placeholder="Optional description"
                                    />
                                </div>
                                <div className="flex justify-end gap-3 pt-2">
                                    <button
                                        type="button"
                                        onClick={() => setShowCreateModal(false)}
                                        className="px-4 py-2 rounded-lg text-white/60 hover:text-white transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                                    >
                                        Create Group
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
