/**
 * Enhanced Execution Storage Service
 * Provides persistent storage for workflow execution data
 */

import { ExecutionStatus, ExecutionLog, ExecutionEvent } from './enhancedWorkflowEditorApi';

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

export interface ExecutionStorageOptions {
  maxStoredInstances?: number;
  retentionDays?: number;
  autoCleanup?: boolean;
}

class ExecutionStorageService {
  private static instance: ExecutionStorageService;
  private readonly STORAGE_PREFIX = 'workflow_execution_';
  private readonly INSTANCES_LIST_KEY = 'workflow_execution_instances';
  private readonly options: Required<ExecutionStorageOptions>;

  private constructor(options: ExecutionStorageOptions = {}) {
    this.options = {
      maxStoredInstances: options.maxStoredInstances ?? 50,
      retentionDays: options.retentionDays ?? 7,
      autoCleanup: options.autoCleanup ?? true
    };

    if (this.options.autoCleanup) {
      this.cleanupOldData();
    }
  }

  public static getInstance(options?: ExecutionStorageOptions): ExecutionStorageService {
    if (!ExecutionStorageService.instance) {
      ExecutionStorageService.instance = new ExecutionStorageService(options);
    }
    return ExecutionStorageService.instance;
  }

  private getStorageKey(instanceId: string): string {
    return `${this.STORAGE_PREFIX}${instanceId}`;
  }

  private getStoredInstances(): string[] {
    try {
      const stored = localStorage.getItem(this.INSTANCES_LIST_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.warn('Failed to load stored instances list:', error);
      return [];
    }
  }

  private updateStoredInstances(instances: string[]): void {
    try {
      localStorage.setItem(this.INSTANCES_LIST_KEY, JSON.stringify(instances));
    } catch (error) {
      console.warn('Failed to update stored instances list:', error);
    }
  }

  /**
   * Save execution data to localStorage
   */
  public saveExecutionData(
    instanceId: string,
    executionStatus: ExecutionStatus | null,
    executionLogs: ExecutionLog[] = [],
    executionEvents: ExecutionEvent[] = [],
    workflowName?: string
  ): boolean {
    try {
      // Get existing data to preserve creation time
      const existing = this.loadExecutionData(instanceId);
      
      const dataToSave: StoredExecutionData = {
        instanceId,
        executionStatus,
        executionLogs,
        executionEvents,
        lastUpdated: new Date().toISOString(),
        createdAt: existing?.createdAt || new Date().toISOString(),
        isCompleted: executionStatus?.status === 'completed' || executionStatus?.status === 'failed',
        workflowName
      };

      // Save the execution data
      localStorage.setItem(this.getStorageKey(instanceId), JSON.stringify(dataToSave));

      // Update instances list
      const instances = this.getStoredInstances();
      if (!instances.includes(instanceId)) {
        instances.push(instanceId);
        
        // Limit the number of stored instances
        if (instances.length > this.options.maxStoredInstances) {
          const toRemove = instances.splice(0, instances.length - this.options.maxStoredInstances);
          toRemove.forEach(id => this.removeExecutionData(id));
        }
        
        this.updateStoredInstances(instances);
      }

      console.log('💾 Saved execution data for instance:', instanceId);
      return true;
    } catch (error) {
      console.error('Failed to save execution data:', error);
      return false;
    }
  }

  /**
   * Load execution data from localStorage
   */
  public loadExecutionData(instanceId: string): StoredExecutionData | null {
    try {
      const stored = localStorage.getItem(this.getStorageKey(instanceId));
      if (!stored) return null;

      const data: StoredExecutionData = JSON.parse(stored);
      
      // Check if data is within retention period
      if (this.isDataExpired(data.createdAt)) {
        this.removeExecutionData(instanceId);
        return null;
      }

      return data;
    } catch (error) {
      console.warn('Failed to load execution data:', error);
      return null;
    }
  }

  /**
   * Remove execution data
   */
  public removeExecutionData(instanceId: string): boolean {
    try {
      localStorage.removeItem(this.getStorageKey(instanceId));
      
      // Update instances list
      const instances = this.getStoredInstances();
      const updatedInstances = instances.filter(id => id !== instanceId);
      this.updateStoredInstances(updatedInstances);
      
      console.log('🗑️ Removed execution data for instance:', instanceId);
      return true;
    } catch (error) {
      console.error('Failed to remove execution data:', error);
      return false;
    }
  }

  /**
   * Get all stored executions
   */
  public getAllStoredExecutions(): StoredExecutionData[] {
    const instances = this.getStoredInstances();
    const executions: StoredExecutionData[] = [];

    instances.forEach(instanceId => {
      const data = this.loadExecutionData(instanceId);
      if (data) {
        executions.push(data);
      }
    });

    // Sort by last updated (newest first)
    return executions.sort((a, b) => 
      new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
    );
  }

  /**
   * Get recent executions (last 10)
   */
  public getRecentExecutions(limit: number = 10): StoredExecutionData[] {
    return this.getAllStoredExecutions().slice(0, limit);
  }

  /**
   * Clear all stored execution data
   */
  public clearAllData(): boolean {
    try {
      const instances = this.getStoredInstances();
      instances.forEach(instanceId => {
        localStorage.removeItem(this.getStorageKey(instanceId));
      });
      
      localStorage.removeItem(this.INSTANCES_LIST_KEY);
      console.log('🧹 Cleared all execution data');
      return true;
    } catch (error) {
      console.error('Failed to clear all data:', error);
      return false;
    }
  }

  /**
   * Export execution data as JSON
   */
  public exportExecutionData(instanceId: string): string | null {
    const data = this.loadExecutionData(instanceId);
    if (!data) return null;

    return JSON.stringify(data, null, 2);
  }

  /**
   * Export all stored data
   */
  public exportAllData(): string {
    const allData = this.getAllStoredExecutions();
    return JSON.stringify(allData, null, 2);
  }

  /**
   * Import execution data from JSON
   */
  public importExecutionData(jsonData: string): boolean {
    try {
      const data: StoredExecutionData = JSON.parse(jsonData);
      
      if (!data.instanceId || !data.executionStatus) {
        throw new Error('Invalid execution data format');
      }

      return this.saveExecutionData(
        data.instanceId,
        data.executionStatus,
        data.executionLogs,
        data.executionEvents,
        data.workflowName
      );
    } catch (error) {
      console.error('Failed to import execution data:', error);
      return false;
    }
  }

  /**
   * Get storage statistics
   */
  public getStorageStats(): {
    totalInstances: number;
    totalSize: number;
    oldestEntry: string | null;
    newestEntry: string | null;
  } {
    const instances = this.getStoredInstances();
    let totalSize = 0;
    let oldestDate: Date | null = null;
    let newestDate: Date | null = null;

    instances.forEach(instanceId => {
      const key = this.getStorageKey(instanceId);
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
  }

  private isDataExpired(createdAt: string): boolean {
    const created = new Date(createdAt);
    const now = new Date();
    const diffDays = (now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays > this.options.retentionDays;
  }

  private cleanupOldData(): void {
    try {
      const instances = this.getStoredInstances();
      const validInstances: string[] = [];

      instances.forEach(instanceId => {
        const data = this.loadExecutionData(instanceId);
        if (data && !this.isDataExpired(data.createdAt)) {
          validInstances.push(instanceId);
        } else {
          localStorage.removeItem(this.getStorageKey(instanceId));
        }
      });

      this.updateStoredInstances(validInstances);
      console.log(`🧹 Cleanup complete. Removed ${instances.length - validInstances.length} expired entries`);
    } catch (error) {
      console.warn('Failed to cleanup old data:', error);
    }
  }
}

export default ExecutionStorageService;
