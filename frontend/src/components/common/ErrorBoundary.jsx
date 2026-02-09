import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({
            error,
            errorInfo
        });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-[#0f1117] flex items-center justify-center p-8">
                    <div className="card max-w-2xl w-full">
                        <div className="text-center">
                            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <h1 className="text-2xl font-bold text-white mb-2">Something went wrong</h1>
                            <p className="text-gray-400 mb-6">
                                An unexpected error occurred. Please refresh the page or contact support if the problem persists.
                            </p>

                            {this.state.error && (
                                <details className="text-left bg-[#1a1b23] p-4 rounded-lg border border-[#2d3748] mb-4">
                                    <summary className="text-sm text-gray-400 cursor-pointer hover:text-white">
                                        Error Details
                                    </summary>
                                    <pre className="text-xs text-red-400 mt-2 overflow-auto">
                                        {this.state.error.toString()}
                                        {this.state.errorInfo && this.state.errorInfo.componentStack}
                                    </pre>
                                </details>
                            )}

                            <button
                                onClick={() => window.location.reload()}
                                className="btn-primary"
                            >
                                Reload Page
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
