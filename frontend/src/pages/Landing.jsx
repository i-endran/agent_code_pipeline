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
    },
    {
        id: 'architect',
        name: 'ARCHITECT',
        description: 'Plan Generator',
        icon: CubeIcon,
    },
    {
        id: 'forge',
        name: 'FORGE',
        description: 'Code Executor',
        icon: CodeBracketIcon,
    },
    {
        id: 'sentinel',
        name: 'SENTINEL',
        description: 'Code Reviewer',
        icon: ShieldCheckIcon,
    },
    {
        id: 'phoenix',
        name: 'PHOENIX',
        description: 'Releaser',
        icon: RocketLaunchIcon,
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
            <header className="mb-12 text-center">
                <h1 className="text-5xl font-bold mb-3 text-gradient-original">
                    AI Agent Pipeline
                </h1>
                <p className="text-base text-gray-400">
                    Configure and deploy 6 specialized agents to automate your SDLC
                </p>
            </header>

            {/* Agent Pipeline */}
            <div className="mb-10">
                <div className="flex items-center justify-center gap-4">
                    {agents.map((agent, index) => {
                        const isEnabled = enabledAgents.has(agent.id);
                        const Icon = agent.icon;

                        return (
                            <div key={agent.id} className="relative flex items-center">
                                {/* Agent Card */}
                                <div
                                    className={`agent-card-original ${isEnabled ? 'enabled' : ''} w-40`}
                                    onClick={() => toggleAgent(agent.id)}
                                >
                                    {/* Icon with Gradient */}
                                    <div className="mb-3">
                                        <Icon className="w-10 h-10 mx-auto text-gradient-icon" />
                                    </div>

                                    {/* Agent Name */}
                                    <h3 className="text-base font-bold text-center mb-1 text-white">{agent.name}</h3>
                                    <p className="text-xs text-gray-500 text-center mb-3">{agent.description}</p>

                                    {/* Toggle Switch */}
                                    <div className="flex justify-center mb-3">
                                        <div className={`toggle-switch-original ${isEnabled ? 'active' : ''}`}>
                                            <div className="toggle-slider-original"></div>
                                        </div>
                                    </div>

                                    {/* Configure Button */}
                                    {isEnabled && (
                                        <button className="w-full text-xs text-blue-400 hover:text-blue-300 transition-colors font-medium">
                                            ⚙ Configure
                                        </button>
                                    )}
                                </div>

                                {/* Connection Arrow */}
                                {index < agents.length - 1 && (
                                    <div className="text-purple-500 text-xl px-2 opacity-50">
                                        →
                                    </div>
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

            {/* Submit Section */}
            <div className="glass-original rounded-xl p-6 max-w-2xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-xl font-semibold mb-1">Ready to Deploy</h2>
                        <p className="text-gray-400 text-sm">
                            {enabledAgents.size} agent{enabledAgents.size !== 1 ? 's' : ''} selected
                        </p>
                    </div>
                    <button
                        className="btn-primary-original"
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
