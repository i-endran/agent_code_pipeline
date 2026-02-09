import { useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import {
    CheckCircleIcon,
    XCircleIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon,
    XMarkIcon
} from '@heroicons/react/24/outline';

export default function Toast() {
    const { notifications, clearNotification } = useApp();

    return (
        <div className="fixed top-4 right-4 z-50 space-y-2">
            {notifications.map((notification) => (
                <ToastItem
                    key={notification.id}
                    notification={notification}
                    onClose={() => clearNotification(notification.id)}
                />
            ))}
        </div>
    );
}

function ToastItem({ notification, onClose }) {
    const { id, message, type, duration } = notification;

    const icons = {
        success: CheckCircleIcon,
        error: XCircleIcon,
        warning: ExclamationTriangleIcon,
        info: InformationCircleIcon
    };

    const colors = {
        success: 'bg-green-500/20 border-green-500/50 text-green-400',
        error: 'bg-red-500/20 border-red-500/50 text-red-400',
        warning: 'bg-orange-500/20 border-orange-500/50 text-orange-400',
        info: 'bg-blue-500/20 border-blue-500/50 text-blue-400'
    };

    const Icon = icons[type] || InformationCircleIcon;
    const colorClass = colors[type] || colors.info;

    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(onClose, duration);
            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    return (
        <div
            className={`flex items-start gap-3 p-4 rounded-lg border backdrop-blur-sm ${colorClass} min-w-[320px] max-w-md animate-slide-in-right shadow-lg`}
        >
            <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="flex-1 text-sm text-white">{message}</p>
            <button
                onClick={onClose}
                className="flex-shrink-0 hover:opacity-70 transition-opacity"
            >
                <XMarkIcon className="w-5 h-5" />
            </button>
        </div>
    );
}
