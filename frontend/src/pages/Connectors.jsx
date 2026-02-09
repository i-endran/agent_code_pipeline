import {
    PlusIcon,
    ChatBubbleLeftRightIcon,
    CodeBracketIcon,
    CheckCircleIcon,
    CloudIcon
} from '@heroicons/react/24/outline';

const connectors = [
    {
        id: 1,
        name: 'GitHub',
        type: 'Source Control',
        status: 'connected',
        icon: CodeBracketIcon,
        details: 'sdlc-agent-bot / main'
    },
    {
        id: 2,
        name: 'Slack',
        type: 'Communication',
        status: 'connected',
        icon: ChatBubbleLeftRightIcon,
        details: '#dev-ops-pipeline'
    },
    {
        id: 3,
        name: 'GitLab',
        type: 'Source Control',
        status: 'disconnected',
        icon: CloudIcon,
        details: 'Not configured'
    },
];

export default function Connectors() {
    return (
        <div className="pt-8 w-full max-w-6xl mx-auto">
            <header className="mb-10 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-gradient mb-2">Connectors</h1>
                    <p className="text-gray-400">Manage your Git repositories and communication platform integrations</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-[#667eea] hover:bg-[#764ba2] text-white rounded-lg transition-all font-medium">
                    <PlusIcon className="w-5 h-5" />
                    Add Connector
                </button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {connectors.map((connector) => (
                    <div key={connector.id} className="card hover:border-[#667eea] transition-all cursor-pointer">
                        <div className="flex justify-between items-start mb-6">
                            <div className="p-3 bg-[#1a1b23] rounded-xl border border-[#2d3748]">
                                <connector.icon className="w-8 h-8 text-[#667eea]" />
                            </div>
                            <span className={`status-badge ${connector.status === 'connected' ? 'status-completed' : 'status-failed'}`}>
                                {connector.status}
                            </span>
                        </div>

                        <h3 className="text-xl font-bold text-white mb-1">{connector.name}</h3>
                        <p className="text-sm text-gray-500 mb-4">{connector.type}</p>

                        <div className="pt-4 border-t border-[#2d3748] flex items-center justify-between">
                            <span className="text-xs text-gray-400 italic">{connector.details}</span>
                            {connector.status === 'connected' && <CheckCircleIcon className="w-5 h-5 text-green-500" />}
                        </div>
                    </div>
                ))}
            </div>

            <section className="mt-12">
                <h2 className="text-xl font-bold text-white mb-6">Available Webhooks</h2>
                <div className="bg-[#1a1b23] border border-[#2d3748] rounded-xl p-6">
                    <div className="flex items-center justify-between py-4 border-b border-[#2d3748]">
                        <div>
                            <div className="text-white font-medium">Task Completion Webhook</div>
                            <div className="text-xs text-gray-500">Trigger external CI/CD when a task completes</div>
                        </div>
                        <code className="text-xs bg-black px-3 py-1 rounded text-[#667eea]">https://api.example.com/webhook</code>
                    </div>
                    <div className="flex items-center justify-between py-4">
                        <div>
                            <div className="text-white font-medium">Error Notification Webhook</div>
                            <div className="text-xs text-gray-500">Alert your team when an agent fails</div>
                        </div>
                        <code className="text-xs bg-black px-3 py-1 rounded text-[#667eea]">https://hooks.slack.com/services/...</code>
                    </div>
                </div>
            </section>
        </div>
    );
}
