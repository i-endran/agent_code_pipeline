import { useState, useMemo } from 'react';
import {
    DocumentTextIcon,
    CubeIcon,
    CodeBracketIcon,
    ShieldCheckIcon,
    RocketLaunchIcon,
    ChartBarIcon,
    ClockIcon,
    CpuChipIcon,
    ArrowsRightLeftIcon
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

// Per-Agent Activity Data (Mock)
const agentActivity = {
    scribe: {
        status: 'running',
        current: { name: 'PRD: Customer Dashboard', progress: 65, time: '1m 20s' },
        next: { name: 'API Spec: Auth Service' }
    },
    architect: {
        status: 'idle',
        current: null,
        next: { name: 'System Design: Data Pipeline' }
    },
    forge: {
        status: 'running',
        current: { name: 'Implementing Auth Context', progress: 30, time: '4m 10s' },
        next: { name: 'Unit Tests: Login Flow' }
    },
    sentinel: {
        status: 'running',
        current: { name: 'Reviewing PR #102', progress: 90, time: '12m 45s' },
        next: null
    }
};

export default function Landing() {
    const [enabledAgents, setEnabledAgents] = useState(new Set());
    const [showModal, setShowModal] = useState(null);

    // Sequential agent selection logic
    const canToggleAgent = (agentId) => {
        const agentIndex = agents.findIndex(a => a.id === agentId);
        if (enabledAgents.has(agentId)) {
            for (let i = agentIndex + 1; i < agents.length; i++) {
                if (enabledAgents.has(agents[i].id)) return false;
            }
            return true;
        } else {
            for (let i = 0; i < agentIndex; i++) {
                if (!enabledAgents.has(agents[i].id)) return false;
            }
            return true;
        }
    };

    const toggleAgent = (agentId) => {
        if (!canToggleAgent(agentId)) return;
        setEnabledAgents(prev => {
            const newSet = new Set(prev);
            if (newSet.has(agentId)) newSet.delete(agentId);
            else newSet.add(agentId);
            return newSet;
        });
    };

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
        <div className="pt-8 pb-8 flex flex-col items-center w-full">
            {/* SVG Gradient */}
            <svg width="0" height="0" style={{ position: 'absolute' }}>
                <defs>
                    <linearGradient id="icon-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#667eea" />
                        <stop offset="100%" stopColor="#764ba2" />
                    </linearGradient>
                </defs>
            </svg>

            <div className="w-full max-w-6xl flex flex-col items-center">
                {/* Hero Section */}
                <header className="mb-12 text-center">
                    <h1 className="text-4xl font-bold mb-3 text-gradient">AI Agent Pipeline</h1>
                    <p className="text-gray-400 text-sm">Configure and deploy 5 specialized agents to automate your SDLC</p>
                </header>

                {/* Agent Pipeline */}
                <div className="mb-8 w-full overflow-x-auto pb-6 scrollbar-hidden">
                    <div className="flex items-start justify-center gap-2 min-w-max px-8 pt-6">
                        {agents.map((agent, index) => {
                            const isEnabled = enabledAgents.has(agent.id);
                            const canToggle = canToggleAgent(agent.id);
                            const Icon = agent.icon;
                            return (
                                <div key={agent.id} className="flex items-center">
                                    <div
                                        className={`agent-box ${isEnabled ? 'enabled' : ''} ${!canToggle ? 'locked' : ''}`}
                                        onClick={() => toggleAgent(agent.id)}
                                    >
                                        <div className="agent-icon">
                                            <Icon className="w-10 h-10" style={{ stroke: 'url(#icon-gradient)' }} />
                                        </div>
                                        <div className="agent-name">{agent.name}</div>
                                        <div className="agent-role">{agent.role}</div>
                                        <div className="agent-toggle">
                                            <div className={`toggle-switch ${isEnabled ? 'active' : ''} ${!canToggle ? 'disabled' : ''}`}>
                                                <div className="toggle-slider"></div>
                                            </div>
                                        </div>
                                        <button
                                            className="btn-config"
                                            onClick={(e) => { e.stopPropagation(); setShowModal(agent.id); }}
                                            disabled={!isEnabled}
                                        >
                                            ⚙ Configure
                                        </button>
                                    </div>
                                    {index < agents.length - 1 && <div className="pipeline-connector">→</div>}
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div className="text-center text-xs text-gray-500 mb-10">
                    <p>↻ SENTINEL → FORGE feedback loop for code fixes</p>
                </div>

                {/* Deployment & Estimation Section (Side by Side) */}
                <div className="w-full grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
                    {/* Left: Ready to Deploy */}
                    <div className="card h-full">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h2 className="text-lg font-semibold mb-1 text-white">Ready to Deploy</h2>
                                <p className="text-gray-400 text-sm">{enabledAgents.size} agent{enabledAgents.size !== 1 ? 's' : ''} selected</p>
                            </div>
                            <button className="btn-primary" disabled={enabledAgents.size === 0}>🚀 Run Pipeline</button>
                        </div>
                        <div className="mb-4">
                            <label className="label">Repository URL</label>
                            <input type="text" placeholder="https://github.com/username/repo" className="input" />
                        </div>
                        <div>
                            <label className="label">Target Branch</label>
                            <input type="text" placeholder="main" className="input" />
                        </div>
                    </div>

                    {/* Right: Token Estimation */}
                    <div className="card h-full flex flex-col">
                        <div className="flex items-center gap-2 mb-6">
                            <ChartBarIcon className="w-6 h-6 text-[#667eea]" />
                            <h2 className="text-lg font-semibold text-white">Token Estimation</h2>
                        </div>
                        <div className="flex-1 space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-[#1a1b23] p-3 rounded-lg border border-[#2d3748]">
                                    <div className="text-xs text-gray-400 mb-1">Input Tokens</div>
                                    <div className="text-blue-400 font-bold text-lg">{tokenEstimate.input.toLocaleString()}</div>
                                </div>
                                <div className="bg-[#1a1b23] p-3 rounded-lg border border-[#2d3748]">
                                    <div className="text-xs text-gray-400 mb-1">Output Tokens</div>
                                    <div className="text-green-400 font-bold text-lg">{tokenEstimate.output.toLocaleString()}</div>
                                </div>
                            </div>
                            <div className="bg-gradient-to-r from-[rgba(102,126,234,0.1)] to-[rgba(118,75,162,0.1)] p-4 rounded-lg border border-[#667eea]/30 flex justify-between items-center mt-auto">
                                <div>
                                    <div className="text-sm text-gray-300">Total Estimated Cost</div>
                                    <div className="text-xs text-gray-500">Based on current model rates</div>
                                </div>
                                <div className="text-2xl font-bold text-gradient">${tokenEstimate.cost}</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Agent Activity Queue Section */}
                <div className="w-full">
                    <div className="flex items-center gap-3 mb-6">
                        <ArrowsRightLeftIcon className="w-6 h-6 text-gray-400" />
                        <h2 className="text-xl font-bold text-white">Agent Activity</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                        {['scribe', 'architect', 'forge', 'sentinel'].map(agentId => {
                            const activity = agentActivity[agentId];
                            const agentName = agentId.toUpperCase();
                            const isIdle = activity.status === 'idle';

                            return (
                                <div key={agentId} className={`task-card ${isIdle ? 'idle' : ''}`}>
                                    <div className="flex justify-between items-start mb-3">
                                        <span className={`status-badge ${isIdle ? 'status-pending' : 'status-running'}`}>
                                            {activity.status}
                                        </span>
                                        <span className="text-xs font-bold text-[#667eea]">{agentName}</span>
                                    </div>

                                    {/* Current Task */}
                                    {activity.current ? (
                                        <>
                                            <h3 className="task-name line-clamp-1">{activity.current.name}</h3>
                                            <div className="task-meta mt-4">
                                                <span className="flex items-center gap-1">
                                                    <ClockIcon className="w-3 h-3" /> {activity.current.time}
                                                </span>
                                                <span>{activity.current.progress}%</span>
                                            </div>
                                            <div className="w-full bg-gray-700 h-1.5 rounded-full mt-2 overflow-hidden">
                                                <div
                                                    className="h-full rounded-full bg-blue-500 transition-all duration-500"
                                                    style={{ width: `${activity.current.progress}%` }}
                                                ></div>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="py-2">
                                            <h3 className="task-name italic text-gray-600">Waiting for input...</h3>
                                            <div className="h-1.5 mt-6"></div>
                                        </div>
                                    )}

                                    {/* Next Task in Queue */}
                                    <div className="next-task-box">
                                        <span className="next-task-label">Next in Queue</span>
                                        <div className="next-task-name">
                                            {activity.next ? activity.next.name : 'Queue Empty'}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Agent Modal */}
            {showModal && (
                <div
                    className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm"
                    onClick={() => setShowModal(null)}
                >
                    <div className="card max-w-md w-full mx-4" onClick={e => e.stopPropagation()}>
                        <h3 className="text-lg font-bold mb-4 text-gradient">Configure {showModal.toUpperCase()}</h3>
                        <p className="text-gray-400 mb-6">Configuration options for this agent...</p>
                        <button className="btn-primary w-full" onClick={() => setShowModal(null)}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
}
