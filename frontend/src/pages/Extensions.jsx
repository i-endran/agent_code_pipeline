import {
    PuzzlePieceIcon,
    WrenchIcon,
    BeakerIcon,
    CircleStackIcon,
    CommandLineIcon,
    PlusIcon
} from '@heroicons/react/24/outline';

const extensions = [
    {
        id: 1,
        name: 'Git Tools',
        author: 'Standard Library',
        version: 'v2.1.0',
        icon: CommandLineIcon,
        description: 'Enables agents to clone, branch, and commit to local repositories.',
        agents: ['ARCHITECT', 'FORGE', 'PHOENIX']
    },
    {
        id: 2,
        name: 'Doc Generator',
        author: 'SDLC Core',
        version: 'v1.0.5',
        icon: CircleStackIcon,
        description: 'Advanced markdown templates for DPIA and Feature Specs.',
        agents: ['SCRIBE']
    },
    {
        id: 3,
        name: 'Browser Search',
        author: 'Community',
        version: 'v0.5.2',
        icon: BeakerIcon,
        description: 'Allows agents to search documentation and StackOverflow.',
        agents: ['ARCHITECT', 'SENTINEL']
    },
];

export default function Extensions() {
    return (
        <div className="pt-8 w-full max-w-6xl mx-auto">
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
                        <button className="text-xs text-[#667eea] hover:underline font-bold">+ Connect Server</button>
                    </div>

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
                </section>

                {/* Installed Tools Section */}
                <section className="space-y-6">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <WrenchIcon className="w-6 h-6 text-[#667eea]" />
                        Installed Capabilities
                    </h2>

                    <div className="space-y-4">
                        {extensions.map(ext => (
                            <div key={ext.id} className="card flex gap-4 hover:border-[#667eea] transition-all group">
                                <div className="p-3 bg-[#1a1b23] rounded-lg h-fit border border-[#2d3748] group-hover:border-[#667eea]/50 transition-colors">
                                    <ext.icon className="w-6 h-6 text-[#667eea]" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-start mb-1">
                                        <h3 className="text-lg font-bold text-white">{ext.name}</h3>
                                        <span className="text-[10px] bg-[#1a1b23] px-2 py-0.5 rounded border border-[#2d3748] text-gray-500 font-mono">
                                            {ext.version}
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-500 mb-4">{ext.description}</p>
                                    <div className="flex flex-wrap gap-2">
                                        {ext.agents.map(agent => (
                                            <span key={agent} className="text-[9px] bg-[#667eea]/10 text-[#667eea] px-2 py-0.5 rounded border border-[#667eea]/20 font-bold">
                                                {agent}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </div>

            <div className="mt-12 flex justify-center">
                <button className="flex items-center gap-2 px-6 py-3 border border-[#2d3748] hover:border-[#667eea] text-gray-400 hover:text-white rounded-xl transition-all">
                    <PlusIcon className="w-5 h-5" />
                    Browse Tool Marketplace
                </button>
            </div>
        </div>
    );
}
