/**
 * Debug utilities for localStorage inspection
 */

export const debugLocalStorage = () => {
  console.group('🔍 localStorage Debug');
  
  // Get all workflow execution keys
  const executionKeys = Object.keys(localStorage).filter(key => 
    key.startsWith('workflow_execution_')
  );
  
  console.log('📋 Total execution keys:', executionKeys.length);
  
  // Show instances list
  const instancesList = localStorage.getItem('workflow_execution_instances');
  try {
    console.log('📝 Instances list:', instancesList ? JSON.parse(instancesList) : 'None');
  } catch (error) {
    console.error('❌ Failed to parse instances list:', error);
    console.log('Raw instances list:', instancesList);
  }
  
  // Show each execution data
  executionKeys.forEach(key => {
    try {
      const rawData = localStorage.getItem(key);
      if (!rawData) {
        console.warn(`⚠️ ${key}: No data found`);
        return;
      }
      
      const data = JSON.parse(rawData);
      console.log(`📂 ${key}:`, {
        instanceId: data.instanceId,
        logsCount: data.executionLogs?.length || 0,
        eventsCount: data.executionEvents?.length || 0,
        status: data.executionStatus?.status,
        lastUpdated: data.lastUpdated,
        createdAt: data.createdAt,
        dataSize: rawData.length
      });
    } catch (error) {
      console.error(`❌ Failed to parse ${key}:`, error);
      const rawData = localStorage.getItem(key);
      console.log(`Raw data preview (first 200 chars):`, rawData?.substring(0, 200));
    }
  });
  
  console.groupEnd();
};

export const clearDebugStorage = () => {
  const executionKeys = Object.keys(localStorage).filter(key => 
    key.startsWith('workflow_execution_')
  );
  
  executionKeys.forEach(key => localStorage.removeItem(key));
  localStorage.removeItem('workflow_execution_instances');
  
  console.log('🧹 Cleared all execution storage');
};

export const cleanCorruptedStorage = () => {
  console.log('🧹 Cleaning corrupted localStorage entries...');
  
  const executionKeys = Object.keys(localStorage).filter(key => 
    key.startsWith('workflow_execution_') && key !== 'workflow_execution_instances'
  );
  
  let cleaned = 0;
  
  executionKeys.forEach(key => {
    try {
      const rawData = localStorage.getItem(key);
      if (!rawData) return;
      
      const data = JSON.parse(rawData);
      
      // Validate data structure
      if (!data.instanceId || !Array.isArray(data.executionLogs) || !Array.isArray(data.executionEvents)) {
        console.log(`🗑️ Removing corrupted entry: ${key}`);
        localStorage.removeItem(key);
        cleaned++;
      }
    } catch (error) {
      console.log(`🗑️ Removing unparseable entry: ${key}`);
      localStorage.removeItem(key);
      cleaned++;
    }
  });
  
  // Clean up instances list
  try {
    const instancesList = localStorage.getItem('workflow_execution_instances');
    if (instancesList) {
      const instances = JSON.parse(instancesList);
      const validInstances = instances.filter((id: string) => {
        const key = `workflow_execution_${id}`;
        return localStorage.getItem(key) !== null;
      });
      
      if (validInstances.length !== instances.length) {
        localStorage.setItem('workflow_execution_instances', JSON.stringify(validInstances));
        console.log(`🧹 Updated instances list: removed ${instances.length - validInstances.length} invalid references`);
      }
    }
  } catch (error) {
    console.log('🗑️ Removing corrupted instances list');
    localStorage.removeItem('workflow_execution_instances');
  }
  
  console.log(`✅ Cleaning complete. Removed ${cleaned} corrupted entries.`);
};

// Make available globally for browser console
if (typeof window !== 'undefined') {
  (window as any).debugStorage = debugLocalStorage;
  (window as any).clearStorage = clearDebugStorage;
  (window as any).cleanStorage = cleanCorruptedStorage;
}
