import { useState, useEffect } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

export const RecentTransactions = () => {
    const { user } = useAuth();
    const [transactions, setTransactions] = useState([]);

    useEffect(() => {
        if (!user) return;

        const fetchTransactions = async () => {
            try {
                const res = await fetch('/api/v1/transactions', {
                    headers: { 'Authorization': `Bearer ${user.token}` }
                });
                if (res.ok) {
                    const data = await res.json();

                    // Map API data to UI format
                    const mapped = data.map(tx => ({
                        id: tx.id,
                        name: tx.description,
                        date: new Date(tx.date).toLocaleDateString(),
                        amount: (tx.amount / 100).toLocaleString('en-US', { style: 'currency', currency: 'USD' }),
                        type: tx.amount > 0 ? 'credit' : 'debit',
                        logo: tx.description.charAt(0).toUpperCase()
                    }));
                    setTransactions(mapped);
                }
            } catch (err) {
                console.error("Failed to fetch transactions", err);
            }
        };

        fetchTransactions();
    }, [user]);

    return (
        <div className="glass-panel p-6 rounded-2xl h-full">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-white/80 font-semibold text-lg">Recent Activity</h3>
                <button className="text-indigo-300 text-sm hover:text-white transition-colors">View All</button>
            </div>

            <div className="space-y-4">
                {transactions.length === 0 && (
                    <div className="text-white/40 text-sm text-center py-4">No recent transactions</div>
                )}
                {transactions.map((tx, idx) => (
                    <motion.div
                        key={tx.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="flex items-center justify-between group p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer"
                    >
                        <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white
                                ${tx.type === 'credit' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-indigo-500/20 text-indigo-400'}
                            `}>
                                {tx.logo}
                            </div>
                            <div>
                                <p className="font-medium text-white">{tx.name}</p>
                                <p className="text-xs text-white/50">{tx.date}</p>
                            </div>
                        </div>
                        <div className={`font-semibold ${tx.type === 'credit' ? 'text-emerald-400' : 'text-white'}`}>
                            {tx.amount}
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};
