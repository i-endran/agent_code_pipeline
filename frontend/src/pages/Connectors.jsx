import { useState, useEffect } from 'react';
import axios from 'axios';
import {
    PlusIcon,
    ChatBubbleLeftRightIcon,
    CodeBracketIcon,
    CheckCircleIcon,
    CloudIcon,
    TrashIcon,
    BoltIcon
} from '@heroicons/react/24/outline';

const API_BASE = 'http://localhost:8000/api';

const CONNECTOR_TYPES = [
    { id: 'github', name: 'GitHub', type: 'Source Control', icon: CodeBracketIcon },
    { id: 'gitlab', name: 'GitLab', type: 'Source Control', icon: CloudIcon },
    { id: 'slack', name: 'Slack', type: 'Communication', icon: ChatBubbleLeftRightIcon },
    { id: 'teams', name: 'MS Teams', type: 'Communication', icon: ChatBubbleLeftRightIcon },
    { id: 'cliq', name: 'Zoho Cliq', type: 'Communication', icon: ChatBubbleLeftRightIcon },
];

export default function Connectors() {
    const [connectors, setConnectors] = useState([]);
    const [outboundWebhooks, setOutboundWebhooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showConnectorModal, setShowConnectorModal] = useState(false);
    const [showWebhookModal, setShowWebhookModal] = useState(false);

    // Form states
    const [newConnector, setNewConnector] = useState({ name: '', type: 'github', config: {} });
    const [newWebhook, setNewWebhook] = useState({ name: '', url: '', events: ['task_completed'], platform: 'custom' });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [connRes, webhookRes] = await Promise.all([
                axios.get(`${API_BASE}/connectors`),
                axios.get(`${API_BASE}/outbound-webhooks`)
            ]);
            setConnectors(connRes.data);
            setOutboundWebhooks(webhookRes.data);
            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch data:", error);
            setLoading(false);
        }
    };

    const handleCreateConnector = async () => {
        try {
            await axios.post(`${API_BASE}/connectors`, {
                ...newConnector,
                config: JSON.parse(newConnector.configStr || '{}') // Temp hack for JSON input
            });
            setShowConnectorModal(false);
            fetchData();
        } catch (error) {
            alert('Failed to create connector. Ensure config is valid JSON.');
        }
    };

    const handleDeleteConnector = async (id) => {
        if (!confirm('Are you sure?')) return;
        await axios.delete(`${API_BASE}/connectors/${id}`);
        fetchData();
    };

    const handleCreateWebhook = async () => {
        try {
            await axios.post(`${API_BASE}/outbound-webhooks/`, newWebhook);
            setShowWebhookModal(false);
            fetchData();
        } catch (error) {
            console.error(error);
            alert('Failed to create webhook');
        }
    };

    const handleDeleteWebhook = async (id) => {
        if (!confirm('Are you sure?')) return;
        await axios.delete(`${API_BASE}/outbound-webhooks/${id}`);
        fetchData();
    };

    const getIcon = (type) => {
        const match = CONNECTOR_TYPES.find(t => t.id === type);
        return match ? match.icon : CodeBracketIcon;
    };

    if (loading) return <div className="p-8 text-gray-400">Loading connectors...</div>;

    return (
        <div className="pt-8 w-full max-w-6xl mx-auto px-4">
            <header className="mb-10 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-gradient mb-2">Connectors</h1>
                    <p className="text-gray-400">Manage external platform integrations</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setShowWebhookModal(true)}
                        className="flex items-center gap-2 px-4 py-2 border border-[#2d3748] hover:border-[#667eea] text-gray-400 hover:text-white rounded-lg transition-all"
                    >
                        <BoltIcon className="w-5 h-5" />
                        Add Webhook
                    </button>
                    <button
                        onClick={() => setShowConnectorModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-[#667eea] hover:bg-[#764ba2] text-white rounded-lg transition-all font-medium"
                    >
                        <PlusIcon className="w-5 h-5" />
                        Add Connector
                    </button>
                </div>
            </header>

            {/* Connectors Grid */}
            <h2 className="text-xl font-bold text-white mb-4">Active Connectors</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {connectors.length === 0 && <p className="text-gray-500 italic">No connectors configured.</p>}
                {connectors.map((connector) => {
                    const Icon = getIcon(connector.type);
                    return (
                        <div key={connector.id} className="card hover:border-[#667eea] transition-all relative group">
                            <button
                                onClick={() => handleDeleteConnector(connector.id)}
                                className="absolute top-4 right-4 text-gray-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                <TrashIcon className="w-5 h-5" />
                            </button>
                            <div className="flex justify-between items-start mb-6">
                                <div className="p-3 bg-[#1a1b23] rounded-xl border border-[#2d3748]">
                                    <Icon className="w-8 h-8 text-[#667eea]" />
                                </div>
                                <span className={`status-badge ${connector.is_active ? 'status-completed' : 'status-failed'}`}>
                                    {connector.is_active ? 'connected' : 'inactive'}
                                </span>
                            </div>

                            <h3 className="text-xl font-bold text-white mb-1">{connector.name}</h3>
                            <p className="text-sm text-gray-500 mb-4 capitalize">{connector.type}</p>

                            <div className="pt-4 border-t border-[#2d3748] flex items-center justify-between">
                                <span className="text-xs text-gray-400 italic truncate max-w-[150px]">
                                    {JSON.stringify(connector.config)}
                                </span>
                                {connector.is_active && <CheckCircleIcon className="w-5 h-5 text-green-500" />}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Outbound Webhooks Section */}
            <section className="mb-12">
                <h2 className="text-xl font-bold text-white mb-6">Outbound Webhooks</h2>
                <div className="space-y-4">
                    {outboundWebhooks.length === 0 && <p className="text-gray-500 italic">No outbound webhooks configured.</p>}
                    {outboundWebhooks.map(webhook => (
                        <div key={webhook.id} className="bg-[#1a1b23] border border-[#2d3748] rounded-xl p-6 flex justify-between items-center group">
                            <div>
                                <div className="text-white font-medium flex items-center gap-2">
                                    {webhook.name}
                                    <span className="text-[10px] bg-gray-800 text-gray-400 px-2 py-0.5 rounded capitalize">{webhook.platform}</span>
                                </div>
                                <div className="text-xs text-gray-500 mt-1">{webhook.url}</div>
                                <div className="flex gap-2 mt-2">
                                    {webhook.events.map(e => (
                                        <span key={e} className="text-[10px] text-[#667eea] bg-[#667eea]/10 px-2 rounded-full">{e}</span>
                                    ))}
                                </div>
                            </div>
                            <button
                                onClick={() => handleDeleteWebhook(webhook.id)}
                                className="text-gray-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                <TrashIcon className="w-5 h-5" />
                            </button>
                        </div>
                    ))}
                </div>
            </section>

            {/* Incoming Webhooks (Static for now, but dynamic host) */}
            <section className="mt-12">
                <h2 className="text-xl font-bold text-white mb-6">Incoming Webhook URLs</h2>
                <div className="bg-[#1a1b23] border border-[#2d3748] rounded-xl p-6">
                    <div className="flex items-center justify-between py-4 border-b border-[#2d3748]">
                        <div>
                            <div className="text-white font-medium">GitHub Webhook</div>
                            <div className="text-xs text-gray-500">Payload URL for repository settings</div>
                        </div>
                        <code className="text-xs bg-black px-3 py-1 rounded text-[#667eea]">http://localhost:8000/api/webhooks/github</code>
                    </div>
                    <div className="flex items-center justify-between py-4">
                        <div>
                            <div className="text-white font-medium">GitLab Webhook</div>
                            <div className="text-xs text-gray-500">Payload URL for merge requests</div>
                        </div>
                        <code className="text-xs bg-black px-3 py-1 rounded text-[#667eea]">http://localhost:8000/api/webhooks/gitlab</code>
                    </div>
                </div>
            </section>

            {/* Modals */}
            {showConnectorModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
                    <div className="bg-[#1a1b23] p-6 rounded-xl border border-[#2d3748] w-full max-w-md">
                        <h3 className="text-xl font-bold text-white mb-4">Add Connector</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Name</label>
                                <input
                                    className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm"
                                    value={newConnector.name}
                                    onChange={e => setNewConnector({ ...newConnector, name: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Type</label>
                                <select
                                    className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm"
                                    value={newConnector.type}
                                    onChange={e => setNewConnector({ ...newConnector, type: e.target.value })}
                                >
                                    {CONNECTOR_TYPES.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Config JSON (Token, URL, etc)</label>
                                <textarea
                                    className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm h-24 font-mono"
                                    placeholder='{"token": "..."}'
                                    value={newConnector.configStr}
                                    onChange={e => setNewConnector({ ...newConnector, configStr: e.target.value })}
                                />
                            </div>
                            <div className="flex justify-end gap-2 mt-6">
                                <button onClick={() => setShowConnectorModal(false)} className="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
                                <button onClick={handleCreateConnector} className="px-4 py-2 bg-[#667eea] text-white rounded">Create</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {showWebhookModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
                    <div className="bg-[#1a1b23] p-6 rounded-xl border border-[#2d3748] w-full max-w-md">
                        <h3 className="text-xl font-bold text-white mb-4">Add Outbound Webhook</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Name</label>
                                <input
                                    className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm"
                                    value={newWebhook.name}
                                    onChange={e => setNewWebhook({ ...newWebhook, name: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Target URL</label>
                                <input
                                    className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm"
                                    value={newWebhook.url}
                                    onChange={e => setNewWebhook({ ...newWebhook, url: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Platform</label>
                                <select
                                    className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm"
                                    value={newWebhook.platform}
                                    onChange={e => setNewWebhook({ ...newWebhook, platform: e.target.value })}
                                >
                                    <option value="custom">Custom (JSON)</option>
                                    <option value="slack">Slack Incoming Webhook</option>
                                    <option value="teams">Microsoft Teams</option>
                                </select>
                            </div>
                            <div className="flex justify-end gap-2 mt-6">
                                <button onClick={() => setShowWebhookModal(false)} className="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
                                <button onClick={handleCreateWebhook} className="px-4 py-2 bg-[#667eea] text-white rounded">Create</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
