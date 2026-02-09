export default function Landing() {
    return (
        <div>
            <header className="mb-8">
                <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                    AI Agent Pipeline
                </h1>
                <p className="text-gray-400 text-lg">
                    Configure and execute your SDLC automation workflow
                </p>
            </header>

            <div className="card">
                <h2 className="text-2xl font-semibold mb-4">Agent Pipeline</h2>
                <p className="text-gray-400 mb-6">
                    The agent pipeline components will be migrated here from the vanilla JS version.
                </p>

                <div className="grid grid-cols-5 gap-4">
                    {['SCRIBE', 'ARCHITECT', 'FORGE', 'SENTINEL', 'PHOENIX'].map((agent, idx) => (
                        <div
                            key={agent}
                            className="bg-dark-700 border border-dark-600 rounded-lg p-4 text-center hover:border-primary-500 transition-colors cursor-pointer"
                        >
                            <div className="w-12 h-12 bg-primary-600 rounded-full mx-auto mb-2 flex items-center justify-center text-xl font-bold">
                                {idx + 1}
                            </div>
                            <div className="text-sm font-medium">{agent}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
