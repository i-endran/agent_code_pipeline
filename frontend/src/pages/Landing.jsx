import { useState } from 'react';
import {
    DocumentTextIcon,
    CubeIcon,
    CodeBracketIcon,
    ShieldCheckIcon,
    RocketLaunchIcon
} from '@heroicons/react/24/outline';

const agents = [
    {
        id: 'scribe',
        name: 'SCRIBE',
        description: 'Document Generator',
        icon: DocumentTextIcon,
        color: 'from-blue-500 to-cyan-500',
    },
    {
        id: 'architect',
        name: 'ARCHITECT',
        description: 'Plan Generator',
        icon: CubeIcon,
        color: 'from-purple-500 to-pink-500',
    },
    {
        id: 'forge',
        name: 'FORGE',
        description: 'Code Executor',
        icon: CodeBracketIcon,
        color: 'from-orange-500 to-red-500',
    },
    {
        id: 'sentinel',
        name: 'SENTINEL',
        description: 'Code Reviewer',
        icon: ShieldCheckIcon,
        color: 'from-green-500 to-emerald-500',
    },
    {
        id: 'phoenix',
        name: 'PHOENIX',
        description: 'Releaser',
        icon: RocketLaunchIcon,
        color: 'from-yellow-500 to-orange-500',
    },
];

export default function Landing() {
    const [enabledAgents, setEnabledAgents] = useState(new Set());

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

    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <header className="mb-16 text-center">
                <h1 className="text-7xl font-bold mb-4 text-gradient leading-tight">
                    AI Agent Pipeline
                </h1>
                <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                    Configure and deploy 5 specialized agents to automate your SDLC workflow
                </p>
            </header>

            {/* Agent Pipeline */}
            <div className="mb-12">
                <div className="flex items-center justify-center gap-6 mb-8">
                    {agents.map((agent, index) => {
                        const isEnabled = enabledAgents.has(agent.id);
                        const Icon = agent.icon;

                        return (
                            <div key={agent.id} className="relative">
                                {/* Agent Card */}
                                <div
                                    className={`agent-card ${isEnabled ? 'enabled' : 'disabled'} w-48 h-64`}
                                    onClick={() => toggleAgent(agent.id)}
                                >
                                    {/* Icon with Gradient */}
                                    <div className={`w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${agent.color} p-4 flex items-center justify-center`}>
                                        <Icon className="w-full h-full text-white" />
                                    </div>

                                    {/* Agent Name */}
                                    <h3 className="text-xl font-bold text-center mb-2">{agent.name}</h3>
                                    <p className="text-sm text-gray-400 text-center mb-4">{agent.description}</p>

                                    {/* Toggle Switch */}
                                    <div className="flex justify-center">
                                        <div className={`toggle-switch ${isEnabled ? 'active' : ''}`}>
                                            <div className="toggle-slider"></div>
                                        </div>
                                    </div>

                                    {/* Configure Button */}
                                    {isEnabled && (
                                        <button className="mt-4 w-full text-blue-400 text-sm font-medium hover:text-blue-300 transition-colors">
                                            ⚙ Configure
                                        </button>
                                    )}
                                </div>

                                {/* Connection Line */}
                                {index < agents.length - 1 && (
                                    <div className="connection-line"></div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Info Text */}
                <div className="text-center text-sm text-gray-500">
                    <p>↻ SENTINEL → FORGE feedback loop for code fixes</p>
                </div>
            </div>

            {/* Submit Section */}
            <div className="glass rounded-3xl p-8 max-w-2xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-2xl font-semibold mb-1">Ready to Deploy</h2>
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
        </div>
    );
}
