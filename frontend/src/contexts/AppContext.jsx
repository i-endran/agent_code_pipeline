import { createContext, useContext, useState, useCallback } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
    const [notifications, setNotifications] = useState([]);
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    const showNotification = useCallback((message, type = 'info', duration = 5000) => {
        const id = Date.now();
        const notification = { id, message, type, duration };

        setNotifications(prev => [...prev, notification]);

        if (duration > 0) {
            setTimeout(() => {
                clearNotification(id);
            }, duration);
        }

        return id;
    }, []);

    const clearNotification = useCallback((id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    }, []);

    const clearAllNotifications = useCallback(() => {
        setNotifications([]);
    }, []);

    const value = {
        notifications,
        showNotification,
        clearNotification,
        clearAllNotifications,
        sidebarCollapsed,
        setSidebarCollapsed
    };

    return (
        <AppContext.Provider value={value}>
            {children}
        </AppContext.Provider>
    );
}

export function useApp() {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within AppProvider');
    }
    return context;
}
