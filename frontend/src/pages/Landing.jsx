import { useState, useMemo } from 'react';
import {
    DocumentTextIcon,
    CubeIcon,
    CodeBracketIcon,
    ShieldCheckIcon,
    RocketLaunchIcon,
    ChartBarIcon
} from '@heroicons/react/24/outline';

const agents = [
    {
        id: 'scribe',
        name: 'SCRIBE',
        role: 'Requirement Parser',
        icon: DocumentTextIcon,
        tokens: { input: 2000, output: 1500 },
    },
    {
        id: 'architect',
        name: 'ARCHITECT',
        role: 'Plan Generator',
        icon: CubeIcon,
        tokens: { input: 3000, output: 2500 },
    },
    {
        id: 'forge',
        name: 'FORGE',
        role: 'Code Executor',
        icon: CodeBracketIcon,
        tokens: { input: 5000, output: 4000 },
    },
    {
        id: 'sentinel',
        name: 'SENTINEL',
        role: 'Code Reviewer',
        icon: ShieldCheckIcon,
        tokens: { input: 4000, output: 3000 },
    },
    {
        id: 'phoenix',
        name: 'PHOENIX',
        role: 'Releaser',
        icon: RocketLaunchIcon,
        tokens: { input: 1000, output: 500 },
    },
];

export default function Landing() {
    // Start with no agents selected by default
    const [enabledAgents, setEnabledAgents] = useState(new Set());
    const [showModal, setShowModal] = useState(null);
    const [showTokenDashboard, setShowTokenDashboard] = useState(false);

    // Sequential agent selection logic
    const canToggleAgent = (agentId) => {
        const agentIndex = agents.findIndex(a => a.id === agentId);
        const isEnabled = enabledAgents.has(agentId);

        if (isEnabled) {
            // Can only disable if no agents after this are enabled
            for (let i = agentIndex + 1; i < agents.length; i++) {
                if (enabledAgents.has(agents[i].id)) {
                    return false; // Can't disable because a later agent is enabled
                }
            }
            return true;
        } else {
            // Can only enable if all previous agents are enabled
            for (let i = 0; i < agentIndex; i++) {
                if (!enabledAgents.has(agents[i].id)) {
                    return false; // Can't enable because a previous agent is disabled
                }
            }
            return true;
        }
    };

    const toggleAgent = (agentId) => {
        if (!canToggleAgent(agentId)) {
            return; // Don't allow toggle if sequential order would be broken
        }

        setEnabledAgents(prev => {
            const newSet = new Set(prev);
            if (newSet.has(agentId)) {
                newSet.delete(agentId);
            } else {
                newSet.add(agentId);
            }
            return newSet;
        });
    };

    const handleConfigure = (e, agentId) => {
        e.stopPropagation();
        setShowModal(agentId);
    };

    // Calculate token estimates
    const tokenEstimate = useMemo(() => {
        let totalInput = 0;
        let totalOutput = 0;

        agents.forEach(agent => {
            if (enabledAgents.has(agent.id)) {
                totalInput += agent.tokens.input;
                totalOutput += agent.tokens.output;
            }
        });

        return {
            input: totalInput,
            output: totalOutput,
            total: totalInput + totalOutput,
            cost: ((totalInput * 0.00001) + (totalOutput * 0.00003)).toFixed(4)
        };
    }, [enabledAgents]);

    return (
        <div className="pt-8 pb-8">
            {/* SVG Gradient Definition for Icons */}
            <svg width="0" height="0" style={{ position: 'absolute' }}>
                <defs>
                    <linearGradient id="icon-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#667eea" />
                        <stop offset="100%" stopColor="#764ba2" />
                    </linearGradient>
                </defs>
            </svg>

            {/* Hero Section - Fixed line-height for text clipping */}
            <header className="mb-12 text-center">
                <h1 className="text-4xl font-bold mb-3 text-gradient">
                    AI Agent Pipeline
                </h1>
                <p className="text-gray-400 text-sm">
                    Configure and deploy 5 specialized agents to automate your SDLC
                </p>
            </header>

            {/* Agent Pipeline - Added more top padding for hover */}
            <div className="mb-10 overflow-visible pt-6">
                <div className="flex items-start justify-center gap-2 min-w-max px-4">
                    {agents.map((agent, index) => {
                        const isEnabled = enabledAgents.has(agent.id);
                        const canToggle = canToggleAgent(agent.id);
                        const Icon = agent.icon;

                        return (
                            <div key={agent.id} className="flex items-center">
                                {/* Agent Card */}
                                <div
                                    className={`agent-box ${isEnabled ? 'enabled' : ''} ${!canToggle ? 'locked' : ''}`}
                                    onClick={() => toggleAgent(agent.id)}
                                    title={!canToggle ? 'Enable previous agents first' : ''}
                                >
                                    {/* Icon */}
                                    <div className="agent-icon">
                                        <Icon
                                            className="w-10 h-10"
                                            style={{ stroke: 'url(#icon-gradient)' }}
                                        />
                                    </div>

                                    {/* Agent Name */}
                                    <div className="agent-name">{agent.name}</div>
                                    <div className="agent-role">{agent.role}</div>

                                    {/* Toggle Switch */}
                                    <div className="agent-toggle">
                                        <div className={`toggle-switch ${isEnabled ? 'active' : ''} ${!canToggle ? 'disabled' : ''}`}>
                                            <div className="toggle-slider"></div>
                                        </div>
                                    </div>

                                    {/* Configure Button */}
                                    <button
                                        className="btn-config"
                                        onClick={(e) => handleConfigure(e, agent.id)}
                                        disabled={!isEnabled}
                                    >
                                        ⚙ Configure
                                    </button>
                                </div>

                                {/* Connection Arrow */}
                                {index < agents.length - 1 && (
                                    <div className="pipeline-connector">→</div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Info Text */}
                <div className="text-center text-xs text-gray-500 mt-6">
                    <p>↻ SENTINEL → FORGE feedback loop for code fixes</p>
                </div>
            </div>

            {/* Token Dashboard Button */}
            <div className="flex justify-center mb-6">
                <button
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-400 hover:text-white border border-gray-600 hover:border-[#667eea] rounded-lg transition-all"
                    onClick={() => setShowTokenDashboard(true)}
                >
                    <ChartBarIcon className="w-5 h-5" />
                    Token Dashboard
                </button>
            </div>

            {/* Submit Section */}
            <div className="card max-w-2xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-lg font-semibold mb-1 text-white">Ready to Deploy</h2>
                        <p className="text-gray-400 text-sm">
                            {enabledAgents.size} agent{enabledAgents.size !== 1 ? 's' : ''} selected
                        </p>
                    </div>
                    <button
                        className="btn-primary"
                        disabled={enabledAgents.size === 0}
                    >
                        🚀 Run Pipeline
                    </button>
                </div>

                {/* Repository Input */}
                <div className="mb-4">
                    <label className="label">Repository URL</label>
                    <input
                        type="text"
                        placeholder="https://github.com/username/repo"
                        className="input"
                    />
                </div>

                {/* Branch Input */}
                <div>
                    <label className="label">Target Branch</label>
                    <input
                        type="text"
                        placeholder="main"
                        className="input"
                    />
                </div>
            </div>

            {/* Agent Configuration Modal */}
            {showModal && (
                <div
                    className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
                    onClick={() => setShowModal(null)}
                >
                    <div
                        className="card max-w-md w-full mx-4"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h3 className="text-lg font-bold mb-4 text-gradient">
                            Configure {showModal.toUpperCase()}
                        </h3>
                        <p className="text-gray-400 mb-4">Agent configuration coming soon...</p>
                        <button
                            className="btn-primary w-full"
                            onClick={() => setShowModal(null)}
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

            {/* Token Dashboard Modal */}
            {showTokenDashboard && (
                <div
                    className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
                    onClick={() => setShowTokenDashboard(false)}
                >
                    <div
                        className="card max-w-lg w-full mx-4"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-lg font-bold text-gradient">
                                Token Estimation
                            </h3>
                            <button
                                className="text-gray-400 hover:text-white text-xl"
                                onClick={() => setShowTokenDashboard(false)}
                            >
                                ×
                            </button>
                        </div>

                        {/* Token Breakdown */}
                        <div className="space-y-3 mb-6">
                            {agents.map(agent => {
                                const isEnabled = enabledAgents.has(agent.id);
                                return (
                                    <div
                                        key={agent.id}
                                        className={`flex justify-between items-center py-2 border-b border-gray-700 ${!isEnabled ? 'opacity-40' : ''}`}
                                    >
                                        <span className="text-sm font-medium">{agent.name}</span>
                                        <div className="text-sm text-gray-400">
                                            <span className="text-blue-400">{isEnabled ? agent.tokens.input.toLocaleString() : 0}</span>
                                            {' / '}
                                            <span className="text-green-400">{isEnabled ? agent.tokens.output.toLocaleString() : 0}</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Totals */}
                        <div className="bg-gray-800/50 rounded-lg p-4 space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">Input Tokens</span>
                                <span className="text-blue-400 font-medium">{tokenEstimate.input.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">Output Tokens</span>
                                <span className="text-green-400 font-medium">{tokenEstimate.output.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm pt-2 border-t border-gray-600">
                                <span className="text-gray-400">Total Tokens</span>
                                <span className="text-white font-bold">{tokenEstimate.total.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">Estimated Cost</span>
                                <span className="text-gradient font-bold">${tokenEstimate.cost}</span>
                            </div>
                        </div>

                        <p className="text-xs text-gray-500 mt-4 text-center">
                            Estimates based on average token usage. Actual usage may vary.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
