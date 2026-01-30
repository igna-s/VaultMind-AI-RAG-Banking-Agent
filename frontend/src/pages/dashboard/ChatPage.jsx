import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Bot, User as UserIcon, Loader2, Paperclip, Plus, MessageSquare, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { FileUploader } from '../../components/dashboard/FileUploader';
import { useLocation } from 'react-router-dom';

const ReasoningSteps = ({ steps, status }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const bottomRef = useRef(null);
    const stepsArray = steps || [];

    useEffect(() => {
        if (isExpanded && bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [stepsArray.length, isExpanded]);

    // Get display text for the latest status
    const getLatestText = () => {
        if (stepsArray.length > 0) {
            const lastStep = stepsArray[stepsArray.length - 1];
            return typeof lastStep === 'object' ? (lastStep.content || lastStep.status || lastStep.thought) : lastStep;
        }
        return status || 'Processing...';
    };

    return (
        <div className="flex flex-col gap-2 mb-2 bg-black/20 p-3 rounded-lg border border-white/5 cursor-pointer hover:bg-black/30 transition-colors group"
            onClick={() => setIsExpanded(!isExpanded)}>

            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Loader2 className={`w-3 h-3 text-indigo-400 ${status ? 'animate-spin' : ''}`} />
                    <span className="text-[10px] font-bold text-indigo-300/60 uppercase tracking-widest group-hover:text-indigo-300 transition-colors">
                        Reasoning Process {stepsArray.length > 0 ? `(${stepsArray.length})` : ''}
                    </span>
                </div>
                {stepsArray.length > 0 && (
                    <span className="text-[10px] text-white/30 group-hover:text-white/50">{isExpanded ? 'Collapse' : 'Expand'}</span>
                )}
            </div>

            {isExpanded && stepsArray.length > 0 ? (
                <div className="space-y-1.5 mt-2">
                    {stepsArray.map((step, idx) => {
                        const stepText = typeof step === 'object' ? (step.content || step.status || step.thought || JSON.stringify(step)) : step;
                        return (
                            <div key={idx} className="flex items-start gap-2 text-xs text-indigo-100/80 font-mono tracking-tight leading-relaxed animate-in fade-in slide-in-from-top-1 duration-200">
                                <span className="text-white/20 text-[10px] mt-0.5 select-none w-4 text-right">{(idx + 1)}</span>
                                <span className="flex-1 opacity-90">{stepText}</span>
                            </div>
                        );
                    })}
                    <div ref={bottomRef} />
                </div>
            ) : (
                <div className="mt-1 flex items-start gap-2 text-xs text-indigo-100/60 font-mono animate-in fade-in duration-200">
                    <span className="text-white/20 text-[10px] mt-0.5 w-4 text-right">{stepsArray.length > 0 ? 'Latest:' : ''}</span>
                    <span className="line-clamp-1 italic">{getLatestText()}</span>
                </div>
            )}
        </div>
    );
};


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
                if (!location.state?.initialQuery) {
                    setMessages([]);
                } else {
                    setMessages([]);
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
        const typingId = Date.now() + 1;

        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    query: userMsg.text,
                    session_id: activeSession
                })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiMsg = { id: typingId, text: '', sender: 'ai', timestamp: new Date(), status: 'Starting...', steps: [] };
            setMessages(prev => [...prev, aiMsg]);

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);

                        if (data.type === 'status') {
                            setMessages(prev => prev.map(msg => {
                                if (msg.id === typingId) {
                                    const newSteps = [...(msg.steps || []), data.content];
                                    return { ...msg, status: data.content, steps: newSteps };
                                }
                                return msg;
                            }));
                        } else if (data.type === 'answer') {
                            setMessages(prev => prev.map(msg =>
                                msg.id === typingId ? {
                                    ...msg,
                                    text: data.response,
                                    status: null,
                                    // Always use backend steps - they now include all status messages
                                    steps: data.reasoning_data?.steps || msg.steps || []
                                } : msg
                            ));

                            if (!activeSession && data.session_id) {
                                setActiveSession(data.session_id);
                            }
                            fetchSessions();
                        } else if (data.type === 'error') {
                            // Sanitize error - don't show technical details
                            const safeError = 'Hubo un problema al procesar tu solicitud. Por favor, intenta de nuevo.';
                            setMessages(prev => prev.map(msg =>
                                msg.id === typingId ? { ...msg, text: safeError, status: null } : msg
                            ));
                        }
                    } catch (e) {
                        console.error("JSON Parse Error", e);
                    }
                }
            }

        } catch (error) {
            console.error("Chat Error:", error);
            // Sanitize error - don't expose technical details to user
            const errorMsg = {
                id: Date.now() + 2,
                text: 'Lo siento, hubo un error de conexión. Por favor, intenta de nuevo.',
                sender: 'ai',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
            setMessages(prev => prev.map(msg =>
                msg.id === typingId && msg.status ? { ...msg, status: null } : msg
            ));
        }
    };

    return (
        <div className="flex h-full bg-[#0f0e17] text-white overflow-hidden rounded-2xl border border-white/5">
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

            <div className="flex-1 flex flex-col relative">
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
                                    <div className="space-y-3">
                                        {/* Show reasoning steps if we have any OR if still processing */}
                                        {(msg.steps?.length > 0 || msg.status) && (
                                            <ReasoningSteps steps={msg.steps || []} status={msg.status} />
                                        )}

                                        {/* Only show text content when NOT currently processing (no status) */}
                                        {!msg.status && msg.text && (
                                            <div className="prose prose-invert prose-sm max-w-none leading-relaxed text-gray-100">
                                                <ReactMarkdown
                                                    remarkPlugins={[remarkGfm]}
                                                    components={{
                                                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                                                        a: ({ node, ...props }) => <a className="text-indigo-400 hover:text-indigo-300 underline" target="_blank" rel="noopener noreferrer" {...props} />,
                                                        ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                                                        ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                                                        li: ({ node, ...props }) => <li className="pl-1" {...props} />,
                                                        h1: ({ node, ...props }) => <h1 className="text-xl font-bold mb-3 mt-4 text-white" {...props} />,
                                                        h2: ({ node, ...props }) => <h2 className="text-lg font-bold mb-2 mt-4 text-indigo-200" {...props} />,
                                                        h3: ({ node, ...props }) => <h3 className="text-base font-bold mb-2 mt-3 text-indigo-300" {...props} />,
                                                        code: ({ node, inline, className, children, ...props }) => {
                                                            return inline ?
                                                                <code className="bg-white/10 px-1 py-0.5 rounded text-xs font-mono text-indigo-200" {...props}>{children}</code> :
                                                                <code className="block bg-black/30 p-3 rounded-lg text-xs font-mono my-2 overflow-x-auto text-indigo-100" {...props}>{children}</code>
                                                        }
                                                    }}
                                                >
                                                    {msg.text}
                                                </ReactMarkdown>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    )}


                    {/* Removed duplicate typing indicator - already shown in message status */}
                </div>

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
