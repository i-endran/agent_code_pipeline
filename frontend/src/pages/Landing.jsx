import { useState } from 'react';
import {
    DocumentTextIcon,
    CubeIcon,
    CodeBracketIcon,
    ChatBubbleLeftRightIcon,
    ShieldCheckIcon,
    RocketLaunchIcon
} from '@heroicons/react/24/outline';

const agents = [
    {
        id: 'scribe',
        name: 'SCRIBE',
        role: 'Requirement Parser',
        icon: DocumentTextIcon,
    },
    {
        id: 'architect',
        name: 'ARCHITECT',
        role: 'Plan Generator',
        icon: CubeIcon,
    },
    {
        id: 'forge',
        name: 'FORGE',
        role: 'Code Executor',
        icon: CodeBracketIcon,
    },
    {
        id: 'herald',
        name: 'HERALD',
        role: 'MR Creator',
        icon: ChatBubbleLeftRightIcon,
    },
    {
        id: 'sentinel',
        name: 'SENTINEL',
        role: 'Code Reviewer',
        icon: ShieldCheckIcon,
    },
    {
        id: 'phoenix',
        name: 'PHOENIX',
        role: 'Releaser',
        icon: RocketLaunchIcon,
    },
];

export default function Landing() {
    const [enabledAgents, setEnabledAgents] = useState(new Set(['scribe', 'architect', 'forge', 'herald']));
    const [showModal, setShowModal] = useState(null);

    const toggleAgent = (agentId) => {
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

    return (
        <div className="py-8">
            {/* SVG Gradient Definition for Icons */}
            <svg width="0" height="0" style={{ position: 'absolute' }}>
                <defs>
                    <linearGradient id="icon-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#667eea" />
                        <stop offset="100%" stopColor="#764ba2" />
                    </linearGradient>
                </defs>
            </svg>

            {/* Hero Section */}
            <header className="mb-10 text-center">
                <h1 className="text-4xl font-bold mb-2 text-gradient">
                    AI Agent Pipeline
                </h1>
                <p className="text-gray-400 text-sm">
                    Configure and deploy 6 specialized agents to automate your SDLC
                </p>
            </header>

            {/* Agent Pipeline */}
            <div className="mb-10 overflow-x-auto pb-4">
                <div className="flex items-start justify-center gap-2 min-w-max px-4">
                    {agents.map((agent, index) => {
                        const isEnabled = enabledAgents.has(agent.id);
                        const Icon = agent.icon;

                        return (
                            <div key={agent.id} className="flex items-center">
                                {/* Agent Card */}
                                <div
                                    className={`agent-box cursor-pointer ${isEnabled ? 'enabled' : ''}`}
                                    onClick={() => toggleAgent(agent.id)}
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
                                        <div className={`toggle-switch ${isEnabled ? 'active' : ''}`}>
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
                <div className="text-center text-xs text-gray-500 mt-4">
                    <p>↻ SENTINEL → FORGE feedback loop for code fixes</p>
                </div>
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

            {/* Modal Placeholder */}
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
        </div>
    );
}
