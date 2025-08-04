/**
 * Debug Script for Workflow Storage Issue
 * Paste this into browser console to debug why workflow data is lost after reload
 */

function debugWorkflowStorage() {
  console.clear();
  console.log('🔍 Debugging Workflow Storage Issue...\n');
  
  // 1. Check current instance tracking
  console.group('📋 Current Instance Tracking');
  const currentInstanceId = localStorage.getItem('workflow_editor_current_instance');
  console.log('Current Instance ID:', currentInstanceId || 'NOT SET');
  
  if (currentInstanceId) {
    console.log('✅ Instance ID is tracked');
  } else {
    console.warn('❌ No current instance ID - this could be the problem!');
  }
  console.groupEnd();
  
  // 2. Check execution data storage
  console.group('💾 Execution Data Storage');
  const executionKeys = Object.keys(localStorage).filter(key => 
    key.startsWith('workflow_execution_') && key !== 'workflow_execution_instances'
  );
  console.log('Total execution entries:', executionKeys.length);
  
  if (executionKeys.length === 0) {
    console.warn('❌ No execution data found in storage!');
    console.groupEnd();
    return;
  }
  
  // Check instances list
  const instancesList = localStorage.getItem('workflow_execution_instances');
  let instances = [];
  if (instancesList) {
    try {
      instances = JSON.parse(instancesList);
      console.log('Tracked instances:', instances.length);
    } catch (error) {
      console.error('❌ Corrupted instances list:', error);
    }
  } else {
    console.warn('❌ No instances list found');
  }
  
  // Check each execution entry
  executionKeys.forEach((key, index) => {
    const instanceId = key.replace('workflow_execution_', '');
    const rawData = localStorage.getItem(key);
    
    try {
      const data = JSON.parse(rawData);
      console.log(`Entry ${index + 1} (${instanceId.slice(0, 8)}...):`, {
        logs: data.executionLogs?.length || 0,
        events: data.executionEvents?.length || 0,
        status: data.executionStatus?.status || 'none',
        lastUpdated: data.lastUpdated,
        isCompleted: data.isCompleted,
        inInstancesList: instances.includes(instanceId),
        isCurrentInstance: instanceId === currentInstanceId
      });
    } catch (error) {
      console.error(`❌ Corrupted data in ${key}:`, error);
    }
  });
  console.groupEnd();
  
  // 3. Test data loading scenario
  console.group('🎭 Test Data Loading Scenario');
  
  if (!currentInstanceId) {
    console.log('Scenario: No current instance - testing auto-load...');
    
    // This is what EnhancedExecutionPanel should do
    if (instances.length > 0) {
      const mostRecentId = instances[instances.length - 1];
      const mostRecentKey = `workflow_execution_${mostRecentId}`;
      const mostRecentData = localStorage.getItem(mostRecentKey);
      
      if (mostRecentData) {
        try {
          const parsed = JSON.parse(mostRecentData);
          console.log('✅ Most recent execution found:', {
            id: mostRecentId.slice(0, 8) + '...',
            logs: parsed.executionLogs?.length || 0,
            events: parsed.executionEvents?.length || 0,
            status: parsed.executionStatus?.status
          });
          
          console.log('💡 This should be auto-loaded in the UI');
        } catch (error) {
          console.error('❌ Cannot parse most recent data:', error);
        }
      } else {
        console.warn('❌ Most recent data not found');
      }
    } else {
      console.warn('❌ No instances to auto-load');
    }
  } else {
    console.log('Scenario: Has current instance - testing direct load...');
    
    const currentKey = `workflow_execution_${currentInstanceId}`;
    const currentData = localStorage.getItem(currentKey);
    
    if (currentData) {
      try {
        const parsed = JSON.parse(currentData);
        console.log('✅ Current instance data found:', {
          id: currentInstanceId.slice(0, 8) + '...',
          logs: parsed.executionLogs?.length || 0,
          events: parsed.executionEvents?.length || 0,
          status: parsed.executionStatus?.status
        });
        
        if (parsed.executionLogs?.length > 0 || parsed.executionEvents?.length > 0) {
          console.log('✅ Data should be visible in UI');
        } else {
          console.warn('⚠️ Current instance has no logs/events - empty execution?');
        }
      } catch (error) {
        console.error('❌ Cannot parse current instance data:', error);
      }
    } else {
      console.error('❌ Current instance data not found - this is the problem!');
      console.log('💡 The instanceId is tracked but data is missing');
    }
  }
  console.groupEnd();
  
  // 4. Recommendations
  console.group('💡 Recommendations');
  
  if (!currentInstanceId && instances.length > 0) {
    console.log('ISSUE: Current instance not tracked but executions exist');
    console.log('FIX: Implement better instance tracking or auto-recovery');
  }
  
  if (currentInstanceId && !localStorage.getItem(`workflow_execution_${currentInstanceId}`)) {
    console.log('ISSUE: Current instance tracked but data missing');
    console.log('FIX: Clear current instance or recover from most recent');
  }
  
  if (executionKeys.length > instances.length) {
    console.log('ISSUE: More execution data than tracked instances');
    console.log('FIX: Clean up orphaned data or rebuild instances list');
  }
  
  const totalDataSize = executionKeys.reduce((total, key) => {
    const data = localStorage.getItem(key);
    return total + (data ? data.length : 0);
  }, 0);
  
  console.log(`Storage usage: ${Math.round(totalDataSize / 1024)} KB`);
  
  if (totalDataSize > 50000) {
    console.warn('⚠️ High storage usage - consider cleanup');
  }
  
  console.groupEnd();
}

// Test auto-recovery
function testAutoRecovery() {
  console.log('🔧 Testing auto-recovery...');
  
  const currentInstanceId = localStorage.getItem('workflow_editor_current_instance');
  const instancesList = localStorage.getItem('workflow_execution_instances');
  
  if (!currentInstanceId && instancesList) {
    try {
      const instances = JSON.parse(instancesList);
      if (instances.length > 0) {
        const mostRecent = instances[instances.length - 1];
        console.log('Setting most recent as current:', mostRecent.slice(0, 8) + '...');
        localStorage.setItem('workflow_editor_current_instance', mostRecent);
        console.log('✅ Auto-recovery complete - refresh page to test');
      }
    } catch (error) {
      console.error('❌ Auto-recovery failed:', error);
    }
  } else {
    console.log('No recovery needed or no data available');
  }
}

// Clear problematic state
function clearCurrentInstance() {
  localStorage.removeItem('workflow_editor_current_instance');
  console.log('✅ Cleared current instance - page should now auto-load most recent');
}

// Export functions
window.debugWorkflowStorage = debugWorkflowStorage;
window.testAutoRecovery = testAutoRecovery;
window.clearCurrentInstance = clearCurrentInstance;

console.log('🔧 Debug tools loaded!');
console.log('Run: debugWorkflowStorage()');
console.log('     testAutoRecovery()');
console.log('     clearCurrentInstance()');
