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
        <aside className="sidebar">
            {/* Logo */}
            <div className="p-5 border-b border-[#2d3748]">
                <h1 className="text-lg font-bold text-gradient">SDLC Pipeline</h1>
                <p className="text-xs text-gray-500 mt-0.5">AI Agent Automation</p>
            </div>

            {/* Navigation */}
            <nav className="px-3 mt-4 flex-1">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                        >
                            <item.icon className="w-5 h-5" />
                            <span>{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-[#2d3748]">
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
