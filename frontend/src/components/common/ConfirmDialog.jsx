import { useState } from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export default function ConfirmDialog({
    show,
    title,
    message,
    confirmLabel = 'Confirm',
    cancelLabel = 'Cancel',
    onConfirm,
    onCancel,
    variant = 'danger' // 'danger' | 'warning' | 'info'
}) {
    const [loading, setLoading] = useState(false);

    if (!show) return null;

    const handleConfirm = async () => {
        setLoading(true);
        try {
            await onConfirm();
        } finally {
            setLoading(false);
        }
    };

    const variants = {
        danger: 'bg-red-500/20 border-red-500/50',
        warning: 'bg-orange-500/20 border-orange-500/50',
        info: 'bg-blue-500/20 border-blue-500/50'
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className={`card max-w-md w-full border ${variants[variant]}`}>
                <div className="flex items-start gap-3 mb-4">
                    <ExclamationTriangleIcon className="w-6 h-6 text-orange-400 flex-shrink-0" />
                    <div>
                        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
                        <p className="text-gray-300 text-sm">{message}</p>
                    </div>
                </div>
                <div className="flex gap-3 justify-end">
                    <button
                        onClick={onCancel}
                        disabled={loading}
                        className="px-4 py-2 rounded-lg bg-[#1a1b23] hover:bg-[#2d3748] text-white border border-[#2d3748] transition-colors disabled:opacity-50"
                    >
                        {cancelLabel}
                    </button>
                    <button
                        onClick={handleConfirm}
                        disabled={loading}
                        className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white transition-colors disabled:opacity-50"
                    >
                        {loading ? 'Processing...' : confirmLabel}
                    </button>
                </div>
            </div>
        </div>
    );
}
