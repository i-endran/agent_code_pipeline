import { useState, useEffect } from 'react';
import axios from 'axios';
import {
    SparklesIcon,
    KeyIcon,
    AdjustmentsHorizontalIcon,
    BoltIcon,
    ShieldCheckIcon,
    PlusIcon
} from '@heroicons/react/24/outline';

const API_BASE = 'http://localhost:8000/api';

export default function Models() {
    const [agents, setAgents] = useState({});
    const [tokenStats, setTokenStats] = useState({ total_tokens: 0, total_cost: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                const response = await axios.get(`${API_BASE}/agents/status`);
                setAgents(response.data.agents);
                setTokenStats({
                    total_tokens: response.data.total_estimated_tokens,
                    total_cost: response.data.total_estimated_cost
                });
                setLoading(false);
            } catch (error) {
                console.error("Failed to fetch agents:", error);
                setLoading(false);
            }
        };

        fetchAgents();
    }, []);

    if (loading) return <div className="p-8 text-gray-400">Loading models...</div>;

    // Transform agents object to array for easier mapping
    const agentList = Object.entries(agents).map(([key, config]) => ({
        id: key,
        ...config
    }));

    return (
        <div className="pt-8 w-full max-w-6xl mx-auto px-4">
            <header className="mb-10 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-gradient mb-2">AI Models</h1>
                    <p className="text-gray-400">Configure LLM providers, API keys, and model orchestration settings</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 border border-[#2d3748] hover:border-[#667eea] text-gray-400 hover:text-white rounded-lg transition-all">
                    <KeyIcon className="w-5 h-5" />
                    Manage API Keys
                </button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
                <div className="card lg:col-span-2">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <SparklesIcon className="w-6 h-6 text-[#667eea]" />
                        Active Orchestration
                    </h2>

                    <div className="space-y-6">
                        {agentList.map(agent => (
                            <div key={agent.id} className="p-4 bg-[#1a1b23] rounded-xl border border-[#2d3748] hover:border-[#667eea]/50 transition-all">
                                <div className="flex justify-between items-start mb-3">
                                    <div>
                                        <h3 className="text-lg font-bold text-white mb-1 capitalize">{agent.name} Agent</h3>
                                        <p className="text-xs text-gray-500">{agent.description}</p>
                                    </div>
                                    <span className="status-badge status-completed">Active</span>
                                </div>

                                <div className="flex gap-4 mb-4">
                                    <span className="text-[10px] text-gray-400 border border-[#2d3748] px-2 py-0.5 rounded uppercase">
                                        {agent.provider}
                                    </span>
                                    <span className="text-[10px] text-gray-400 border border-[#2d3748] px-2 py-0.5 rounded">
                                        {agent.model}
                                    </span>
                                </div>

                                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[#2d3748]">
                                    <div className="flex items-center gap-2 text-xs text-gray-500">
                                        <BoltIcon className="w-4 h-4 text-blue-400" />
                                        Max Tokens: <span className="text-gray-300 font-bold">{agent.max_tokens}</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-xs text-gray-500">
                                        <AdjustmentsHorizontalIcon className="w-4 h-4 text-green-400" />
                                        Temp: <span className="text-gray-300 font-bold">{agent.temperature}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="card">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <ShieldCheckIcon className="w-5 h-5 text-green-500" />
                            Safety Guardrails
                        </h3>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between text-xs p-2 bg-[#1a1b23] rounded border border-[#2d3748]">
                                <span className="text-gray-400">PII Filtering</span>
                                <span className="text-green-500 font-bold">ON</span>
                            </div>
                            <div className="flex items-center justify-between text-xs p-2 bg-[#1a1b23] rounded border border-[#2d3748]">
                                <span className="text-gray-400">Context Window Warn</span>
                                <span className="text-gray-500 font-bold">85%</span>
                            </div>
                            <div className="pt-4 mt-2 border-t border-[#2d3748]">
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-gray-400">Est. Token Usage</span>
                                    <span className="text-sm font-bold text-white">{tokenStats.total_tokens.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between items-center mt-1">
                                    <span className="text-xs text-gray-400">Est. Cost</span>
                                    <span className="text-sm font-bold text-green-400">${tokenStats.total_cost.toFixed(4)}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="card bg-gradient-to-br from-[#1a1b23] to-[#2d3748]/20 border-dashed">
                        <h3 className="text-white font-bold mb-2">Experimental Models</h3>
                        <p className="text-xs text-gray-500 mb-4">Enable early access to Gemini 2.0 Ultra when available.</p>
                        <button className="w-full py-2 bg-[#2d3748] hover:bg-[#667eea] text-gray-400 hover:text-white rounded-lg text-xs font-bold transition-all">
                            Request Access
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
