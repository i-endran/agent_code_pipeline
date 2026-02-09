import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export default function ErrorMessage({ error, onRetry, className = '' }) {
    if (!error) return null;

    return (
        <div className={`card bg-red-500/10 border-red-500/30 ${className}`}>
            <div className="flex items-start gap-3">
                <ExclamationTriangleIcon className="w-6 h-6 text-red-400 flex-shrink-0" />
                <div className="flex-1">
                    <h3 className="text-red-400 font-semibold mb-1">Error</h3>
                    <p className="text-gray-300 text-sm">{error}</p>
                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="mt-3 text-sm text-red-400 hover:text-red-300 underline"
                        >
                            Try Again
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
