import { useState } from 'react';
import {
    CheckCircleIcon,
    XCircleIcon,
    ClockIcon,
    EyeIcon
} from '@heroicons/react/24/outline';

export default function ApprovalCard({ approval, onApprove, onReject, onViewDetails }) {
    const [isProcessing, setIsProcessing] = useState(false);

    const getStatusBadge = (status) => {
        const badges = {
            pending: 'status-pending',
            approved: 'status-completed',
            rejected: 'status-failed',
            timeout: 'status-failed'
        };
        return badges[status] || 'status-pending';
    };

    const getCheckpointLabel = (checkpoint) => {
        const labels = {
            scribe_output: 'SCRIBE Output',
            architect_plan: 'ARCHITECT Plan',
            forge_code: 'FORGE Code',
            sentinel_review: 'SENTINEL Review',
            phoenix_release: 'PHOENIX Release'
        };
        return labels[checkpoint] || checkpoint;
    };

    const formatTimeAgo = (timestamp) => {
        const now = new Date();
        const created = new Date(timestamp);
        const diffMs = now - created;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours}h ago`;
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays}d ago`;
    };

    const handleApprove = async () => {
        setIsProcessing(true);
        await onApprove(approval.id);
        setIsProcessing(false);
    };

    const handleReject = async () => {
        setIsProcessing(true);
        await onReject(approval.id);
        setIsProcessing(false);
    };

    return (
        <div className="card hover:border-[#667eea]/50 transition-all">
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-lg font-semibold text-white mb-1">
                        {getCheckpointLabel(approval.checkpoint)}
                    </h3>
                    <p className="text-sm text-gray-400">
                        Task: <span className="font-mono text-[#667eea]">{approval.task_id}</span>
                    </p>
                </div>
                <span className={`status-badge ${getStatusBadge(approval.status)}`}>
                    {approval.status}
                </span>
            </div>

            {/* Summary */}
            {approval.summary && (
                <p className="text-gray-300 text-sm mb-4 line-clamp-2">
                    {approval.summary}
                </p>
            )}

            {/* Metadata */}
            <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
                <span className="flex items-center gap-1">
                    <ClockIcon className="w-4 h-4" />
                    {formatTimeAgo(approval.created_at)}
                </span>
                {approval.timeout_at && approval.status === 'pending' && (
                    <span className="text-orange-400">
                        Timeout: {new Date(approval.timeout_at).toLocaleTimeString()}
                    </span>
                )}
            </div>

            {/* Artifacts */}
            {approval.artifact_paths && approval.artifact_paths.length > 0 && (
                <div className="mb-4">
                    <p className="text-xs text-gray-500 mb-2">Artifacts:</p>
                    <div className="flex flex-wrap gap-2">
                        {approval.artifact_paths.slice(0, 3).map((path, idx) => (
                            <span key={idx} className="text-xs bg-[#1a1b23] px-2 py-1 rounded border border-[#2d3748] text-gray-400">
                                {path.split('/').pop()}
                            </span>
                        ))}
                        {approval.artifact_paths.length > 3 && (
                            <span className="text-xs text-gray-500">
                                +{approval.artifact_paths.length - 3} more
                            </span>
                        )}
                    </div>
                </div>
            )}

            {/* Actions */}
            {approval.status === 'pending' && (
                <div className="flex gap-2">
                    <button
                        onClick={handleApprove}
                        disabled={isProcessing}
                        className="flex-1 flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                        <CheckCircleIcon className="w-4 h-4" />
                        Approve
                    </button>
                    <button
                        onClick={handleReject}
                        disabled={isProcessing}
                        className="flex-1 flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                        <XCircleIcon className="w-4 h-4" />
                        Reject
                    </button>
                    <button
                        onClick={() => onViewDetails(approval)}
                        className="flex items-center justify-center gap-2 bg-[#1a1b23] hover:bg-[#2d3748] text-white px-4 py-2 rounded-lg text-sm font-medium border border-[#2d3748] transition-colors"
                    >
                        <EyeIcon className="w-4 h-4" />
                        Details
                    </button>
                </div>
            )}

            {/* Approved/Rejected Info */}
            {approval.status !== 'pending' && approval.actions && approval.actions.length > 0 && (
                <div className="bg-[#1a1b23] p-3 rounded-lg border border-[#2d3748]">
                    <p className="text-xs text-gray-400 mb-1">
                        {approval.status === 'approved' ? 'Approved' : 'Rejected'} by{' '}
                        <span className="text-white">{approval.actions[0].user_name}</span>
                    </p>
                    {approval.actions[0].comment && (
                        <p className="text-sm text-gray-300 italic">
                            "{approval.actions[0].comment}"
                        </p>
                    )}
                </div>
            )}
        </div>
    );
}
