import { FileUploader } from '../../components/dashboard/FileUploader';
import { motion } from 'framer-motion';

export default function DocumentManagement() {
    return (
        <div className="space-y-8">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white">Knowledge Base</h1>
                    <p className="text-white/60 mt-2">Manage documents and data sources for the RAG system.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="lg:col-span-2 space-y-6"
                >
                    <div className="glass-panel p-6 rounded-2xl">
                        <h3 className="text-white/80 font-semibold mb-6">Active Documents</h3>
                        <div className="text-center py-12 text-white/30">
                            No documents indexed yet.
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <FileUploader />
                </motion.div>
            </div>
        </div>
    );
}
