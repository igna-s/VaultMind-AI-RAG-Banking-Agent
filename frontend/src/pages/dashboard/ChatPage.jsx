import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User as UserIcon, Loader2, Paperclip, Plus, MessageSquare, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { FileUploader } from '../../components/dashboard/FileUploader';
import { useLocation } from 'react-router-dom';
export default function ChatPage() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [sessions, setSessions] = useState([]);
    const [activeSession, setActiveSession] = useState(null);
    const [showUploader, setShowUploader] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);

    const scrollRef = useRef(null);
    const { user } = useAuth();

    // Fetch sessions on mount
    const fetchSessions = async () => {
        try {
            const data = await api.get('/chat/sessions');
            setSessions(data);
        } catch (error) {
            console.error("Failed to fetch sessions:", error);
        }
    };

    useEffect(() => {
        fetchSessions();
    }, []);

    const location = useLocation();

    // Auto-send if initialQuery exists
    useEffect(() => {
        if (location.state?.initialQuery) {
            setInput(location.state.initialQuery);
            // Optional: Auto-submit
            // handleSend(null, location.state.initialQuery);
            // But for now let's just pre-fill
        }
    }, [location.state]);

    // Cleanup state after use so it doesn't persist on reload/navigation
    useEffect(() => {
        if (location.state?.initialQuery) {
            window.history.replaceState({}, document.title);
        }
    }, []);

    // Load history when activeSession changes
    useEffect(() => {
        const loadHistory = async () => {
            if (!activeSession) {
                // If we have a pre-filled input and no session, we just wait for user to send
                if (!location.state?.initialQuery) {
                    setMessages([]);
                } else {
                    setMessages([]); // Start clean for new query
                }
                return;
            }

            try {
                setLoadingHistory(true);
                const data = await api.get(`/chat/sessions/${activeSession}`);
                setMessages(data.messages);
            } catch (error) {
                console.error("Failed to load history:", error);
            } finally {
                setLoadingHistory(false);
            }
        };

        loadHistory();
    }, [activeSession]);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping]);

    const handleNewChat = () => {
        setActiveSession(null);
        setMessages([]);
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { id: Date.now(), text: input, sender: 'user', timestamp: new Date() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        try {
            const data = await api.post('/chat', {
                query: userMsg.text,
                session_id: activeSession
            });

            // If we were in a new chat, the backend created a session
            if (!activeSession && data.session_id) {
                setActiveSession(data.session_id);
            }

            // Refetch sessions to update order/dates
            fetchSessions();

            const aiMsg = {
                id: Date.now() + 1,
                text: data.response,
                sender: 'ai',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMsg]);
        } catch (error) {
            console.error("Chat Error:", error);
            const errorMsg = {
                id: Date.now() + 1,
                text: `Error: ${error.message}`,
                sender: 'ai',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="flex h-full bg-[#0f0e17] text-white overflow-hidden rounded-2xl border border-white/5">
            {/* Left Sidebar - History */}
            <div className="w-64 border-r border-white/5 bg-[#161420] flex flex-col hidden md:flex">
                <div className="p-4 border-b border-white/5">
                    <button
                        onClick={handleNewChat}
                        className="w-full flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl transition-all font-medium text-sm"
                    >
                        <Plus className="w-4 h-4" />
                        New Chat
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {sessions.length === 0 ? (
                        <div className="p-4 text-center text-xs text-white/30">
                            No recent chats
                        </div>
                    ) : (
                        sessions.map(session => (
                            <button
                                key={session.id}
                                onClick={() => setActiveSession(session.id)}
                                className={`w-full text-left px-3 py-3 rounded-lg text-sm flex items-center gap-3 transition-colors ${activeSession === session.id
                                    ? 'bg-white/10 text-white'
                                    : 'text-white/60 hover:bg-white/5 hover:text-white'
                                    }`}
                            >
                                <MessageSquare className="w-4 h-4 opacity-70" />
                                <div className="truncate flex-1">
                                    <p className="truncate font-medium">{session.title}</p>
                                    <p className="text-xs text-white/30">{session.date}</p>
                                </div>
                            </button>
                        ))
                    )}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col relative">
                {/* Header */}
                <div className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#161420]/50 backdrop-blur-sm">
                    <div className="flex items-center gap-3">
                        <Bot className="w-5 h-5 text-indigo-400" />
                        <span className="font-semibold">VaultMind AI</span>
                    </div>
                    <button
                        onClick={() => setShowUploader(!showUploader)}
                        className={`p-2 rounded-lg transition-colors ${showUploader ? 'bg-white/10 text-white' : 'text-white/60 hover:bg-white/5'}`}
                        title="Toggle Documents"
                    >
                        <Paperclip className="w-5 h-5" />
                    </button>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6" ref={scrollRef}>
                    {messages.length === 0 && !loadingHistory ? (
                        <div className="h-full flex flex-col items-center justify-center text-white/30 space-y-4">
                            <Bot className="w-12 h-12 opacity-20" />
                            <p className="text-sm">Start a conversation with VaultMind</p>
                        </div>
                    ) : (
                        messages.map((msg) => (
                            <motion.div
                                key={msg.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex items-start gap-4 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center border
                                    ${msg.sender === 'ai' ? 'bg-indigo-500/10 border-indigo-500/20' : 'bg-white/10 border-white/10'}`}>
                                    {msg.sender === 'ai' ? <Bot className="w-5 h-5 text-indigo-400" /> : <UserIcon className="w-5 h-5 text-white/70" />}
                                </div>

                                <div className={`max-w-[70%] rounded-2xl p-4 text-sm leading-relaxed shadow-sm
                                    ${msg.sender === 'ai'
                                        ? 'bg-[#1e1c29] border border-white/5 text-white/90 rounded-tl-none'
                                        : 'bg-indigo-600 text-white rounded-tr-none'
                                    }`}>
                                    {msg.text}
                                </div>
                            </motion.div>
                        ))
                    )}

                    {isTyping && (
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
                                <Bot className="w-5 h-5 text-indigo-400" />
                            </div>
                            <div className="bg-[#1e1c29] border border-white/5 px-4 py-3 rounded-2xl rounded-tl-none">
                                <Loader2 className="w-4 h-4 text-white/40 animate-spin" />
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-white/5 bg-[#161420]">
                    <div className="max-w-4xl mx-auto relative">
                        <form onSubmit={handleSend} className="relative">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Message VaultMind AI..."
                                className="w-full bg-[#0f0e17] border border-white/10 rounded-xl pl-5 pr-14 py-4 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-500/50 transition-all shadow-inner"
                            />
                            <button
                                type="submit"
                                disabled={!input.trim()}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </form>
                        <p className="text-center text-xs text-white/20 mt-2">
                            AI responses may vary. Verify important information.
                        </p>
                    </div>
                </div>
            </div>

            {/* Right Panel - Uploads */}
            <AnimatePresence>
                {showUploader && (
                    <motion.div
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 320, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        className="border-l border-white/5 bg-[#161420] overflow-hidden flex flex-col"
                    >
                        <div className="p-4 border-b border-white/5 font-medium flex items-center justify-between">
                            <span>Documents</span>
                            <button onClick={() => setShowUploader(false)} className="hover:text-white/70">
                                <span className="sr-only">Close</span>
                                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
                            </button>
                        </div>
                        <div className="p-4 flex-1 overflow-y-auto">
                            <FileUploader />

                            <div className="mt-6">
                                <h4 className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-3">Context</h4>
                                <div className="space-y-2">
                                    <div className="p-3 bg-white/5 rounded-lg border border-white/5 text-xs text-white/60">
                                        No active documents in this session.
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
