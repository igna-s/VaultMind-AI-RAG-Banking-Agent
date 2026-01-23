import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

export const AccountStats = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState([
        { title: "Total Balance", value: "Loading...", change: "...", isPositive: true },
        { title: "Income", value: "$4,200.00", change: "+4.1%", isPositive: true },
        { title: "Expenses", value: "$1,850.00", change: "-1.2%", isPositive: false },
    ]);

    useEffect(() => {
        if (!user) return;

        const fetchAccounts = async () => {
            try {
                // Using relative path to proxy
                const res = await fetch('/api/v1/accounts', {
                    headers: { 'Authorization': `Bearer ${user.token}` }
                });
                if (res.ok) {
                    const accounts = await res.json();
                    if (accounts.length > 0) {
                        const main = accounts[0];
                        // Convert cents to dollars
                        const balance = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(main.balance / 100);
                        
                        setStats(prev => [
                            { ...prev[0], value: balance },
                            prev[1], 
                            prev[2]
                        ]);
                    }
                }
            } catch (err) {
                console.error("Failed to fetch accounts", err);
            }
        };

        fetchAccounts();
    }, [user]);

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {stats.map((stat, idx) => (
                <motion.div 
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="glass-panel p-6 rounded-2xl relative overflow-hidden group"
                >
                    <div className="relative z-10">
                        <h3 className="text-white/60 text-sm font-medium">{stat.title}</h3>
                        <p className="text-3xl font-bold mt-2 text-white">{stat.value}</p>
                        <div className={`mt-4 text-sm flex items-center gap-1 ${stat.isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                            <span>{stat.change}</span>
                            <span className="opacity-60">from last month</span>
                        </div>
                    </div>
                    {/* Hover Glow Effect */}
                    <div className="absolute -right-10 -top-10 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-all duration-500" />
                </motion.div>
            ))}
        </div>
    );
};
