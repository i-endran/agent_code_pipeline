import { useState, useMemo, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import {
    DocumentTextIcon,
    CubeIcon,
    CodeBracketIcon,
    ShieldCheckIcon,
    RocketLaunchIcon,
    ChartBarIcon,
    ClockIcon,
    ArrowsRightLeftIcon,
    XMarkIcon
} from '@heroicons/react/24/outline';

const API_BASE = 'http://localhost:8000/api';

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
    const navigate = useNavigate();
    const [enabledAgents, setEnabledAgents] = useState(new Set(['scribe', 'architect', 'forge', 'sentinel', 'phoenix']));
    const [agentActivity, setAgentActivity] = useState({});

    // Deployment Form
    const [repoUrl, setRepoUrl] = useState('');
    const [branch, setBranch] = useState('main');
    const [taskDescription, setTaskDescription] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Scribe Specific State
    const [scribePrompt, setScribePrompt] = useState('');
    const [selectedDocs, setSelectedDocs] = useState(new Set(['feature_doc']));
    const [outputFormat, setOutputFormat] = useState('markdown');

    // Modal State
    const [showModal, setShowModal] = useState(null); // agentId
    const [editConfig, setEditConfig] = useState({});
    const [availableConnectors, setAvailableConnectors] = useState([]);
    const [assignedConnectors, setAssignedConnectors] = useState([]);

    // Initial load and polling
    useEffect(() => {
        fetchActivity();
        fetchConnectors();
        const interval = setInterval(fetchActivity, 3000);
        return () => clearInterval(interval);
    }, []);

    const fetchActivity = async () => {
        try {
            const res = await axios.get(`${API_BASE}/agents/activity`);
            setAgentActivity(res.data);
        } catch (error) {
            console.error("Failed to fetch activity:", error);
        }
    };

    const fetchConnectors = async () => {
        try {
            const res = await axios.get(`${API_BASE}/connectors`);
            setAvailableConnectors(res.data);
        } catch (error) {
            console.error("Failed to fetch connectors:", error);
        }
    };

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

    const handleOpenModal = async (agentId) => {
        setShowModal(agentId);
        // Fetch current config
        try {
            const res = await axios.get(`${API_BASE}/agents/${agentId}`);
            setEditConfig({
                model: res.data.model,
                temperature: res.data.temperature,
                max_tokens: res.data.max_tokens,
                system_prompt: res.data.system_prompt || ""
            });

            // Fetch prompt specifically if not in main response (depends on backend)
            // But let's assume /agents/{id} returns merged config
            const promptRes = await axios.get(`${API_BASE}/agents/${agentId}/prompt`);
            setEditConfig(prev => ({ ...prev, system_prompt: promptRes.data.system_prompt }));

            // Fetch assignments
            const connRes = await axios.get(`${API_BASE}/agents/${agentId}/connectors`);
            setAssignedConnectors(connRes.data);

        } catch (error) {
            console.error("Failed to fetch agent details:", error);
            // Fallback defaults if new agent
            setEditConfig({ model: 'gpt-4o', temperature: 0.7, max_tokens: 2000, system_prompt: '' });
        }
    };

    const handleSaveConfig = async () => {
        try {
            await axios.patch(`${API_BASE}/agents/${showModal}`, editConfig);
            alert("Configuration saved!");
            setShowModal(null);
        } catch (error) {
            console.error("Failed to save config:", error);
            alert("Failed to save configuration");
        }
    };

    const handleToggleConnector = async (connectorId, isAssigned) => {
        try {
            if (isAssigned) {
                await axios.delete(`${API_BASE}/agents/${showModal}/connectors/${connectorId}`);
            } else {
                await axios.post(`${API_BASE}/agents/${showModal}/connectors`, { connector_id: connectorId });
            }
            // Refresh assignments
            const res = await axios.get(`${API_BASE}/agents/${showModal}/connectors`);
            setAssignedConnectors(res.data);
        } catch (error) {
            console.error("Failed to toggle connector:", error);
        }
    };


    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post(`${API_BASE}/scribe/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setTaskDescription(res.data.text);
            alert(`File uploaded: ${res.data.filename}`);
        } catch (error) {
            console.error("Upload failed:", error);
            alert("File upload failed.");
        }
    };

    const toggleDoc = (doc) => {
        setSelectedDocs(prev => {
            const newSet = new Set(prev);
            if (newSet.has(doc)) newSet.delete(doc);
            else newSet.add(doc);
            return newSet;
        });
    };

    const handleRunPipeline = async () => {
        if (!repoUrl) {
            alert('Repository URL is required');
            return;
        }
        if (!taskDescription) {
            alert('Task description is required');
            return;
        }

        setIsSubmitting(true);
        try {
            const payload = {
                repo_url: repoUrl,
                branch: branch,
                requirements: taskDescription,
                agents: {
                    scribe: { enabled: enabledAgents.has('scribe') },
                    architect: { enabled: enabledAgents.has('architect') },
                    forge: { enabled: enabledAgents.has('forge') },
                    sentinel: { enabled: enabledAgents.has('sentinel') },
                    phoenix: { enabled: enabledAgents.has('phoenix') }
                },
                scribe_config: {
                    user_prompt: scribePrompt,
                    selected_documents: Array.from(selectedDocs),
                    output_format: outputFormat
                }
            };

            const res = await axios.post(`${API_BASE}/v1/pipelines/run`, payload);
            alert(`Pipeline started! Task ID: ${res.data.task_id}`);
            // Optional: navigate to specific task view if it existed
            setTaskDescription(''); // Reset form
        } catch (error) {
            console.error("Failed to start pipeline:", error);
            alert("Failed to start pipeline. Check console for details.");
        } finally {
            setIsSubmitting(false);
        }
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

            <div className="w-full max-w-6xl flex flex-col items-center px-4">
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
                                            onClick={(e) => { e.stopPropagation(); handleOpenModal(agent.id); }}
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
                    <div className="card h-full flex flex-col">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h2 className="text-lg font-semibold mb-1 text-white">Create New Task</h2>
                                <p className="text-gray-400 text-sm">{enabledAgents.size} agent{enabledAgents.size !== 1 ? 's' : ''} selected</p>
                            </div>
                        </div>

                        <div className="space-y-4 flex-1">
                            <div>
                                <label className="label">Task Description / Requirements</label>
                                <textarea
                                    className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm h-24 resize-none focus:border-[#667eea] outline-none"
                                    placeholder="Describe the feature or bug fix..."
                                    value={taskDescription}
                                    onChange={e => setTaskDescription(e.target.value)}
                                />
                                <div className="mt-2 text-right">
                                    <input
                                        type="file"
                                        id="upload-req"
                                        className="hidden"
                                        onChange={handleFileUpload}
                                        accept=".txt,.md,.docx"
                                    />
                                    <label htmlFor="upload-req" className="text-xs text-[#667eea] cursor-pointer hover:text-white">
                                        📄 Upload Requirements (txt, md, docx)
                                    </label>
                                </div>
                            </div>

                            {enabledAgents.has('scribe') && (
                                <div className="p-3 bg-[#1a1b23] rounded-lg border border-[#2d3748] space-y-3">
                                    <h3 className="text-sm font-semibold text-white">Scribe Configuration</h3>

                                    <div>
                                        <label className="block text-xs text-gray-400 mb-1">Documents to Generate</label>
                                        <div className="flex gap-2">
                                            {['feature_doc', 'dpia', 'data_flow'].map(doc => (
                                                <button
                                                    key={doc}
                                                    className={`px-2 py-1 text-xs rounded border ${
                                                        selectedDocs.has(doc)
                                                        ? 'bg-[#667eea]/20 border-[#667eea] text-[#667eea]'
                                                        : 'border-[#2d3748] text-gray-500 hover:text-gray-300'
                                                    }`}
                                                    onClick={() => toggleDoc(doc)}
                                                >
                                                    {doc.replace('_', ' ').toUpperCase()}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-xs text-gray-400 mb-1">Output Format</label>
                                        <select
                                            className="w-full bg-black border border-[#2d3748] rounded p-1 text-white text-xs"
                                            value={outputFormat}
                                            onChange={e => setOutputFormat(e.target.value)}
                                        >
                                            <option value="markdown">Markdown</option>
                                            <option value="docx">Microsoft Word (.docx)</option>
                                            <option value="cloud">Cloud Tool (Not Implemented)</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-xs text-gray-400 mb-1">Scribe Prompt (User Notes)</label>
                                        <textarea
                                            className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-xs h-16 resize-none"
                                            placeholder="Additional context for requirements analysis..."
                                            value={scribePrompt}
                                            onChange={e => setScribePrompt(e.target.value)}
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="label">Repository URL</label>
                                    <input
                                        type="text"
                                        placeholder="https://github.com/username/repo"
                                        className="input"
                                        value={repoUrl}
                                        onChange={e => setRepoUrl(e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label className="label">Target Branch</label>
                                    <input
                                        type="text"
                                        placeholder="main"
                                        className="input"
                                        value={branch}
                                        onChange={e => setBranch(e.target.value)}
                                    />
                                </div>
                            </div>
                        </div>

                        <button
                            className="btn-primary w-full mt-6 flex justify-center items-center gap-2"
                            disabled={enabledAgents.size === 0 || isSubmitting}
                            onClick={handleRunPipeline}
                        >
                            {isSubmitting ? (
                                <>
                                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                    Submitting...
                                </>
                            ) : '🚀 Run Pipeline'}
                        </button>
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
                            const activity = agentActivity[agentId] || { status: 'idle', current: null, next: null };
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
                                                    <ClockIcon className="w-3 h-3" /> {activity.current.time || '0s'}
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

            {/* Config Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="bg-[#1a1b23] w-full max-w-2xl rounded-xl border border-[#2d3748] flex flex-col max-h-[90vh]">
                        <div className="p-6 border-b border-[#2d3748] flex justify-between items-center">
                            <h3 className="text-xl font-bold text-white capitalize">Configure {showModal}</h3>
                            <button onClick={() => setShowModal(null)} className="text-gray-400 hover:text-white">
                                <XMarkIcon className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto flex-1 space-y-6">
                            {/* Connector Assignment */}
                            <div>
                                <h4 className="text-sm font-bold text-white mb-3">Assigned Connectors</h4>
                                <div className="flex flex-wrap gap-2">
                                    {availableConnectors.map(conn => {
                                        const isAssigned = assignedConnectors.some(ac => ac.id === conn.id);
                                        return (
                                            <button
                                                key={conn.id}
                                                onClick={() => handleToggleConnector(conn.id, isAssigned)}
                                                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${isAssigned
                                                        ? 'bg-[#667eea]/20 border-[#667eea] text-[#667eea]'
                                                        : 'bg-black border-[#2d3748] text-gray-400 hover:border-gray-500'
                                                    }`}
                                            >
                                                {conn.name} ({conn.type})
                                                {isAssigned && " ✓"}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">Model ID</label>
                                    <input
                                        className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm"
                                        value={editConfig.model || ''}
                                        onChange={e => setEditConfig({ ...editConfig, model: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">Temperature</label>
                                    <input
                                        type="number" step="0.1"
                                        className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm"
                                        value={editConfig.temperature || 0}
                                        onChange={e => setEditConfig({ ...editConfig, temperature: parseFloat(e.target.value) })}
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs text-gray-400 mb-1">System Prompt</label>
                                <textarea
                                    className="w-full bg-black border border-[#2d3748] rounded p-2 text-white text-sm font-mono h-40"
                                    value={editConfig.system_prompt || ''}
                                    onChange={e => setEditConfig({ ...editConfig, system_prompt: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="p-6 border-t border-[#2d3748] flex justify-end gap-3">
                            <button onClick={() => setShowModal(null)} className="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
                            <button onClick={handleSaveConfig} className="px-4 py-2 bg-[#667eea] text-white rounded">Save Configuration</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
