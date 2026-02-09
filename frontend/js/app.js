/**
 * Main Application
 * Initializes event handlers and UI updates
 */

document.addEventListener('DOMContentLoaded', () => {
    initializeEventHandlers();
    updateUI();
    loadRunningTasks();

    // Connect to global WebSocket for task updates
    connectToStatusUpdates();
});

/**
 * Initialize all event handlers
 */
function initializeEventHandlers() {
    // Agent enable toggles
    document.querySelectorAll('.agent-enable').forEach(toggle => {
        toggle.addEventListener('change', handleAgentToggle);
    });

    // Agent configure buttons
    document.querySelectorAll('.agent-config-btn').forEach(btn => {
        btn.addEventListener('click', handleConfigureClick);
    });

    // Submit button
    document.getElementById('submit-pipeline').addEventListener('click', handleSubmit);

    // Refresh tasks button
    document.getElementById('refresh-tasks').addEventListener('click', loadRunningTasks);

    // Range sliders
    document.getElementById('architect-granularity').addEventListener('input', (e) => {
        document.getElementById('architect-granularity-value').textContent = e.target.value;
    });

    document.getElementById('sentinel-threshold').addEventListener('input', (e) => {
        document.getElementById('sentinel-threshold-value').textContent = e.target.value;
    });

    // Token dashboard modal
    document.getElementById('tokenDashboardModal').addEventListener('show.bs.modal', loadTokenDashboard);
}

/**
 * Handle agent toggle change
 */
function handleAgentToggle(event) {
    const agentId = event.target.dataset.agent;
    const enabled = event.target.checked;

    const result = pipelineManager.setAgentEnabled(agentId, enabled);

    if (!result.success) {
        // Revert toggle
        event.target.checked = false;
        showToast('Cannot Enable', result.error, 'warning');
        return;
    }

    updateUI();

    // If enabling, open config modal
    if (enabled) {
        openAgentModal(agentId);
    }
}

/**
 * Handle configure button click
 */
function handleConfigureClick(event) {
    const agentId = event.target.closest('button').dataset.agent;
    openAgentModal(agentId);
}

/**
 * Open agent configuration modal
 */
function openAgentModal(agentId) {
    const modal = new bootstrap.Modal(document.getElementById(`modal-${agentId}`));

    // Pre-fill with existing config
    const config = pipelineManager.getAgentConfig(agentId);
    fillModalWithConfig(agentId, config);

    modal.show();
}

/**
 * Fill modal inputs with existing configuration
 */
function fillModalWithConfig(agentId, config) {
    switch (agentId) {
        case 'scribe':
            setInputValue('scribe-prompt', config.user_prompt);
            setInputValue('scribe-requirement', config.requirement_text);
            setInputValue('scribe-context', config.project_context);
            setInputValue('scribe-format', config.output_format || 'markdown');

            // Set checkboxes for SCRIBE
            const selectedDocs = config.selected_documents || ['feature_doc'];
            document.querySelectorAll('.scribe-doc-type').forEach(cb => {
                cb.checked = selectedDocs.includes(cb.value);
            });
            break;
        case 'architect':
            setInputValue('architect-prompt', config.user_prompt);
            setInputValue('architect-techstack', config.tech_stack);
            setInputValue('architect-notes', config.architecture_notes);
            setInputValue('architect-granularity', config.granularity || 3);
            document.getElementById('architect-granularity-value').textContent = config.granularity || 3;
            break;
        case 'forge':
            setInputValue('forge-prompt', config.user_prompt);
            setInputValue('forge-repo', config.repo_path);
            setInputValue('forge-branch', config.target_branch);
            setInputValue('forge-test', config.test_command || 'npm test');
            setInputValue('forge-lint', config.lint_command || 'npm run lint');
            break;
        case 'sentinel':
            setInputValue('sentinel-prompt', config.user_prompt);
            setInputValue('sentinel-criteria', config.review_criteria);
            setInputValue('sentinel-threshold', config.auto_approve_threshold || 85);
            document.getElementById('sentinel-threshold-value').textContent = config.auto_approve_threshold || 85;
            setInputValue('sentinel-iterations', config.max_fix_iterations || 3);
            setInputValue('sentinel-target', config.target_branch || 'develop');
            break;
        case 'phoenix':
            setInputValue('phoenix-prompt', config.user_prompt);
            setInputValue('phoenix-branch', config.release_branch || 'main');
            setInputValue('phoenix-platform', config.chat_platform || 'slack');
            setInputValue('phoenix-strategy', config.merge_strategy || 'squash');
            setInputValue('phoenix-webhook', config.chat_webhook_url);
            document.getElementById('phoenix-changelog').checked = config.changelog_enabled !== false;
            setInputValue('phoenix-template', config.notification_template);
            break;
    }
}

/**
 * Helper to set input value
 */
function setInputValue(elementId, value) {
    const el = document.getElementById(elementId);
    if (el) el.value = value || '';
}

/**
 * Save agent configuration from modal
 */
function saveAgentConfig(agentId) {
    let config = {};

    switch (agentId) {
        case 'scribe':
            const selectedDocs = Array.from(document.querySelectorAll('.scribe-doc-type:checked')).map(cb => cb.value);
            config = {
                user_prompt: document.getElementById('scribe-prompt').value,
                requirement_text: document.getElementById('scribe-requirement').value,
                project_context: document.getElementById('scribe-context').value,
                output_format: document.getElementById('scribe-format').value,
                selected_documents: selectedDocs,
            };
            break;
        case 'architect':
            config = {
                user_prompt: document.getElementById('architect-prompt').value,
                tech_stack: document.getElementById('architect-techstack').value,
                architecture_notes: document.getElementById('architect-notes').value,
                granularity: document.getElementById('architect-granularity').value,
            };
            break;
        case 'forge':
            config = {
                user_prompt: document.getElementById('forge-prompt').value,
                repo_path: document.getElementById('forge-repo').value,
                target_branch: document.getElementById('forge-branch').value,
                test_command: document.getElementById('forge-test').value,
                lint_command: document.getElementById('forge-lint').value,
            };
            break;
        case 'sentinel':
            config = {
                user_prompt: document.getElementById('sentinel-prompt').value,
                review_criteria: document.getElementById('sentinel-criteria').value,
                auto_approve_threshold: document.getElementById('sentinel-threshold').value,
                max_fix_iterations: document.getElementById('sentinel-iterations').value,
                target_branch: document.getElementById('sentinel-target').value,
            };
            break;
        case 'phoenix':
            config = {
                user_prompt: document.getElementById('phoenix-prompt').value,
                release_branch: document.getElementById('phoenix-branch').value,
                chat_platform: document.getElementById('phoenix-platform').value,
                merge_strategy: document.getElementById('phoenix-strategy').value,
                chat_webhook_url: document.getElementById('phoenix-webhook').value,
                changelog_enabled: document.getElementById('phoenix-changelog').checked,
                notification_template: document.getElementById('phoenix-template').value,
            };
            break;
    }

    pipelineManager.setAgentConfig(agentId, config);

    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById(`modal-${agentId}`));
    modal.hide();

    // Update UI
    updateUI();

    showToast('Configuration Saved', `${agentId.toUpperCase()} configuration updated`, 'success');
}

/**
 * Update UI based on current state
 */
function updateUI() {
    const enabledAgents = pipelineManager.getEnabledAgents();

    // Update agent boxes
    AGENT_ORDER.forEach((agentId, index) => {
        const box = document.getElementById(`agent-${agentId}`);
        const toggle = document.getElementById(`enable-${agentId}`);
        const configBtn = box.querySelector('.agent-config-btn');

        const isEnabled = enabledAgents.includes(agentId);
        const isConfigured = pipelineManager.isAgentConfigured(agentId);
        const canEnable = pipelineManager.canEnableAgent(agentId);

        // Update toggle
        toggle.checked = isEnabled;
        toggle.disabled = !canEnable && !isEnabled;

        // Update box styling
        box.classList.toggle('enabled', isEnabled);
        box.classList.toggle('configured', isEnabled && isConfigured);

        // Update config button
        configBtn.disabled = !isEnabled;

        // Update connector
        if (index > 0) {
            const connector = box.previousElementSibling?.querySelector('.pipeline-connector');
            if (connector) {
                connector.classList.toggle('active', isEnabled);
            }
        }
    });

    // Update token estimation
    updateTokenEstimate();

    // Update submit button
    const submitBtn = document.getElementById('submit-pipeline');
    const pipelineName = document.getElementById('pipeline-name').value.trim();
    submitBtn.disabled = !pipelineManager.isReadyToSubmit() || !pipelineName;
}

/**
 * Update token estimation display
 */
function updateTokenEstimate() {
    const container = document.getElementById('token-estimate-container');
    const estimate = pipelineManager.calculateEstimate();

    if (estimate.agents.length === 0) {
        container.innerHTML = `
            <div class="text-muted text-center py-3">
                Enable agents to see token estimation
            </div>
        `;
        return;
    }

    let html = '';

    for (const item of estimate.agents) {
        html += `
            <div class="estimate-row">
                <span>${item.agent.toUpperCase()}</span>
                <span>
                    <span class="text-muted">${item.tokens.toLocaleString()} tokens</span>
                    <span class="ms-2 text-success">$${item.cost.toFixed(2)}</span>
                </span>
            </div>
        `;
    }

    html += `
        <div class="estimate-row estimate-total">
            <span>TOTAL ESTIMATED</span>
            <span>
                <span class="text-primary">${estimate.totalTokens.toLocaleString()} tokens</span>
                <span class="ms-2 text-success">$${estimate.totalCost}</span>
            </span>
        </div>
    `;

    container.innerHTML = html;
}

/**
 * Handle pipeline submission
 */
async function handleSubmit() {
    const name = document.getElementById('pipeline-name').value.trim();
    const description = document.getElementById('pipeline-description').value.trim();

    if (!name) {
        showToast('Error', 'Please enter a pipeline name', 'error');
        return;
    }

    if (!pipelineManager.isReadyToSubmit()) {
        showToast('Error', 'Please configure all enabled agents', 'error');
        return;
    }

    const submitBtn = document.getElementById('submit-pipeline');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';

    try {
        // Create pipeline
        const payload = pipelineManager.buildPayload(name, description);
        const pipeline = await API.createPipeline(payload);

        // Create and start task
        const task = await API.createTask(pipeline.id);

        showToast('Pipeline Submitted', `Task #${task.id} is now running`, 'success');

        // Reset form
        document.getElementById('pipeline-name').value = '';
        document.getElementById('pipeline-description').value = '';
        pipelineManager.reset();
        updateUI();

        // Refresh tasks list
        loadRunningTasks();

    } catch (error) {
        showToast('Submission Failed', error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-play-fill me-2"></i>Submit Pipeline';
    }
}

/**
 * Load running tasks
 */
async function loadRunningTasks() {
    const container = document.getElementById('tasks-container');

    try {
        const tasks = await API.getRunningTasks();

        document.getElementById('running-count').textContent = tasks.length;

        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="text-muted text-center py-4">
                    <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                    No running tasks
                </div>
            `;
            return;
        }

        container.innerHTML = tasks.map(task => renderTaskCard(task)).join('');

    } catch (error) {
        container.innerHTML = `
            <div class="text-danger text-center py-4">
                <i class="bi bi-exclamation-triangle fs-1 d-block mb-2"></i>
                Failed to load tasks: ${error.message}
            </div>
        `;
    }
}

/**
 * Render a task card
 */
function renderTaskCard(task) {
    const statusClass = `status-${task.status}`;
    const progress = calculateProgress(task);

    return `
        <div class="task-card fade-in" data-task-id="${task.id}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="task-name">Task #${task.id}</div>
                <span class="status-badge ${statusClass}">${task.status.replace('_', ' ')}</span>
            </div>
            <div class="task-status">
                <i class="bi bi-cpu text-primary"></i>
                <span>${task.current_stage ? task.current_stage.toUpperCase() : 'Starting...'}</span>
            </div>
            <div class="progress task-progress">
                <div class="progress-bar bg-primary" style="width: ${progress}%"></div>
            </div>
            <div class="task-meta d-flex justify-content-between mt-2">
                <span>
                    <i class="bi bi-clock me-1"></i>
                    ${formatDate(task.created_at)}
                </span>
                <span>
                    <i class="bi bi-coin me-1"></i>
                    ${task.actual_tokens || 0} / ${task.estimated_tokens} tokens
                </span>
            </div>
        </div>
    `;
}

/**
 * Calculate task progress percentage
 */
function calculateProgress(task) {
    const stages = ['scribe', 'architect', 'forge', 'herald', 'sentinel', 'phoenix'];

    if (task.status === 'completed') return 100;
    if (task.status === 'failed' || task.status === 'cancelled') return 0;

    if (!task.current_stage) return 5;

    const stageIndex = stages.indexOf(task.current_stage);
    return Math.round((stageIndex / stages.length) * 100);
}

/**
 * Format date string
 */
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Show a toast notification
 */
function showToast(title, message, type = 'info') {
    const toast = document.getElementById('toast-notification');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');

    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Update icon based on type
    const icon = toast.querySelector('.bi');
    icon.className = 'bi me-2';
    switch (type) {
        case 'success': icon.classList.add('bi-check-circle', 'text-success'); break;
        case 'error': icon.classList.add('bi-x-circle', 'text-danger'); break;
        case 'warning': icon.classList.add('bi-exclamation-triangle', 'text-warning'); break;
        default: icon.classList.add('bi-info-circle', 'text-info');
    }

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

/**
 * Connect to WebSocket for status updates
 */
function connectToStatusUpdates() {
    wsManager.connectToAll((data) => {
        if (data.type === 'status_update') {
            // Update the specific task card
            const taskCard = document.querySelector(`[data-task-id="${data.task_id}"]`);
            if (taskCard) {
                // Refresh the tasks list to get updated data
                loadRunningTasks();
            }
        }
    });
}

/**
 * Load token dashboard data
 */
async function loadTokenDashboard() {
    const container = document.getElementById('dashboard-content');

    try {
        const data = await API.getTokenDashboard(7);

        container.innerHTML = `
            <div class="row g-4 mb-4">
                <div class="col-md-4">
                    <div class="dashboard-stat">
                        <div class="stat-value">${data.total_tokens.toLocaleString()}</div>
                        <div class="stat-label">Total Tokens (7 days)</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="dashboard-stat">
                        <div class="stat-value">$${data.total_cost.toFixed(2)}</div>
                        <div class="stat-label">Total Cost</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="dashboard-stat">
                        <div class="stat-value">${data.total_tasks}</div>
                        <div class="stat-label">Completed Tasks</div>
                    </div>
                </div>
            </div>
            
            <h6 class="mb-3">Daily Usage</h6>
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Tasks</th>
                            <th>Tokens</th>
                            <th>Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(data.daily_usage || {}).map(([date, usage]) => `
                            <tr>
                                <td>${date}</td>
                                <td>${usage.tasks}</td>
                                <td>${usage.tokens.toLocaleString()}</td>
                                <td>$${usage.cost.toFixed(2)}</td>
                            </tr>
                        `).join('') || '<tr><td colspan="4" class="text-center text-muted">No data available</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;

    } catch (error) {
        container.innerHTML = `
            <div class="text-danger text-center py-4">
                <i class="bi bi-exclamation-triangle fs-1 d-block mb-2"></i>
                Failed to load dashboard: ${error.message}
            </div>
        `;
    }
}

// Add input listener for pipeline name
document.getElementById('pipeline-name').addEventListener('input', updateUI);
