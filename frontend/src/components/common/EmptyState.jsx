export default function EmptyState({
    icon: Icon,
    title,
    description,
    action,
    actionLabel
}) {
    return (
        <div className="card text-center py-12">
            {Icon && (
                <Icon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            )}
            <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
            {description && (
                <p className="text-gray-400 mb-6 max-w-md mx-auto">{description}</p>
            )}
            {action && actionLabel && (
                <button onClick={action} className="btn-primary">
                    {actionLabel}
                </button>
            )}
        </div>
    );
}
