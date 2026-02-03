import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { Database, Users, MessageSquare, Zap, Activity, FileText, ArrowRight, Clock } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../../services/api';

export default function Overview() {
    const { user } = useAuth();
    const isAdmin = user?.role === 'admin';
    const navigate = useNavigate();

    const [stats, setStats] = useState({ documents: 0, users: 0, queries: 0 });
    const [loading, setLoading] = useState(true);
    const [recentSessions, setRecentSessions] = useState([]);

    const [activityData, setActivityData] = useState([]);

    useEffect(() => {
        if (isAdmin) {
            // Fetch Overview Stats
            api.get('/stats/overview')
                .then(data => {
                    setStats(data);
                    setLoading(false);
                })
                .catch(err => {
                    console.error("Failed to fetch stats", err);
                    setLoading(false);
                });

            // Fetch Activity Graph
            api.get('/stats/activity')
                .then(data => setActivityData(data))
                .catch(console.error);
        } else {
            // Fetch recent sessions for user
            api.get('/chat/sessions')
                .then(data => setRecentSessions(data.slice(0, 4))) // Get top 4
                .catch(console.error);
        }
    }, [isAdmin]);

    // Helper to get bar heights from token data
    const getDynamicMaxTokens = () => {
        if (!activityData || activityData.length === 0) return 1000;
        // Correct scaling for stacked bars: Max of (Groq + Retriever)
        const maxVal = Math.max(...activityData.map(d => (d.groq || 0) + (d.retriever || 0)));
        return maxVal > 100 ? maxVal : 100; // Minimum scale 100
    };

    const getTokenData = (index) => {
        if (!activityData || activityData.length === 0) return { groq: 5, retriever: 5, rawGroq: 0, rawRetriever: 0 };

        // Backend now returns exactly 24 data points
        const dataPoint = activityData[index];
        if (!dataPoint) return { groq: 5, retriever: 5, rawGroq: 0, rawRetriever: 0 };

        const maxTokens = getDynamicMaxTokens();
        const rawGroq = dataPoint.groq || 0;
        const rawRetriever = dataPoint.retriever || 0;

        return {
            groq: Math.min(rawGroq / maxTokens * 100, 100), // Height %
            retriever: Math.min(rawRetriever / maxTokens * 100, 100), // Height %
            rawGroq,
            rawRetriever
        };
    };


    const handlePromptClick = (text) => {
        navigate('/dashboard/chat', { state: { initialQuery: text } });
    };

    // Admin View Data
    const adminStats = [
        { icon: Database, label: 'Documents Indexed', value: loading ? '...' : stats.documents, color: 'from-emerald-400 to-green-500' },
        { icon: Users, label: 'Active Users', value: loading ? '...' : stats.users, color: 'from-blue-400 to-indigo-500' },
        { icon: MessageSquare, label: 'Queries Today', value: loading ? '...' : stats.queries, color: 'from-purple-400 to-pink-500' },
    ];

    const suggestedPrompts = [
        "Summarize the key findings in the latest report.",
        "What are the compliance requirements for this project?",
        "Find any mention of 'deadline' in the documents.",
        "Explain the technical architecture described."
    ];

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-10">
            {/* Header ... */}
            <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <motion.h1
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-4xl md:text-5xl font-bold text-white tracking-tight"
                    >
                        {isAdmin ? 'System Command' : <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">Hello, {user?.email?.split('@')[0] || 'User'}</span>}
                    </motion.h1>
                    <p className="text-white/50 mt-3 text-lg font-light">
                        {isAdmin
                            ? "Overview of the RAG Knowledge Engine status."
                            : "Your AI Knowledge Assistant is ready. Access your organization's intelligence."}
                    </p>
                </div>
            </header>

            {isAdmin ? (
                /* Admin View */
                <>
                    {/* Stats Row */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {adminStats.map((stat, i) => (
                            <motion.div
                                key={stat.label}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="glass-panel p-6 rounded-2xl relative overflow-hidden group hover:border-white/10 transition-colors"
                            >
                                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${stat.color} opacity-10 rounded-full blur-3xl group-hover:opacity-20 transition-opacity`} />
                                <div className="relative z-10">
                                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} p-2.5 mb-4 shadow-lg shadow-black/20`}>
                                        <stat.icon className="w-full h-full text-white" />
                                    </div>
                                    <h3 className="text-4xl font-bold text-white tracking-tight">{stat.value}</h3>
                                    <p className="text-white/60 font-medium mt-1 uppercase text-xs tracking-wider">{stat.label}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Token Usage Chart */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="glass-panel p-8 rounded-3xl min-h-[300px] flex flex-col border border-white/5 bg-gradient-to-b from-white/5 to-transparent"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                                    <Activity className="w-5 h-5 text-emerald-400" />
                                    Token Usage (24h)
                                </h3>
                                <div className="flex gap-4 text-xs">
                                    <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-purple-500"></span> Groq (LLM)</span>
                                    <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-500"></span> Retriever</span>
                                </div>
                            </div>

                            <div className="flex h-40 mt-4 relative">
                                {/* Y-Axis Scale */}
                                <div className="flex flex-col justify-between text-xs text-white/30 font-mono pr-2 h-full text-right w-12 border-r border-white/10 py-1">
                                    <span>{getDynamicMaxTokens()}</span>
                                    <span>{Math.round(getDynamicMaxTokens() / 2)}</span>
                                    <span>0</span>
                                </div>

                                {/* Chart Area */}
                                <div className="flex-1 flex items-end justify-center gap-1 h-full px-4 overflow-hidden relative">

                                    {[...Array(24)].map((_, i) => {
                                        const data = getTokenData(i);
                                        // Make sure min height is used if value > 0 but small, to ensure visibility
                                        const groqHeight = data.rawGroq > 0 ? Math.max(data.groq, 2) : 0;
                                        const retHeight = data.rawRetriever > 0 ? Math.max(data.retriever, 2) : 0;

                                        return (
                                            <div key={i} className="w-full h-full flex flex-col justify-end items-center gap-0.5" style={{ maxWidth: '16px' }}>
                                                <div
                                                    className="w-full bg-purple-500/60 rounded-t-sm transition-all duration-1000"
                                                    style={{ height: `${groqHeight}%` }}
                                                    title={`Groq: ${data.rawGroq} tokens`}
                                                />
                                                <div
                                                    className="w-full bg-emerald-500/60 rounded-t-sm transition-all duration-1000"
                                                    style={{ height: `${retHeight}%` }}
                                                    title={`Retriever: ${data.rawRetriever} tokens`}
                                                />
                                            </div>
                                        );
                                    })}
                                    <div className="absolute inset-x-0 bottom-0 h-px bg-white/10" />
                                </div>
                            </div>

                            <div className="mt-4 flex justify-between text-xs text-white/30 font-mono uppercase tracking-wider">
                                <span>24h Ago</span>
                                <span>12h Ago</span>
                                <span>Now</span>
                            </div>
                        </motion.div>

                        {/* Quick Actions */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.2 }}
                            className="grid grid-rows-2 gap-4"
                        >
                            <Link to="/dashboard/documents" className="glass-panel p-8 rounded-3xl hover:bg-white/5 transition-all group border border-white/5 flex items-center justify-between">
                                <div className="flex items-center gap-6">
                                    <div className="w-14 h-14 rounded-2xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform shadow-inner">
                                        <FileText className="w-7 h-7" />
                                    </div>
                                    <div>
                                        <h4 className="text-xl font-bold text-white">Knowledge Base</h4>
                                        <p className="text-white/50 text-sm mt-1">Manage vector store documents</p>
                                    </div>
                                </div>
                                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors">
                                    <ArrowRight className="w-5 h-5 text-white/60" />
                                </div>
                            </Link>

                            <Link to="/dashboard/users" className="glass-panel p-8 rounded-3xl hover:bg-white/5 transition-all group border border-white/5 flex items-center justify-between">
                                <div className="flex items-center gap-6">
                                    <div className="w-14 h-14 rounded-2xl bg-pink-500/20 flex items-center justify-center text-pink-400 group-hover:scale-110 transition-transform shadow-inner">
                                        <Users className="w-7 h-7" />
                                    </div>
                                    <div>
                                        <h4 className="text-xl font-bold text-white">Users & Access</h4>
                                        <p className="text-white/50 text-sm mt-1">Manage roles and permissions</p>
                                    </div>
                                </div>
                                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors">
                                    <ArrowRight className="w-5 h-5 text-white/60" />
                                </div>
                            </Link>
                        </motion.div>
                    </div>
                </>
            ) : (
                /* User View */
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Main Action Area */}
                    <div className="lg:col-span-8 space-y-8">
                        {/* New Chat Hero */}
                        <motion.div
                            className="element-glass p-10 rounded-[2rem] relative overflow-hidden border border-indigo-500/20 group"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/2 group-hover:bg-indigo-600/30 transition-colors duration-700" />

                            <div className="relative z-10">
                                <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center mb-8 backdrop-blur-md border border-white/20 shadow-xl">
                                    <Zap className="w-8 h-8 text-yellow-300" />
                                </div>
                                <h2 className="text-3xl font-bold text-white mb-4">Start a new conversation</h2>
                                <p className="text-white/60 mb-10 max-w-lg leading-relaxed text-lg">
                                    VaultMind is connected to your secure knowledge base. Ask me to analyze documents, extract data, or summarize meetings.
                                </p>

                                <div className="flex flex-wrap gap-3">
                                    {suggestedPrompts.map((query, i) => (
                                        <button
                                            key={i}
                                            onClick={() => handlePromptClick(query)}
                                            className="px-5 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white/80 text-sm transition-all hover:text-white hover:border-white/30 hover:shadow-lg hover:-translate-y-0.5"
                                        >
                                            <span className="opacity-50 mr-2">✨</span>
                                            {query}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    </div>

                    {/* Sidebar / Recent */}
                    <div className="lg:col-span-4 space-y-6">
                        <div className="flex items-center justify-between px-2">
                            <h3 className="text-white font-semibold flex items-center gap-2">
                                <Clock className="w-5 h-5 text-indigo-400" />
                                Jump back in
                            </h3>
                            <Link to="/dashboard/chat" className="text-xs text-white/40 hover:text-white transition-colors">See all</Link>
                        </div>

                        <div className="space-y-4">
                            {recentSessions.length === 0 ? (
                                <div className="p-8 rounded-3xl glass-panel border border-white/5 border-dashed flex flex-col items-center justify-center text-center">
                                    <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-3">
                                        <MessageSquare className="w-5 h-5 text-white/20" />
                                    </div>
                                    <p className="text-white/40 text-sm">No recent activity found.</p>
                                </div>
                            ) : (
                                recentSessions.map((session, i) => (
                                    <motion.div
                                        key={session.id}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: i * 0.1 }}
                                    >
                                        <Link
                                            to="/dashboard/chat"
                                            className="flex flex-col p-5 rounded-3xl glass-panel hover:bg-white/5 hover:border-indigo-500/30 border border-white/5 transition-all cursor-pointer group"
                                        >
                                            <div className="flex items-start justify-between mb-2">
                                                <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 group-hover:bg-indigo-500/20 group-hover:text-indigo-300 transition-colors">
                                                    <MessageSquare className="w-5 h-5" />
                                                </div>
                                                <span className="text-xs font-mono text-white/30 bg-white/5 px-2 py-1 rounded-lg">{session.date.split(' ')[0]}</span>
                                            </div>
                                            <h4 className="text-white/90 font-medium truncate pr-4 text-lg">{session.title}</h4>
                                            <p className="text-white/40 text-sm mt-1 line-clamp-2">
                                                Continue conversation...
                                            </p>
                                        </Link>
                                    </motion.div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
