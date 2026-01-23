import { AccountStats } from '../../components/dashboard/AccountStats';
import { RecentTransactions } from '../../components/dashboard/RecentTransactions';
import { FileUploader } from '../../components/dashboard/FileUploader';
import { motion } from 'framer-motion';

export default function Overview() {
    return (
        <div className="p-6 max-w-7xl mx-auto">
            <header className="mb-8">
                <motion.h1 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-3xl font-bold text-white"
                >
                    Dashboard Overview
                </motion.h1>
                <p className="text-white/50 mt-1">Welcome back to your financial command center.</p>
            </header>

            {/* Quick Stats Row */}
            <AccountStats />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content Area (Charts/Activity) */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Placeholder for Chart */}
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="glass-panel p-6 rounded-2xl h-80 flex flex-col justify-between"
                    >
                        <h3 className="text-white/80 font-semibold mb-4 text-lg">Spending Analysis</h3>
                        <div className="flex-1 border-dashed border-2 border-white/10 rounded-xl flex items-center justify-center relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-t from-indigo-500/10 to-transparent" />
                            <p className="text-white/30 font-medium relative z-10">Financial Chart Visualization</p>
                            {/* Mock bars */}
                            <div className="absolute bottom-0 left-10 w-8 h-32 bg-indigo-500/40 rounded-t-md mx-2" />
                            <div className="absolute bottom-0 left-24 w-8 h-48 bg-indigo-500/60 rounded-t-md mx-2" />
                            <div className="absolute bottom-0 left-38 w-8 h-24 bg-indigo-500/30 rounded-t-md mx-2" />
                             <div className="absolute bottom-0 left-52 w-8 h-56 bg-indigo-500/80 rounded-t-md mx-2 animate-pulse" />
                        </div>
                    </motion.div>

                    {/* File Upload Section */}
                    <div>
                         <h3 className="text-white/80 font-semibold mb-4 text-lg">Document Management</h3>
                         <FileUploader />
                    </div>
                </div>

                {/* Sidebar (Transactions) */}
                <div>
                    <RecentTransactions />
                </div>
            </div>
        </div>
    );
}
