import Sidebar from './Sidebar';

export default function Layout({ children }) {
    return (
        <div className="flex min-h-screen" style={{ backgroundColor: '#1e2028' }}>
            <Sidebar />
            <main className="ml-64 flex-1 p-6">
                <div className="max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
}
