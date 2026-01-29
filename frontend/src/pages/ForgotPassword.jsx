import React, { useState } from 'react';
import { api } from '../services/api';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);
        setError(null);

        try {
            await api.post('/auth/forgot-password', { email });
            setMessage("Si el correo existe, recibirás un enlace de recuperación pronto.");
        } catch (err) {
            setError(err.message || 'Error al procesar la solicitud');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-zinc-900 rounded-2xl p-8 border border-zinc-800 shadow-xl">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                        Recuperar Contraseña
                    </h2>
                    <p className="text-zinc-400 mt-2">
                        Ingresa tu email para recibir un enlace
                    </p>
                </div>

                {message && (
                    <div className="mb-6 p-4 bg-green-900/30 border border-green-800 rounded-lg text-green-400 text-sm">
                        {message}
                    </div>
                )}

                {error && (
                    <div className="mb-6 p-4 bg-red-900/30 border border-red-800 rounded-lg text-red-400 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-zinc-300">Email</label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-black border border-zinc-800 rounded-xl px-10 py-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
                                placeholder="tu@email.com"
                                required
                            />
                        </div>
                    </div>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl transition-colors flex items-center justify-center gap-2"
                    >
                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Enviar Enlace'}
                    </motion.button>
                </form>

                <div className="mt-6 text-center">
                    <Link
                        to="/login"
                        className="text-zinc-400 hover:text-white text-sm inline-flex items-center gap-2 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" /> Volver al Login
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ForgotPassword;
