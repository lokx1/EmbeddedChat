/**
 * Debug Tool for localStorage Testing
 * Paste this code into browser console to debug storage issues
 */

// 1. Debug current localStorage state
function debugCurrentStorage() {
  console.group('🔍 Current Storage Debug');
  
  // Check current instance
  const currentInstance = localStorage.getItem('workflow_editor_current_instance');
  console.log('Current Instance ID:', currentInstance);
  
  // Check all execution keys
  const allKeys = Object.keys(localStorage);
  const executionKeys = allKeys.filter(key => key.startsWith('workflow_execution_'));
  console.log('Total execution entries:', executionKeys.length);
  
  // Show current instance data
  if (currentInstance) {
    const currentKey = `workflow_execution_${currentInstance}`;
    const currentData = localStorage.getItem(currentKey);
    if (currentData) {
      try {
        const parsed = JSON.parse(currentData);
        console.log('Current instance data:', {
          instanceId: parsed.instanceId,
          logsCount: parsed.executionLogs?.length || 0,
          eventsCount: parsed.executionEvents?.length || 0,
          status: parsed.executionStatus?.status,
          lastUpdated: parsed.lastUpdated
        });
      } catch (error) {
        console.error('Failed to parse current instance data:', error);
      }
    } else {
      console.warn('Current instance data not found in storage');
    }
  }
  
  // Show recent executions
  const instancesList = localStorage.getItem('workflow_execution_instances');
  if (instancesList) {
    try {
      const instances = JSON.parse(instancesList);
      console.log('Stored instances list:', instances);
      
      // Show details of each
      instances.slice(0, 3).forEach((id, index) => {
        const key = `workflow_execution_${id}`;
        const data = localStorage.getItem(key);
        if (data) {
          try {
            const parsed = JSON.parse(data);
            console.log(`Instance ${index + 1} (${id.slice(0, 8)}...):`, {
              logsCount: parsed.executionLogs?.length || 0,
              eventsCount: parsed.executionEvents?.length || 0,
              status: parsed.executionStatus?.status,
              lastUpdated: parsed.lastUpdated
            });
          } catch (error) {
            console.error(`Failed to parse instance ${id}:`, error);
          }
        }
      });
    } catch (error) {
      console.error('Failed to parse instances list:', error);
    }
  }
  
  console.groupEnd();
}

// 2. Test auto-load logic
function testAutoLoad() {
  console.group('🧪 Test Auto-Load Logic');
  
  const currentInstance = localStorage.getItem('workflow_editor_current_instance');
  console.log('Step 1 - Current instance:', currentInstance);
  
  if (currentInstance) {
    // Test loading current instance
    const currentKey = `workflow_execution_${currentInstance}`;
    const currentData = localStorage.getItem(currentKey);
    
    if (currentData) {
      try {
        const parsed = JSON.parse(currentData);
        console.log('Step 2 - Successfully loaded current instance data');
        console.log('Data counts:', {
          logs: parsed.executionLogs?.length || 0,
          events: parsed.executionEvents?.length || 0
        });
        
        // This should be what EnhancedExecutionPanel receives
        return parsed;
      } catch (error) {
        console.error('Step 2 - Failed to parse current instance:', error);
      }
    } else {
      console.warn('Step 2 - Current instance data not found');
    }
  }
  
  // Fallback: Test loading most recent
  console.log('Step 3 - Testing fallback to most recent execution');
  const instancesList = localStorage.getItem('workflow_execution_instances');
  if (instancesList) {
    try {
      const instances = JSON.parse(instancesList);
      if (instances.length > 0) {
        const mostRecentId = instances[instances.length - 1]; // Last added
        const recentKey = `workflow_execution_${mostRecentId}`;
        const recentData = localStorage.getItem(recentKey);
        
        if (recentData) {
          const parsed = JSON.parse(recentData);
          console.log('Step 4 - Most recent execution loaded:', {
            id: mostRecentId.slice(0, 8) + '...',
            logs: parsed.executionLogs?.length || 0,
            events: parsed.executionEvents?.length || 0
          });
          return parsed;
        }
      }
    } catch (error) {
      console.error('Step 3 - Failed to load recent execution:', error);
    }
  }
  
  console.warn('❌ Auto-load failed - no data found');
  console.groupEnd();
  return null;
}

// 3. Simulate component behavior
function simulateComponentBehavior() {
  console.group('🎭 Simulate Component Behavior');
  
  // Simulate props (empty on reload)
  const propExecutionStatus = null;
  const propExecutionLogs = [];
  const propExecutionEvents = [];
  const instanceId = localStorage.getItem('workflow_editor_current_instance');
  
  console.log('Props (empty on reload):', {
    propExecutionStatus: !!propExecutionStatus,
    propExecutionLogs: propExecutionLogs.length,
    propExecutionEvents: propExecutionEvents.length,
    instanceId: instanceId || 'null'
  });
  
  // Test hook logic
  let storedData = null;
  if (instanceId) {
    const key = `workflow_execution_${instanceId}`;
    const data = localStorage.getItem(key);
    if (data) {
      try {
        storedData = JSON.parse(data);
      } catch (error) {
        console.error('Failed to parse stored data:', error);
      }
    }
  }
  
  console.log('Hook stored data:', {
    storedStatus: !!storedData?.executionStatus,
    storedLogs: storedData?.executionLogs?.length || 0,
    storedEvents: storedData?.executionEvents?.length || 0
  });
  
  // Test merge logic
  const finalStatus = propExecutionStatus || storedData?.executionStatus;
  const finalLogs = propExecutionLogs.length > 0 ? propExecutionLogs : (storedData?.executionLogs || []);
  const finalEvents = propExecutionEvents.length > 0 ? propExecutionEvents : (storedData?.executionEvents || []);
  
  console.log('Final merged data:', {
    finalStatus: !!finalStatus,
    finalLogs: finalLogs.length,
    finalEvents: finalEvents.length
  });
  
  console.log('✅ Expected UI result:', {
    shouldShowLogs: finalLogs.length,
    shouldShowEvents: finalEvents.length,
    shouldShowStatus: !!finalStatus
  });
  
  console.groupEnd();
  return { finalStatus, finalLogs, finalEvents };
}

// 4. Run all tests
function runStorageTests() {
  console.clear();
  console.log('🚀 Running localStorage Debug Tests...\n');
  
  debugCurrentStorage();
  console.log('\n');
  
  const autoLoadResult = testAutoLoad();
  console.log('\n');
  
  const componentResult = simulateComponentBehavior();
  console.log('\n');
  
  // Summary
  console.group('📋 Summary');
  console.log('Auto-load test result:', !!autoLoadResult);
  console.log('Component simulation result:', {
    status: !!componentResult.finalStatus,
    logs: componentResult.finalLogs.length,
    events: componentResult.finalEvents.length
  });
  
  if (componentResult.finalLogs.length === 0 && componentResult.finalEvents.length === 0) {
    console.warn('❌ Issue detected: No data loaded after simulation');
    console.log('💡 Possible causes:');
    console.log('1. Hook not loading stored data correctly');
    console.log('2. Merge logic not working');
    console.log('3. Component not using hook data');
  } else {
    console.log('✅ Storage tests passed - data should be available');
  }
  console.groupEnd();
}

// Export for console use
window.debugCurrentStorage = debugCurrentStorage;
window.testAutoLoad = testAutoLoad;
window.simulateComponentBehavior = simulateComponentBehavior;
window.runStorageTests = runStorageTests;

console.log('🔧 Debug tools loaded! Run: runStorageTests()');
