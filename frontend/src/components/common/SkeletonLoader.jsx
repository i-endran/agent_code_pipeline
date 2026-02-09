export default function SkeletonLoader({ type = 'card', count = 1 }) {
    const skeletons = {
        card: (
            <div className="card animate-pulse">
                <div className="h-4 bg-gray-700 rounded w-3/4 mb-4"></div>
                <div className="h-3 bg-gray-700 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-700 rounded w-5/6 mb-4"></div>
                <div className="flex gap-2">
                    <div className="h-8 bg-gray-700 rounded w-20"></div>
                    <div className="h-8 bg-gray-700 rounded w-20"></div>
                </div>
            </div>
        ),
        list: (
            <div className="flex items-center gap-4 p-4 border border-[#2d3748] rounded-lg animate-pulse">
                <div className="w-10 h-10 bg-gray-700 rounded-full"></div>
                <div className="flex-1">
                    <div className="h-4 bg-gray-700 rounded w-1/2 mb-2"></div>
                    <div className="h-3 bg-gray-700 rounded w-3/4"></div>
                </div>
            </div>
        ),
        text: (
            <div className="animate-pulse space-y-2">
                <div className="h-4 bg-gray-700 rounded w-full"></div>
                <div className="h-4 bg-gray-700 rounded w-5/6"></div>
                <div className="h-4 bg-gray-700 rounded w-4/6"></div>
            </div>
        )
    };

    return (
        <div className="space-y-4">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i}>{skeletons[type]}</div>
            ))}
        </div>
    );
}
