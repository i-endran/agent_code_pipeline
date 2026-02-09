import { useState } from 'react';

export default function Models() {
    const [apiKey, setApiKey] = useState('');
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        // TODO: Save to backend
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">Model Configuration</h1>

            <div className="card mb-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h2 className="text-xl font-semibold">Google Gemini</h2>
                        <p className="text-sm text-gray-400">Primary LLM provider for all agents</p>
                    </div>
                    <div className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                        Active
                    </div>
                </div>

                <div className="mb-4">
                    <label className="label">API Key</label>
                    <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="Enter your Gemini API key"
                        className="input"
                    />
                </div>

                <button
                    onClick={handleSave}
                    className="btn-primary"
                >
                    {saved ? '✓ Saved' : 'Save Configuration'}
                </button>
            </div>

            <div className="card opacity-50">
                <h2 className="text-xl font-semibold mb-2">Other Providers</h2>
                <p className="text-gray-400 text-sm">
                    Additional LLM providers (OpenAI, Anthropic) can be configured in future phases.
                </p>
            </div>
        </div>
    );
}
