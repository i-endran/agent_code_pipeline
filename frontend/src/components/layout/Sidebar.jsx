import { Link, useLocation } from 'react-router-dom';
import {
    HomeIcon,
    LinkIcon,
    PuzzlePieceIcon,
    CpuChipIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    CheckCircleIcon
} from '@heroicons/react/24/outline';

const navItems = [
    { name: 'Pipeline', path: '/', icon: HomeIcon },
    { name: 'Approvals', path: '/approvals', icon: CheckCircleIcon, badge: 0 },
    { name: 'Models', path: '/models', icon: CpuChipIcon },
    { name: 'Connectors', path: '/connectors', icon: LinkIcon },
    { name: 'Extensions', path: '/extensions', icon: PuzzlePieceIcon },
];

export default function Sidebar({ isCollapsed, setIsCollapsed }) {
    const location = useLocation();

    return (
        <aside
            className={`sidebar transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'}`}
            style={{ width: isCollapsed ? '5rem' : '16rem' }}
        >
            {/* Logo & Toggle */}
            <div className="p-5 border-b border-[#2d3748] flex items-center justify-between relative overflow-hidden">
                <div className={`transition-opacity duration-300 flex flex-col ${isCollapsed ? 'opacity-0' : 'opacity-100'}`}>
                    <h1 className="text-lg font-bold text-gradient whitespace-nowrap">SDLC Pipeline</h1>
                    <p className="text-xs text-gray-500 mt-0.5 whitespace-nowrap">AI Agent Automation</p>
                </div>

                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className={`p-1.5 rounded-lg bg-[#2d3748] hover:bg-[#4a5568] transition-all absolute top-6 ${isCollapsed ? 'left-6' : 'right-4'}`}
                    title={isCollapsed ? "Expand" : "Collapse"}
                >
                    {isCollapsed ? (
                        <ChevronRightIcon className="w-5 h-5 text-gray-400" />
                    ) : (
                        <ChevronLeftIcon className="w-5 h-5 text-gray-400" />
                    )}
                </button>
            </div>

            {/* Navigation */}
            <nav className={`px-3 mt-4 flex-1 ${isCollapsed ? 'flex flex-col items-center' : ''}`}>
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`sidebar-nav-item ${isActive ? 'active' : ''} ${isCollapsed ? 'justify-center p-3' : 'justify-start'}`}
                            title={isCollapsed ? item.name : ""}
                        >
                            <item.icon className="w-5 h-5 min-w-[1.25rem]" />
                            {!isCollapsed && <span className="transition-opacity duration-300">{item.name}</span>}
                            {item.badge !== undefined && item.badge > 0 && !isCollapsed && (
                                <span className="ml-auto bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                                    {item.badge}
                                </span>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className={`p-4 border-t border-[#2d3748] transition-all duration-300 ${isCollapsed ? 'flex justify-center' : ''}`}>
                <div className="text-xs text-gray-500">
                    <div className="flex items-center gap-2 mb-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        {!isCollapsed && <span className="whitespace-nowrap">Backend Connected</span>}
                    </div>
                    {!isCollapsed && <div className="text-gray-600 whitespace-nowrap">Phase 3 - React + Tailwind</div>}
                </div>
            </div>
        </aside>
    );
}
