/**
 * Pipeline Management
 * Handles pipeline configuration and state
 */

const AGENT_ORDER = ['scribe', 'architect', 'forge', 'herald', 'sentinel', 'phoenix'];

// Token estimates (should match backend config)
const TOKEN_ESTIMATES = {
    scribe: { tokens: 2500, cost: 0.05 },
    architect: { tokens: 4000, cost: 0.08 },
    forge: { tokens: 12000, cost: 0.20 },
    herald: { tokens: 1500, cost: 0.02 },
    sentinel: { tokens: 3000, cost: 0.06 },
    phoenix: { tokens: 1000, cost: 0.01 },
};

/**
 * Pipeline State Manager
 */
class PipelineManager {
    constructor() {
        this.agentConfigs = {};
        this.enabledAgents = new Set();

        // Initialize empty configs
        for (const agent of AGENT_ORDER) {
            this.agentConfigs[agent] = { enabled: false };
        }
    }

    /**
     * Enable or disable an agent
     */
    setAgentEnabled(agentId, enabled) {
        if (enabled) {
            // Check sequential constraint
            const agentIndex = AGENT_ORDER.indexOf(agentId);

            // All previous agents must be enabled
            for (let i = 0; i < agentIndex; i++) {
                if (!this.enabledAgents.has(AGENT_ORDER[i])) {
                    return {
                        success: false,
                        error: `Please enable ${AGENT_ORDER[i].toUpperCase()} first`
                    };
                }
            }

            this.enabledAgents.add(agentId);
            this.agentConfigs[agentId].enabled = true;
        } else {
            // Disable this and all subsequent agents
            const agentIndex = AGENT_ORDER.indexOf(agentId);

            for (let i = agentIndex; i < AGENT_ORDER.length; i++) {
                this.enabledAgents.delete(AGENT_ORDER[i]);
                this.agentConfigs[AGENT_ORDER[i]].enabled = false;
            }
        }

        return { success: true };
    }

    /**
     * Check if an agent can be enabled
     */
    canEnableAgent(agentId) {
        const agentIndex = AGENT_ORDER.indexOf(agentId);

        if (agentIndex === 0) return true;

        // Previous agent must be enabled
        return this.enabledAgents.has(AGENT_ORDER[agentIndex - 1]);
    }

    /**
     * Update agent configuration
     */
    setAgentConfig(agentId, config) {
        this.agentConfigs[agentId] = {
            ...this.agentConfigs[agentId],
            ...config,
        };
    }

    /**
     * Get agent configuration
     */
    getAgentConfig(agentId) {
        return this.agentConfigs[agentId];
    }

    /**
     * Check if agent is configured
     */
    isAgentConfigured(agentId) {
        const config = this.agentConfigs[agentId];

        // Check required fields per agent
        switch (agentId) {
            case 'scribe':
                return !!(config.requirement_text && config.requirement_text.trim());
            case 'architect':
                return true; // No required fields
            case 'forge':
                return !!(config.repo_path && config.target_branch);
            case 'herald':
                return !!(config.repo_url);
            case 'sentinel':
                return true; // No required fields
            case 'phoenix':
                return !!(config.release_branch);
            default:
                return false;
        }
    }

    /**
     * Get list of enabled agents
     */
    getEnabledAgents() {
        return AGENT_ORDER.filter(a => this.enabledAgents.has(a));
    }

    /**
     * Calculate token estimates for enabled agents
     */
    calculateEstimate() {
        const enabledList = this.getEnabledAgents();
        const estimates = [];
        let totalTokens = 0;
        let totalCost = 0;

        for (const agent of enabledList) {
            const est = TOKEN_ESTIMATES[agent];
            estimates.push({
                agent,
                tokens: est.tokens,
                cost: est.cost,
            });
            totalTokens += est.tokens;
            totalCost += est.cost;
        }

        return {
            agents: estimates,
            totalTokens,
            totalCost: totalCost.toFixed(2),
        };
    }

    /**
     * Check if pipeline is ready to submit
     */
    isReadyToSubmit() {
        const enabled = this.getEnabledAgents();

        if (enabled.length === 0) return false;

        // All enabled agents must be configured
        for (const agent of enabled) {
            if (!this.isAgentConfigured(agent)) {
                return false;
            }
        }

        return true;
    }

    /**
     * Build pipeline payload for API
     */
    buildPayload(name, description) {
        return {
            name,
            description,
            agent_configs: {
                scribe: this._buildScribeConfig(),
                architect: this._buildArchitectConfig(),
                forge: this._buildForgeConfig(),
                herald: this._buildHeraldConfig(),
                sentinel: this._buildSentinelConfig(),
                phoenix: this._buildPhoenixConfig(),
            },
        };
    }

    _buildScribeConfig() {
        const config = this.agentConfigs.scribe;
        return {
            enabled: this.enabledAgents.has('scribe'),
            model: config.model || '',
            requirement_text: config.requirement_text || '',
            project_context: config.project_context || '',
            output_format: config.output_format || 'markdown',
        };
    }

    _buildArchitectConfig() {
        const config = this.agentConfigs.architect;
        return {
            enabled: this.enabledAgents.has('architect'),
            model: config.model || '',
            tech_stack: (config.tech_stack || '').split(',').map(s => s.trim()).filter(Boolean),
            architecture_notes: config.architecture_notes || '',
            granularity: parseInt(config.granularity) || 3,
        };
    }

    _buildForgeConfig() {
        const config = this.agentConfigs.forge;
        return {
            enabled: this.enabledAgents.has('forge'),
            model: config.model || '',
            repo_path: config.repo_path || '',
            target_branch: config.target_branch || '',
            test_command: config.test_command || 'npm test',
            lint_command: config.lint_command || 'npm run lint',
        };
    }

    _buildHeraldConfig() {
        const config = this.agentConfigs.herald;
        return {
            enabled: this.enabledAgents.has('herald'),
            model: config.model || '',
            git_provider: config.git_provider || 'github',
            repo_url: config.repo_url || '',
            mr_title_template: config.mr_title_template || '[AUTO] {feature_name}',
            reviewer_webhook_url: config.reviewer_webhook_url || '',
            labels: (config.labels || '').split(',').map(s => s.trim()).filter(Boolean),
        };
    }

    _buildSentinelConfig() {
        const config = this.agentConfigs.sentinel;
        return {
            enabled: this.enabledAgents.has('sentinel'),
            model: config.model || '',
            review_criteria: config.review_criteria || '',
            auto_approve_threshold: parseInt(config.auto_approve_threshold) || 85,
            max_fix_iterations: parseInt(config.max_fix_iterations) || 3,
            target_branch: config.target_branch || 'develop',
        };
    }

    _buildPhoenixConfig() {
        const config = this.agentConfigs.phoenix;
        return {
            enabled: this.enabledAgents.has('phoenix'),
            model: config.model || '',
            release_branch: config.release_branch || 'main',
            chat_webhook_url: config.chat_webhook_url || '',
            chat_platform: config.chat_platform || 'slack',
            changelog_enabled: config.changelog_enabled !== false,
            notification_template: config.notification_template || '',
            merge_strategy: config.merge_strategy || 'squash',
        };
    }

    /**
     * Reset all configurations
     */
    reset() {
        this.enabledAgents.clear();
        for (const agent of AGENT_ORDER) {
            this.agentConfigs[agent] = { enabled: false };
        }
    }
}

// Export singleton instance
const pipelineManager = new PipelineManager();
