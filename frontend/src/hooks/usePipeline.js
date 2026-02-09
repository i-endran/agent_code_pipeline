import { useApi } from './useApi';

/**
 * Custom hook for pipeline operations
 * @returns {object} Pipeline operation methods
 */
export function usePipeline() {
    const createApi = useApi('/v1/pipelines', { method: 'POST' });
    const startApi = useApi('', { method: 'POST' });
    const stopApi = useApi('', { method: 'POST' });
    const deleteApi = useApi('', { method: 'DELETE' });

    const createPipeline = async (config) => {
        return await createApi.execute(null, { data: config });
    };

    const startPipeline = async (pipelineId) => {
        return await startApi.execute(`/v1/pipelines/${pipelineId}/start`);
    };

    const stopPipeline = async (pipelineId) => {
        return await stopApi.execute(`/v1/pipelines/${pipelineId}/stop`);
    };

    const deletePipeline = async (pipelineId) => {
        return await deleteApi.execute(`/v1/pipelines/${pipelineId}`);
    };

    return {
        createPipeline,
        startPipeline,
        stopPipeline,
        deletePipeline,
        loading: createApi.loading || startApi.loading || stopApi.loading || deleteApi.loading,
        error: createApi.error || startApi.error || stopApi.error || deleteApi.error
    };
}
