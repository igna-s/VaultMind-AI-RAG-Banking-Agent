import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

export const FileUploader = () => {
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [error, setError] = useState('');
    const { user } = useAuth();

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setError('');
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragging(true);
        } else if (e.type === 'dragleave') {
            setIsDragging(false);
        }
    }, []);

    const handleDrop = useCallback(async (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        setError('');

        const files = [...e.dataTransfer.files];
        if (files && files[0]) {
            await uploadFile(files[0]);
        }
    }, []);

    const handleFileInput = async (e) => {
        const files = [...e.target.files];
        setError('');
        if (files && files[0]) {
            await uploadFile(files[0]);
        }
    };

    const API_URL = import.meta.env.VITE_API_BASE_URL || '';

    const uploadFile = async (file) => {
        setUploading(true);
        setError('');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                headers: {},
                body: formData
            });

            if (!response.ok) throw new Error('Upload failed');

            const data = await response.json();
            setUploadedFile({ name: file.name, type: file.type });
            setTimeout(() => setUploadedFile(null), 3000); // Clear success msg
        } catch (error) {
            console.error(error);
            setError("Upload failed. Make sure backend is running.");
            setTimeout(() => setError(''), 5000);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-white/80 font-semibold mb-4 text-lg flex items-center gap-2">
                <svg className="w-5 h-5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                Upload Documents
            </h3>

            {error && (
                <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    {error}
                </div>
            )}

            <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`
                    border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300
                    flex flex-col items-center justify-center min-h-[200px] cursor-pointer
                    ${isDragging
                        ? 'border-indigo-400 bg-indigo-500/10 scale-[1.02]'
                        : 'border-white/10 hover:border-white/20 hover:bg-white/5'}
                `}
                onClick={() => document.getElementById('fileInput').click()}
            >
                <input
                    type="file"
                    id="fileInput"
                    className="hidden"
                    onChange={handleFileInput}
                />

                <AnimatePresence mode="wait">
                    {uploading ? (
                        <motion.div
                            key="uploading"
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        >
                            <div className="w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4" />
                            <p className="text-indigo-300 animate-pulse">Uploading...</p>
                        </motion.div>
                    ) : uploadedFile ? (
                        <motion.div
                            key="success"
                            initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                        >
                            <div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center mb-4 text-emerald-400">
                                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12" /></svg>
                            </div>
                            <p className="text-emerald-300 font-medium">Uploaded {uploadedFile.name}</p>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="idle"
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        >
                            <div className="w-12 h-12 bg-indigo-500/20 rounded-full flex items-center justify-center mb-4 text-indigo-400 mx-auto">
                                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
                            </div>
                            <p className="text-white/60 font-medium">Click or Drag files here</p>
                            <p className="text-white/30 text-sm mt-1">PDF, TXT, CSV (Max 10MB)</p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};
