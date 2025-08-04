/**
 * Enhanced Execution Storage Hook
 * Provides persistent storage and management for workflow execution data
 */

import { useState, useEffect, useCallback } from 'react';
import { ExecutionStatus, ExecutionLog, ExecutionEvent } from '../services/enhancedWorkflowEditorApi';

export interface StoredExecutionData {
  instanceId: string;
  executionStatus: ExecutionStatus | null;
  executionLogs: ExecutionLog[];
  executionEvents: ExecutionEvent[];
  lastUpdated: string;
  createdAt: string;
  isCompleted: boolean;
  workflowName?: string;
}

interface UseExecutionStorageOptions {
  autoSave?: boolean;
  retentionDays?: number;
  maxStoredInstances?: number;
}

interface UseExecutionStorageReturn {
  // Current execution data
  executionStatus: ExecutionStatus | null;
  executionLogs: ExecutionLog[];
  executionEvents: ExecutionEvent[];
  
  // Storage operations
  saveExecution: (
    instanceId: string,
    status: ExecutionStatus | null,
    logs: ExecutionLog[],
    events: ExecutionEvent[],
    workflowName?: string
  ) => boolean;
  loadExecution: (instanceId: string) => StoredExecutionData | null;
  removeExecution: (instanceId: string) => boolean;
  
  // Bulk operations
  getAllExecutions: () => StoredExecutionData[];
  getRecentExecutions: (limit?: number) => StoredExecutionData[];
  clearAllExecutions: () => boolean;
  
  // Import/Export
  exportExecution: (instanceId: string) => string | null;
  exportAllExecutions: () => string;
  importExecution: (jsonData: string) => boolean;
  
  // Utilities
  getStorageStats: () => {
    totalInstances: number;
    totalSize: number;
    oldestEntry: string | null;
    newestEntry: string | null;
  };
  
  // State
  isLoading: boolean;
  error: string | null;
}

export const useExecutionStorage = (
  instanceId?: string,
  options: UseExecutionStorageOptions = {}
): UseExecutionStorageReturn => {
  const {
    autoSave = true,
    retentionDays = 7,
    maxStoredInstances = 50
  } = options;

  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus | null>(null);
  const [executionLogs, setExecutionLogs] = useState<ExecutionLog[]>([]);
  const [executionEvents, setExecutionEvents] = useState<ExecutionEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Storage constants
  const STORAGE_PREFIX = 'workflow_execution_';
  const INSTANCES_LIST_KEY = 'workflow_execution_instances';

  const getStorageKey = useCallback((id: string): string => {
    return `${STORAGE_PREFIX}${id}`;
  }, []);

  const getStoredInstances = useCallback((): string[] => {
    try {
      const stored = localStorage.getItem(INSTANCES_LIST_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.warn('Failed to load stored instances list:', error);
      return [];
    }
  }, []);

  const updateStoredInstances = useCallback((instances: string[]): void => {
    try {
      localStorage.setItem(INSTANCES_LIST_KEY, JSON.stringify(instances));
    } catch (error) {
      console.warn('Failed to update stored instances list:', error);
    }
  }, []);

  const isDataExpired = useCallback((createdAt: string): boolean => {
    const created = new Date(createdAt);
    const now = new Date();
    const diffDays = (now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays > retentionDays;
  }, [retentionDays]);

  const cleanupOldData = useCallback((): void => {
    try {
      const instances = getStoredInstances();
      const validInstances: string[] = [];

      instances.forEach(id => {
        try {
          const stored = localStorage.getItem(getStorageKey(id));
          if (stored) {
            const data: StoredExecutionData = JSON.parse(stored);
            if (!isDataExpired(data.createdAt)) {
              validInstances.push(id);
            } else {
              localStorage.removeItem(getStorageKey(id));
            }
          }
        } catch (error) {
          localStorage.removeItem(getStorageKey(id));
        }
      });

      updateStoredInstances(validInstances);
      console.log(`🧹 Cleanup complete. Removed ${instances.length - validInstances.length} expired entries`);
    } catch (error) {
      console.warn('Failed to cleanup old data:', error);
    }
  }, [getStoredInstances, getStorageKey, isDataExpired, updateStoredInstances]);

  // Save execution data
  const saveExecution = useCallback((
    id: string,
    status: ExecutionStatus | null,
    logs: ExecutionLog[] = [],
    events: ExecutionEvent[] = [],
    workflowName?: string
  ): boolean => {
    try {
      setError(null);
      
      // Get existing data to preserve creation time
      const existing = loadExecution(id);
      
      const dataToSave: StoredExecutionData = {
        instanceId: id,
        executionStatus: status,
        executionLogs: logs,
        executionEvents: events,
        lastUpdated: new Date().toISOString(),
        createdAt: existing?.createdAt || new Date().toISOString(),
        isCompleted: status?.status === 'completed' || status?.status === 'failed',
        workflowName
      };

      // Save the execution data
      localStorage.setItem(getStorageKey(id), JSON.stringify(dataToSave));

      // Update instances list
      const instances = getStoredInstances();
      if (!instances.includes(id)) {
        instances.push(id);
        
        // Limit the number of stored instances
        if (instances.length > maxStoredInstances) {
          const toRemove = instances.splice(0, instances.length - maxStoredInstances);
          toRemove.forEach(removeId => {
            localStorage.removeItem(getStorageKey(removeId));
          });
        }
        
        updateStoredInstances(instances);
      }

      console.log('💾 Saved execution data for instance:', id);
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to save execution data: ${errorMessage}`);
      console.error('Failed to save execution data:', err);
      return false;
    }
  }, [getStorageKey, getStoredInstances, maxStoredInstances, updateStoredInstances]);

  // Load execution data
  const loadExecution = useCallback((id: string): StoredExecutionData | null => {
    try {
      const stored = localStorage.getItem(getStorageKey(id));
      if (!stored) return null;

      const data: StoredExecutionData = JSON.parse(stored);
      
      // Validate data structure
      if (!data.instanceId || !Array.isArray(data.executionLogs) || !Array.isArray(data.executionEvents)) {
        console.warn('Invalid data structure, removing corrupted entry:', id);
        localStorage.removeItem(getStorageKey(id));
        return null;
      }
      
      // Check if data is within retention period
      if (isDataExpired(data.createdAt)) {
        localStorage.removeItem(getStorageKey(id));
        return null;
      }

      return data;
    } catch (err) {
      console.warn('Failed to load execution data, removing corrupted entry:', id, err);
      // Remove corrupted data
      try {
        localStorage.removeItem(getStorageKey(id));
      } catch (removeErr) {
        console.error('Failed to remove corrupted data:', removeErr);
      }
      return null;
    }
  }, [getStorageKey, isDataExpired]);

  // Remove execution data
  const removeExecution = useCallback((id: string): boolean => {
    try {
      localStorage.removeItem(getStorageKey(id));
      
      // Update instances list
      const instances = getStoredInstances();
      const updatedInstances = instances.filter(instanceId => instanceId !== id);
      updateStoredInstances(updatedInstances);
      
      console.log('🗑️ Removed execution data for instance:', id);
      return true;
    } catch (err) {
      console.error('Failed to remove execution data:', err);
      return false;
    }
  }, [getStorageKey, getStoredInstances, updateStoredInstances]);

  // Get all stored executions
  const getAllExecutions = useCallback((): StoredExecutionData[] => {
    const instances = getStoredInstances();
    const executions: StoredExecutionData[] = [];

    instances.forEach(id => {
      const data = loadExecution(id);
      if (data) {
        executions.push(data);
      }
    });

    // Sort by last updated (newest first)
    return executions.sort((a, b) => 
      new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
    );
  }, [getStoredInstances, loadExecution]);

  // Get recent executions
  const getRecentExecutions = useCallback((limit: number = 10): StoredExecutionData[] => {
    return getAllExecutions().slice(0, limit);
  }, [getAllExecutions]);

  // Clear all stored execution data
  const clearAllExecutions = useCallback((): boolean => {
    try {
      const instances = getStoredInstances();
      instances.forEach(id => {
        localStorage.removeItem(getStorageKey(id));
      });
      
      localStorage.removeItem(INSTANCES_LIST_KEY);
      console.log('🧹 Cleared all execution data');
      return true;
    } catch (err) {
      console.error('Failed to clear all data:', err);
      return false;
    }
  }, [getStoredInstances, getStorageKey]);

  // Export execution data
  const exportExecution = useCallback((id: string): string | null => {
    const data = loadExecution(id);
    if (!data) return null;
    return JSON.stringify(data, null, 2);
  }, [loadExecution]);

  // Export all stored data
  const exportAllExecutions = useCallback((): string => {
    const allData = getAllExecutions();
    return JSON.stringify(allData, null, 2);
  }, [getAllExecutions]);

  // Import execution data
  const importExecution = useCallback((jsonData: string): boolean => {
    try {
      const data: StoredExecutionData = JSON.parse(jsonData);
      
      if (!data.instanceId || !data.executionStatus) {
        throw new Error('Invalid execution data format');
      }

      return saveExecution(
        data.instanceId,
        data.executionStatus,
        data.executionLogs,
        data.executionEvents,
        data.workflowName
      );
    } catch (err) {
      console.error('Failed to import execution data:', err);
      return false;
    }
  }, [saveExecution]);

  // Get storage statistics
  const getStorageStats = useCallback(() => {
    const instances = getStoredInstances();
    let totalSize = 0;
    let oldestDate: Date | null = null;
    let newestDate: Date | null = null;

    instances.forEach(id => {
      const key = getStorageKey(id);
      const data = localStorage.getItem(key);
      if (data) {
        totalSize += data.length;
        
        try {
          const parsed: StoredExecutionData = JSON.parse(data);
          const createdAt = new Date(parsed.createdAt);
          
          if (!oldestDate || createdAt < oldestDate) {
            oldestDate = createdAt;
          }
          if (!newestDate || createdAt > newestDate) {
            newestDate = createdAt;
          }
        } catch (error) {
          // Ignore parsing errors
        }
      }
    });

    return {
      totalInstances: instances.length,
      totalSize,
      oldestEntry: oldestDate ? (oldestDate as Date).toISOString() : null,
      newestEntry: newestDate ? (newestDate as Date).toISOString() : null
    };
  }, [getStoredInstances, getStorageKey]);

  // Auto-load data when instanceId changes
  useEffect(() => {
    if (instanceId) {
      setIsLoading(true);
      setError(null);
      
      const savedData = loadExecution(instanceId);
      
      if (savedData) {
        setExecutionStatus(savedData.executionStatus);
        setExecutionLogs(savedData.executionLogs);
        setExecutionEvents(savedData.executionEvents);
        console.log('📂 Loaded saved execution data for:', instanceId, {
          status: !!savedData.executionStatus,
          logs: savedData.executionLogs.length,
          events: savedData.executionEvents.length
        });
      } else {
        // Only reset to empty if we don't already have data for a different instance
        // This prevents losing data during transitions
        console.log('📭 No saved data found for instance:', instanceId);
        setExecutionStatus(null);
        setExecutionLogs([]);
        setExecutionEvents([]);
      }
      
      setIsLoading(false);
    } else {
      // No instanceId provided - keep current data but don't auto-save
      console.log('📭 No instanceId provided to useExecutionStorage');
    }
  }, [instanceId, loadExecution]);

  // Auto-save when data changes
  useEffect(() => {
    if (autoSave && instanceId && (executionStatus || executionLogs.length > 0 || executionEvents.length > 0)) {
      saveExecution(instanceId, executionStatus, executionLogs, executionEvents);
    }
  }, [autoSave, instanceId, executionStatus, executionLogs, executionEvents, saveExecution]);

  // Cleanup old data on mount
  useEffect(() => {
    cleanupOldData();
  }, [cleanupOldData]);

  return {
    // Current execution data
    executionStatus,
    executionLogs,
    executionEvents,
    
    // Storage operations
    saveExecution,
    loadExecution,
    removeExecution,
    
    // Bulk operations
    getAllExecutions,
    getRecentExecutions,
    clearAllExecutions,
    
    // Import/Export
    exportExecution,
    exportAllExecutions,
    importExecution,
    
    // Utilities
    getStorageStats,
    
    // State
    isLoading,
    error
  };
};
