/**
 * Custom hooks for workflow management
 */
import { useState, useEffect, useCallback } from 'react';
import workflowApi, { 
  WorkflowTemplate, 
  WorkflowInstance, 
  WorkflowTaskLog
} from '../services/workflowApi';

// Hook for managing workflow templates
export const useWorkflowTemplates = () => {
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = useCallback(async (filters?: { category?: string; is_public?: boolean }) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.getTemplates(filters);
      if (response.success && response.data) {
        setTemplates(response.data.templates);
      } else {
        setError(response.error || 'Failed to fetch templates');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const createTemplate = useCallback(async (templateData: Partial<WorkflowTemplate>) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.createTemplate(templateData);
      if (response.success) {
        await fetchTemplates(); // Refresh list
        return response;
      } else {
        setError(response.error || 'Failed to create template');
        return response;
      }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, [fetchTemplates]);

  return {
    templates,
    loading,
    error,
    fetchTemplates,
    createTemplate,
  };
};

// Hook for managing workflow instances
export const useWorkflowInstances = () => {
  const [instances, setInstances] = useState<WorkflowInstance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInstances = useCallback(async (filters?: { 
    status?: string; 
    limit?: number; 
    offset?: number; 
  }) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.getInstances(filters);
      if (response.success && response.data) {
        setInstances(response.data.instances);
      } else {
        setError(response.error || 'Failed to fetch instances');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const createInstance = useCallback(async (instanceData: Partial<WorkflowInstance>) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.createInstance(instanceData);
      if (response.success) {
        await fetchInstances(); // Refresh list
        return response;
      } else {
        setError(response.error || 'Failed to create instance');
        return response;
      }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, [fetchInstances]);

  const executeInstance = useCallback(async (instanceId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.executeInstance(instanceId);
      if (response.success) {
        await fetchInstances(); // Refresh list to show updated status
        return response;
      } else {
        setError(response.error || 'Failed to execute instance');
        return response;
      }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, [fetchInstances]);

  return {
    instances,
    loading,
    error,
    fetchInstances,
    createInstance,
    executeInstance,
  };
};

// Hook for monitoring single workflow instance
export const useWorkflowInstance = (instanceId: string | null) => {
  const [instance, setInstance] = useState<WorkflowInstance | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInstance = useCallback(async () => {
    if (!instanceId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.getInstance(instanceId);
      if (response.success && response.data) {
        setInstance(response.data.instance);
      } else {
        setError(response.error || 'Failed to fetch instance');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [instanceId]);

  useEffect(() => {
    fetchInstance();
  }, [fetchInstance]);

  // Auto-refresh for running instances
  useEffect(() => {
    if (instance?.status === 'running') {
      const interval = setInterval(fetchInstance, 2000); // Refresh every 2 seconds
      return () => clearInterval(interval);
    }
  }, [instance?.status, fetchInstance]);

  return {
    instance,
    loading,
    error,
    refetch: fetchInstance,
  };
};

// Hook for task logs
export const useTaskLogs = () => {
  const [logs, setLogs] = useState<WorkflowTaskLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(async (filters?: {
    limit?: number;
    offset?: number;
    status?: string;
    start_date?: string;
    end_date?: string;
  }) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.getTaskLogs(filters);
      if (response.success && response.data) {
        setLogs(response.data.logs);
      } else {
        setError(response.error || 'Failed to fetch logs');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    logs,
    loading,
    error,
    fetchLogs,
  };
};

// Hook for analytics
export const useAnalytics = () => {
  const [dailyData, setDailyData] = useState<any>(null);
  const [weeklyData, setWeeklyData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDailyAnalytics = useCallback(async (date: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.getDailyAnalytics(date);
      if (response.success && response.data) {
        setDailyData(response.data);
      } else {
        setError(response.error || 'Failed to fetch daily analytics');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchWeeklyAnalytics = useCallback(async (endDate: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.getWeeklyAnalytics(endDate);
      if (response.success && response.data) {
        setWeeklyData(response.data);
      } else {
        setError(response.error || 'Failed to fetch weekly analytics');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const generateDailyReport = useCallback(async (reportDate?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.generateDailyReport(reportDate);
      if (response.success) {
        return response;
      } else {
        setError(response.error || 'Failed to generate report');
        return response;
      }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    dailyData,
    weeklyData,
    loading,
    error,
    fetchDailyAnalytics,
    fetchWeeklyAnalytics,
    generateDailyReport,
  };
};

// Hook for Google Sheets processing
export const useGoogleSheets = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processSheets = useCallback(async (data: {
    google_sheets_id: string;
    notification_settings?: any;
    output_settings?: any;
  }) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.processGoogleSheets(data);
      if (response.success) {
        return response;
      } else {
        setError(response.error || 'Failed to process sheets');
        return response;
      }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    processSheets,
  };
};

// Hook for backend health check
export const useBackendHealth = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    try {
      const response = await workflowApi.healthCheck();
      setIsHealthy(response.success);
    } catch {
      setIsHealthy(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    isHealthy,
    loading,
    checkHealth,
  };
};
