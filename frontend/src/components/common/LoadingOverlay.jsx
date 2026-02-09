import Spinner from './Spinner';

export default function LoadingOverlay({ message = 'Loading...', show = true }) {
    if (!show) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="card text-center">
                <Spinner size="xl" className="mx-auto mb-4" />
                <p className="text-white text-lg">{message}</p>
            </div>
        </div>
    );
}
