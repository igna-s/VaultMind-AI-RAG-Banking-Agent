import React, { useState } from 'react';
import { api } from '../services/api';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Lock, Loader2, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const ResetPassword = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const navigate = useNavigate();

    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    // Helper function for validation (same as Login.jsx for consistency)
    const checkPasswordStrength = (pass) => {
        const requirements = [
            { id: 1, text: "At least 10 characters", met: pass.length >= 10 },
            { id: 2, text: "Contains uppercase letter", met: /[A-Z]/.test(pass) },
            { id: 3, text: "Contains lowercase letter", met: /[a-z]/.test(pass) },
            { id: 4, text: "Contains number", met: /[0-9]/.test(pass) },
            { id: 5, text: "Contains special character", met: /[!@#$%^&*(),.?":{}|<>]/.test(pass) },
        ];
        return requirements;
    };

    const passwordRequirements = checkPasswordStrength(newPassword);
    const isPasswordValid = passwordRequirements.every(req => req.met);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!isPasswordValid) {
            setError("La contraseña no cumple con los requisitos de seguridad.");
            return;
        }

        if (newPassword !== confirmPassword) {
            setError("Las contraseñas no coinciden");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            await api.post('/auth/reset-password', { token, new_password: newPassword });
            setSuccess(true);
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            setError(err.message || 'Error al restablecer la contraseña. El enlace puede haber expirado.');
        } finally {
            setLoading(false);
        }
    };

    if (!token) {
        return (
            <div className="min-h-screen bg-black text-white flex items-center justify-center">
                <div className="bg-red-900/20 text-red-400 p-6 rounded-xl border border-red-800">
                    Enlace inválido o incompleto.
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-zinc-900 rounded-2xl p-8 border border-zinc-800 shadow-xl">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                        Nueva Contraseña
                    </h2>
                    <p className="text-zinc-400 mt-2">
                        Ingresa tu nueva contraseña segura
                    </p>
                </div>

                {success ? (
                    <div className="text-center py-8">
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-4"
                        >
                            <CheckCircle className="w-8 h-8 text-green-500" />
                        </motion.div>
                        <h3 className="text-xl font-semibold text-white mb-2">¡Contraseña Actualizada!</h3>
                        <p className="text-zinc-400">Redirigiendo al login...</p>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {error && (
                            <div className="p-4 bg-red-900/30 border border-red-800 rounded-lg text-red-400 text-sm">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-300">Nueva Contraseña</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                                <input
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="w-full bg-black border border-zinc-800 rounded-xl px-10 py-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>

                            {/* Password Strength Indicators */}
                            <div className="mt-2 space-y-1 bg-black/50 p-3 rounded-lg border border-zinc-800">
                                {passwordRequirements.map((req) => (
                                    <div key={req.id} className="flex items-center gap-2 text-xs">
                                        <div className={`w-1.5 h-1.5 rounded-full ${req.met ? 'bg-green-500' : 'bg-red-500'}`} />
                                        <span className={req.met ? 'text-green-500' : 'text-zinc-500'}>
                                            {req.text}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-300">Confirmar Contraseña</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                                <input
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="w-full bg-black border border-zinc-800 rounded-xl px-10 py-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
                                    placeholder="••••••••"
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
                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Cambiar Contraseña'}
                        </motion.button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default ResetPassword;
