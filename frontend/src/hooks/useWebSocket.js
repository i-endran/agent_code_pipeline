import { useState, useEffect, useRef, useCallback } from 'react';

const WS_BASE = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

/**
 * Custom hook for WebSocket connections with auto-reconnect
 * @param {string} url - WebSocket URL (e.g., '/ws/status/task123')
 * @param {object} options - Configuration options
 * @returns {object} { connected, lastMessage, sendMessage, subscribe, unsubscribe }
 */
export function useWebSocket(url, options = {}) {
    const {
        autoConnect = true,
        reconnectInterval = 3000,
        maxReconnectAttempts = 5,
        onMessage = null,
        onConnect = null,
        onDisconnect = null,
        onError = null
    } = options;

    const [connected, setConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const wsRef = useRef(null);
    const reconnectAttemptsRef = useRef(0);
    const reconnectTimeoutRef = useRef(null);
    const subscribersRef = useRef(new Set());

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const wsUrl = url.startsWith('ws') ? url : `${WS_BASE}${url}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected:', wsUrl);
            setConnected(true);
            reconnectAttemptsRef.current = 0;
            onConnect?.();
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setLastMessage(data);
                onMessage?.(data);

                // Notify all subscribers
                subscribersRef.current.forEach(callback => callback(data));
            } catch (err) {
                console.error('WebSocket message parse error:', err);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            onError?.(error);
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            setConnected(false);
            onDisconnect?.();

            // Auto-reconnect
            if (reconnectAttemptsRef.current < maxReconnectAttempts) {
                reconnectAttemptsRef.current++;
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log(`Reconnecting... (attempt ${reconnectAttemptsRef.current})`);
                    connect();
                }, reconnectInterval);
            }
        };

        wsRef.current = ws;
    }, [url, reconnectInterval, maxReconnectAttempts, onMessage, onConnect, onDisconnect, onError]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setConnected(false);
    }, []);

    const sendMessage = useCallback((data) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    }, []);

    const subscribe = useCallback((callback) => {
        subscribersRef.current.add(callback);
        return () => subscribersRef.current.delete(callback);
    }, []);

    const unsubscribe = useCallback((callback) => {
        subscribersRef.current.delete(callback);
    }, []);

    useEffect(() => {
        if (autoConnect) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [autoConnect, connect, disconnect]);

    return {
        connected,
        lastMessage,
        sendMessage,
        subscribe,
        unsubscribe,
        connect,
        disconnect
    };
}
