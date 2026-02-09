import Sidebar from './Sidebar';

export default function Layout({ children }) {
    return (
        <div className="flex min-h-screen bg-black">
            <Sidebar />
            <main className="ml-64 flex-1 p-8">
                <div className="max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
}
