import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { useWebSocket } from '../hooks/useWebSocket';
import { useApp } from './AppContext';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const PipelineContext = createContext(null);

export function PipelineProvider({ children }) {
    const [pipelines, setPipelines] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [approvals, setApprovals] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const { showNotification } = useApp();

    // WebSocket for live updates
    const { lastMessage, connected } = useWebSocket('/ws/status/global', {
        onMessage: (data) => {
            if (data.type === 'task_update') {
                setTasks(prev => prev.map(t =>
                    t.id === data.task_id ? { ...t, ...data } : t
                ));
            }

            if (data.type === 'approval_created') {
                setApprovals(prev => [data.approval, ...prev]);
                showNotification(
                    `New approval required: ${data.approval?.checkpoint || 'Unknown'}`,
                    'warning',
                    8000
                );
            }

            if (data.type === 'approval_resolved') {
                setApprovals(prev => prev.filter(a => a.id !== data.approval_id));
                showNotification(
                    `Approval ${data.action}: ${data.checkpoint || ''}`,
                    data.action === 'approved' ? 'success' : 'error',
                    5000
                );
            }

            if (data.status === 'completed') {
                showNotification(`Task completed: ${data.task_id}`, 'success');
            }

            if (data.status === 'failed') {
                showNotification(`Task failed: ${data.message || data.task_id}`, 'error', 0);
            }
        }
    });

    const fetchPipelines = useCallback(async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_BASE}/v1/pipelines`);
            setPipelines(response.data);
            setError(null);
        } catch (err) {
            setError(err.message);
            console.error('Failed to fetch pipelines:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchTasks = useCallback(async () => {
        try {
            const response = await axios.get(`${API_BASE}/tasks`);
            setTasks(response.data);
        } catch (err) {
            console.error('Failed to fetch tasks:', err);
        }
    }, []);

    const fetchApprovals = useCallback(async () => {
        try {
            const response = await axios.get(`${API_BASE}/approvals/pending`);
            setApprovals(response.data);
        } catch (err) {
            console.error('Failed to fetch approvals:', err);
        }
    }, []);

    const refreshAll = useCallback(async () => {
        await Promise.all([
            fetchPipelines(),
            fetchTasks(),
            fetchApprovals()
        ]);
    }, [fetchPipelines, fetchTasks, fetchApprovals]);

    // Initial fetch
    useEffect(() => {
        refreshAll();
    }, [refreshAll]);

    const value = {
        pipelines,
        tasks,
        approvals,
        loading,
        error,
        connected,
        lastMessage,
        fetchPipelines,
        fetchTasks,
        fetchApprovals,
        refreshAll,
        setPipelines,
        setTasks,
        setApprovals
    };

    return (
        <PipelineContext.Provider value={value}>
            {children}
        </PipelineContext.Provider>
    );
}

export function usePipelineContext() {
    const context = useContext(PipelineContext);
    if (!context) {
        throw new Error('usePipelineContext must be used within PipelineProvider');
    }
    return context;
}
