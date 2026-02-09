import { useState, useEffect } from 'react';
import axios from 'axios';
import {
    CheckCircleIcon,
    XCircleIcon,
    ClockIcon,
    BellIcon
} from '@heroicons/react/24/outline';
import ApprovalCard from '../components/ApprovalCard';

const API_BASE = 'http://localhost:8000/api';

export default function Approvals() {
    const [pendingApprovals, setPendingApprovals] = useState([]);
    const [dashboard, setDashboard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, pending, approved, rejected
    const [selectedApproval, setSelectedApproval] = useState(null);

    useEffect(() => {
        fetchDashboard();
        // Poll for updates every 5 seconds
        const interval = setInterval(fetchDashboard, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchDashboard = async () => {
        try {
            const response = await axios.get(`${API_BASE}/approvals/dashboard`);
            setDashboard(response.data);
            setPendingApprovals(response.data.pending_requests);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch approvals:', error);
            setLoading(false);
        }
    };

    const handleApprove = async (approvalId) => {
        try {
            await axios.post(`${API_BASE}/approvals/${approvalId}/approve`, {
                action: 'approved',
                user_name: 'User',
                comment: 'Approved via dashboard'
            });
            fetchDashboard(); // Refresh
        } catch (error) {
            console.error('Failed to approve:', error);
            alert('Failed to approve request');
        }
    };

    const handleReject = async (approvalId) => {
        const comment = prompt('Please provide a reason for rejection:');
        if (!comment) return;

        try {
            await axios.post(`${API_BASE}/approvals/${approvalId}/reject`, {
                action: 'rejected',
                user_name: 'User',
                comment: comment
            });
            fetchDashboard(); // Refresh
        } catch (error) {
            console.error('Failed to reject:', error);
            alert('Failed to reject request');
        }
    };

    const handleViewDetails = (approval) => {
        setSelectedApproval(approval);
        // TODO: Open modal with full details
        console.log('View details for:', approval);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-gray-400">Loading approvals...</div>
            </div>
        );
    }

    return (
        <div className="pt-8 pb-8 px-8">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gradient mb-2">Approvals</h1>
                        <p className="text-gray-400">Review and approve agent outputs</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <BellIcon className="w-6 h-6 text-[#667eea]" />
                        {dashboard && dashboard.pending_count > 0 && (
                            <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                                {dashboard.pending_count}
                            </span>
                        )}
                    </div>
                </div>

                {/* Stats Cards */}
                {dashboard && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="card bg-gradient-to-br from-orange-500/10 to-orange-600/5 border-orange-500/30">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-400 mb-1">Pending</p>
                                    <p className="text-2xl font-bold text-orange-400">{dashboard.pending_count}</p>
                                </div>
                                <ClockIcon className="w-8 h-8 text-orange-400/50" />
                            </div>
                        </div>
                        <div className="card bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-500/30">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-400 mb-1">Approved</p>
                                    <p className="text-2xl font-bold text-green-400">{dashboard.approved_count}</p>
                                </div>
                                <CheckCircleIcon className="w-8 h-8 text-green-400/50" />
                            </div>
                        </div>
                        <div className="card bg-gradient-to-br from-red-500/10 to-red-600/5 border-red-500/30">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-400 mb-1">Rejected</p>
                                    <p className="text-2xl font-bold text-red-400">{dashboard.rejected_count}</p>
                                </div>
                                <XCircleIcon className="w-8 h-8 text-red-400/50" />
                            </div>
                        </div>
                        <div className="card bg-gradient-to-br from-gray-500/10 to-gray-600/5 border-gray-500/30">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-400 mb-1">Timeout</p>
                                    <p className="text-2xl font-bold text-gray-400">{dashboard.timeout_count}</p>
                                </div>
                                <ClockIcon className="w-8 h-8 text-gray-400/50" />
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Pending Approvals */}
            <div>
                <h2 className="text-xl font-semibold text-white mb-4">Pending Approvals</h2>
                {pendingApprovals.length === 0 ? (
                    <div className="card text-center py-12">
                        <CheckCircleIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                        <p className="text-gray-400 text-lg">No pending approvals</p>
                        <p className="text-gray-500 text-sm mt-2">All caught up! 🎉</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                        {pendingApprovals.map((approval) => (
                            <ApprovalCard
                                key={approval.id}
                                approval={approval}
                                onApprove={handleApprove}
                                onReject={handleReject}
                                onViewDetails={handleViewDetails}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* Recent Activity */}
            {dashboard && dashboard.recent_actions && dashboard.recent_actions.length > 0 && (
                <div className="mt-12">
                    <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
                    <div className="card">
                        <div className="space-y-3">
                            {dashboard.recent_actions.map((action) => (
                                <div key={action.id} className="flex items-start gap-3 pb-3 border-b border-[#2d3748] last:border-0 last:pb-0">
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${action.action === 'approved' ? 'bg-green-500/20' : 'bg-red-500/20'
                                        }`}>
                                        {action.action === 'approved' ? (
                                            <CheckCircleIcon className="w-5 h-5 text-green-400" />
                                        ) : (
                                            <XCircleIcon className="w-5 h-5 text-red-400" />
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm text-white">
                                            <span className="font-semibold">{action.user_name}</span>{' '}
                                            {action.action === 'approved' ? 'approved' : 'rejected'} a request
                                        </p>
                                        {action.comment && (
                                            <p className="text-xs text-gray-400 mt-1 italic">"{action.comment}"</p>
                                        )}
                                        <p className="text-xs text-gray-500 mt-1">
                                            {new Date(action.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
