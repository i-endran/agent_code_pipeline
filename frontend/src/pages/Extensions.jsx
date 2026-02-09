import { useState, useEffect } from 'react';
import axios from 'axios';
import {
    PuzzlePieceIcon,
    WrenchIcon,
    BeakerIcon,
    CircleStackIcon,
    CommandLineIcon,
    PlusIcon,
    ServerIcon
} from '@heroicons/react/24/outline';

const API_BASE = 'http://localhost:8000/api';

const AGENT_STAGES = ['SCRIBE', 'ARCHITECT', 'FORGE', 'SENTINEL', 'PHOENIX'];

export default function Extensions() {
    const [mcpServers, setMcpServers] = useState([]);
    const [connectors, setConnectors] = useState([]);
    const [agentMappings, setAgentMappings] = useState({}); // { stage: [connectorId, ...] }
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            // 1. Fetch MCP Servers & Connectors
            const [mcpRes, connRes] = await Promise.all([
                axios.get(`${API_BASE}/mcp/servers`),
                axios.get(`${API_BASE}/connectors`)
            ]);

            setMcpServers(mcpRes.data);
            setConnectors(connRes.data);

            // 2. Fetch Agent Mappings to build badges
            const mappingPromises = AGENT_STAGES.map(stage =>
                axios.get(`${API_BASE}/agents/${stage.toLowerCase()}/connectors`)
                    .then(res => ({ stage, connectors: res.data }))
            );

            const mappingsResult = await Promise.all(mappingPromises);
            const mappingMap = {};
            mappingsResult.forEach(item => {
                // Store set of connector IDs for each stage
                mappingMap[item.stage] = new Set(item.connectors.map(c => c.id));
            });
            setAgentMappings(mappingMap);

            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch extensions data:", error);
            setLoading(false);
        }
    };

    const getAgentBadges = (connectorId) => {
        return AGENT_STAGES.filter(stage =>
            agentMappings[stage] && agentMappings[stage].has(connectorId)
        );
    };

    if (loading) return <div className="p-8 text-gray-400">Loading extensions...</div>;

    return (
        <div className="pt-8 w-full max-w-6xl mx-auto px-4">
            <header className="mb-10">
                <h1 className="text-3xl font-bold text-gradient mb-2">Extensions & Tools</h1>
                <p className="text-gray-400">Configure custom capabilities and MCP server integrations</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* MCP Servers Section */}
                <section className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-bold text-white flex items-center gap-2">
                            <PuzzlePieceIcon className="w-6 h-6 text-[#667eea]" />
                            MCP Servers
                        </h2>
                        {/* Placeholder for Add Server - functionality pending per requirements */}
                        <button className="text-xs text-[#667eea] hover:underline font-bold">+ Connect Server</button>
                    </div>

                    {mcpServers.length === 0 ? (
                        <div className="card border-dashed">
                            <div className="text-center py-10">
                                <div className="w-16 h-16 bg-[#1a1b23] rounded-full flex items-center justify-center mx-auto mb-4 border border-[#2d3748]">
                                    <PuzzlePieceIcon className="w-8 h-8 text-gray-600" />
                                </div>
                                <h3 className="text-white font-medium mb-1">No MCP Servers Connected</h3>
                                <p className="text-xs text-gray-500 max-w-[250px] mx-auto">
                                    Connect external tool providers through the Model Context Protocol.
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {mcpServers.map(server => (
                                <div key={server.id} className="card flex justify-between items-center group">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-[#667eea]/10 rounded-lg">
                                            <ServerIcon className="w-6 h-6 text-[#667eea]" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-white">{server.name}</h3>
                                            <p className="text-xs text-gray-500">{server.url}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xs font-bold text-green-400 mb-1">Active</div>
                                        <div className="text-[10px] text-gray-500">{server.tools.length} tools</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>

                {/* Installed Capabilities (Connectors + MCP Tools) */}
                <section className="space-y-6">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <WrenchIcon className="w-6 h-6 text-[#667eea]" />
                        Installed Capabilities
                    </h2>

                    <div className="space-y-4">
                        {/* 1. Connectors */}
                        {connectors.map(conn => (
                            <div key={`conn-${conn.id}`} className="card flex gap-4 hover:border-[#667eea] transition-all group">
                                <div className="p-3 bg-[#1a1b23] rounded-lg h-fit border border-[#2d3748] group-hover:border-[#667eea]/50 transition-colors">
                                    <CommandLineIcon className="w-6 h-6 text-[#667eea]" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-start mb-1">
                                        <h3 className="text-lg font-bold text-white max-w-[200px] truncate">{conn.name}</h3>
                                        <span className="text-[10px] bg-[#1a1b23] px-2 py-0.5 rounded border border-[#2d3748] text-gray-500 font-mono">
                                            CONNECTOR
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-500 mb-4 capitalize">{conn.type} Integration</p>
                                    <div className="flex flex-wrap gap-2">
                                        {getAgentBadges(conn.id).length > 0 ? (
                                            getAgentBadges(conn.id).map(agent => (
                                                <span key={agent} className="text-[9px] bg-[#667eea]/10 text-[#667eea] px-2 py-0.5 rounded border border-[#667eea]/20 font-bold">
                                                    {agent}
                                                </span>
                                            ))
                                        ) : (
                                            <span className="text-[9px] text-gray-600 italic">Unassigned</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}

                        {/* 2. MCP Tools */}
                        {mcpServers.flatMap(s => s.tools).map(tool => (
                            <div key={`tool-${tool.id}`} className="card flex gap-4 hover:border-[#667eea] transition-all group">
                                <div className="p-3 bg-[#1a1b23] rounded-lg h-fit border border-[#2d3748] group-hover:border-[#667eea]/50 transition-colors">
                                    <BeakerIcon className="w-6 h-6 text-pink-500" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-start mb-1">
                                        <h3 className="text-lg font-bold text-white">{tool.name}</h3>
                                        <span className="text-[10px] bg-[#1a1b23] px-2 py-0.5 rounded border border-[#2d3748] text-gray-500 font-mono">
                                            MCP TOOL
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-500 mb-4">{tool.description || "No description provided."}</p>
                                    <div className="flex flex-wrap gap-2">
                                        <span className="text-[9px] bg-pink-500/10 text-pink-500 px-2 py-0.5 rounded border border-pink-500/20 font-bold">
                                            GLOBAL
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
}
