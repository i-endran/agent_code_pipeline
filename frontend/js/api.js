/**
 * API Service
 * Handles all communication with the backend API
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';
const WS_BASE_URL = 'ws://localhost:8000';

const API = {
    /**
     * Make a fetch request with JSON handling
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, mergedOptions);

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    // ============ Pipelines ============

    async createPipeline(data) {
        return this.request('/pipelines/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getPipelines() {
        return this.request('/pipelines/');
    },

    async getPipeline(id) {
        return this.request(`/pipelines/${id}`);
    },

    async getPipelineEstimate(id) {
        return this.request(`/pipelines/${id}/estimate`);
    },

    async deletePipeline(id) {
        return this.request(`/pipelines/${id}`, {
            method: 'DELETE',
        });
    },

    // ============ Tasks ============

    async createTask(pipelineId) {
        return this.request('/tasks/', {
            method: 'POST',
            body: JSON.stringify({ pipeline_id: pipelineId }),
        });
    },

    async getTasks(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/tasks/?${params}`);
    },

    async getRunningTasks() {
        return this.request('/tasks/running');
    },

    async getTask(id) {
        return this.request(`/tasks/${id}`);
    },

    async getTaskLogs(id) {
        return this.request(`/tasks/${id}/logs`);
    },

    async cancelTask(id) {
        return this.request(`/tasks/${id}/cancel`, {
            method: 'POST',
        });
    },

    async getTokenDashboard(days = 7) {
        return this.request(`/tasks/dashboard/tokens?days=${days}`);
    },

    // ============ Agents ============

    async getAgents() {
        return this.request('/agents/');
    },

    async getAgent(id) {
        return this.request(`/agents/${id}`);
    },

    async getAgentPrompt(id) {
        return this.request(`/agents/${id}/prompt`);
    },
};

/**
 * WebSocket Manager for real-time updates
 */
class WebSocketManager {
    constructor() {
        this.connections = new Map();
        this.listeners = new Map();
    }

    /**
     * Connect to task status WebSocket
     */
    connectToTask(taskId, onMessage) {
        const wsUrl = `${WS_BASE_URL}/ws/status/${taskId}`;
        return this._connect(`task_${taskId}`, wsUrl, onMessage);
    }

    /**
     * Connect to global status WebSocket
     */
    connectToAll(onMessage) {
        const wsUrl = `${WS_BASE_URL}/ws/all`;
        return this._connect('all', wsUrl, onMessage);
    }

    /**
     * Internal connection handler
     */
    _connect(key, url, onMessage) {
        // Close existing connection if any
        this.disconnect(key);

        const ws = new WebSocket(url);

        ws.onopen = () => {
            console.log(`WebSocket connected: ${key}`);
        };

        ws.onmessage = (event) => {
            if (event.data === 'pong') return;
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (e) {
                console.error('WebSocket message parse error:', e);
            }
        };

        ws.onerror = (error) => {
            console.error(`WebSocket error [${key}]:`, error);
        };

        ws.onclose = () => {
            console.log(`WebSocket closed: ${key}`);
            this.connections.delete(key);
        };

        // Keepalive ping
        const pingInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send('ping');
            }
        }, 25000);

        this.connections.set(key, { ws, pingInterval });

        return ws;
    }

    /**
     * Disconnect a specific WebSocket
     */
    disconnect(key) {
        const connection = this.connections.get(key);
        if (connection) {
            clearInterval(connection.pingInterval);
            connection.ws.close();
            this.connections.delete(key);
        }
    }

    /**
     * Disconnect all WebSockets
     */
    disconnectAll() {
        for (const key of this.connections.keys()) {
            this.disconnect(key);
        }
    }
}

// Export singleton instance
const wsManager = new WebSocketManager();
