import { Link, useLocation } from 'react-router-dom';
import {
    HomeIcon,
    LinkIcon,
    PuzzlePieceIcon,
    CpuChipIcon
} from '@heroicons/react/24/outline';

const navItems = [
    { name: 'Pipeline', path: '/', icon: HomeIcon },
    { name: 'Connectors', path: '/connectors', icon: LinkIcon },
    { name: 'Extensions', path: '/extensions', icon: PuzzlePieceIcon },
    { name: 'Models', path: '/models', icon: CpuChipIcon },
];

export default function Sidebar() {
    const location = useLocation();

    return (
        <aside className="w-64 bg-dark-800 border-r border-dark-700 h-screen fixed left-0 top-0">
            <div className="p-6">
                <h1 className="text-2xl font-bold text-primary-500">SDLC Pipeline</h1>
                <p className="text-xs text-gray-500 mt-1">AI Agent Automation</p>
            </div>

            <nav className="px-4">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all ${isActive
                                    ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/50'
                                    : 'text-gray-400 hover:bg-dark-700 hover:text-white'
                                }`}
                        >
                            <item.icon className="w-5 h-5" />
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-700">
                <div className="text-xs text-gray-500">
                    <div className="flex items-center gap-2 mb-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span>Backend Connected</span>
                    </div>
                    <div className="text-gray-600">Phase 3 - React + Tailwind</div>
                </div>
            </div>
        </aside>
    );
}
