/**
 * Workflow Storage Recovery Utility
 * Helper functions to diagnose and fix storage issues
 */

// Test all recovery scenarios
function testWorkflowRecovery() {
  console.clear();
  console.log('🧪 Testing Workflow Recovery Scenarios...\n');
  
  // Get current state
  const currentInstanceId = localStorage.getItem('workflow_editor_current_instance');
  const instancesList = localStorage.getItem('workflow_execution_instances');
  
  console.group('📋 Current State');
  console.log('Current Instance ID:', currentInstanceId || 'NONE');
  
  if (instancesList) {
    try {
      const instances = JSON.parse(instancesList);
      console.log('Available instances:', instances.length);
      
      instances.forEach((id, idx) => {
        const key = `workflow_execution_${id}`;
        const data = localStorage.getItem(key);
        if (data) {
          try {
            const parsed = JSON.parse(data);
            console.log(`  ${idx + 1}. ${id.slice(0, 8)}... (${parsed.executionLogs?.length || 0} logs, ${parsed.executionEvents?.length || 0} events)`);
          } catch (e) {
            console.log(`  ${idx + 1}. ${id.slice(0, 8)}... (CORRUPTED)`);
          }
        }
      });
    } catch (e) {
      console.error('Instances list corrupted:', e);
    }
  } else {
    console.log('No instances list found');
  }
  console.groupEnd();
  
  // Test scenarios
  console.group('🧪 Test Scenarios');
  
  // Scenario 1: Current instance missing
  if (!currentInstanceId && instancesList) {
    console.log('❌ Scenario 1: Current instance missing but executions exist');
    console.log('   This should trigger auto-recovery in EnhancedWorkflowEditor');
    console.log('   Expected: Most recent execution should become current');
  }
  
  // Scenario 2: Current instance exists but no data
  if (currentInstanceId) {
    const currentKey = `workflow_execution_${currentInstanceId}`;
    const currentData = localStorage.getItem(currentKey);
    
    if (!currentData) {
      console.log('❌ Scenario 2: Current instance tracked but data missing');
      console.log('   This should trigger fallback to auto-load in EnhancedExecutionPanel');
    } else {
      try {
        const parsed = JSON.parse(currentData);
        if (!parsed.executionLogs?.length && !parsed.executionEvents?.length) {
          console.log('⚠️ Scenario 3: Current instance has empty execution data');
          console.log('   This might not trigger auto-load - could be the issue');
        } else {
          console.log('✅ Scenario 4: Current instance has valid data');
          console.log('   This should work correctly');
        }
      } catch (e) {
        console.log('❌ Scenario 5: Current instance data corrupted');
      }
    }
  }
  
  console.groupEnd();
  
  return {
    currentInstanceId,
    hasInstancesList: !!instancesList,
    needsRecovery: !currentInstanceId && !!instancesList
  };
}

// Force recovery by setting most recent as current
function forceRecovery() {
  console.log('🔧 Forcing recovery...');
  
  const instancesList = localStorage.getItem('workflow_execution_instances');
  if (!instancesList) {
    console.error('❌ No execution data to recover from');
    return false;
  }
  
  try {
    const instances = JSON.parse(instancesList);
    if (instances.length === 0) {
      console.error('❌ Instances list is empty');
      return false;
    }
    
    // Find the most recent instance with data
    let targetInstance = null;
    for (let i = instances.length - 1; i >= 0; i--) {
      const id = instances[i];
      const key = `workflow_execution_${id}`;
      const data = localStorage.getItem(key);
      
      if (data) {
        try {
          const parsed = JSON.parse(data);
          if (parsed.executionLogs?.length > 0 || parsed.executionEvents?.length > 0) {
            targetInstance = id;
            break;
          }
        } catch (e) {
          console.warn('Skipping corrupted instance:', id);
        }
      }
    }
    
    if (targetInstance) {
      localStorage.setItem('workflow_editor_current_instance', targetInstance);
      console.log('✅ Recovery complete! Set current instance to:', targetInstance.slice(0, 8) + '...');
      console.log('🔄 Refresh the page to see results');
      return true;
    } else {
      console.error('❌ No valid execution data found to recover');
      return false;
    }
  } catch (e) {
    console.error('❌ Recovery failed:', e);
    return false;
  }
}

// Clean up orphaned or corrupted data
function cleanupStorage() {
  console.log('🧹 Cleaning up storage...');
  
  const instancesList = localStorage.getItem('workflow_execution_instances');
  const allKeys = Object.keys(localStorage).filter(key => key.startsWith('workflow_execution_'));
  
  let cleaned = 0;
  let recovered = [];
  
  // Check each execution key
  allKeys.forEach(key => {
    if (key === 'workflow_execution_instances') return;
    
    const data = localStorage.getItem(key);
    try {
      const parsed = JSON.parse(data);
      
      // Validate data structure
      if (!parsed.instanceId || !Array.isArray(parsed.executionLogs) || !Array.isArray(parsed.executionEvents)) {
        console.log('Removing corrupted entry:', key);
        localStorage.removeItem(key);
        cleaned++;
      } else {
        const instanceId = key.replace('workflow_execution_', '');
        recovered.push(instanceId);
      }
    } catch (e) {
      console.log('Removing corrupted entry:', key);
      localStorage.removeItem(key);
      cleaned++;
    }
  });
  
  // Rebuild instances list
  if (recovered.length > 0) {
    localStorage.setItem('workflow_execution_instances', JSON.stringify(recovered));
    console.log('✅ Rebuilt instances list with', recovered.length, 'valid entries');
  } else {
    localStorage.removeItem('workflow_execution_instances');
    console.log('🗑️ Removed empty instances list');
  }
  
  console.log(`🧹 Cleanup complete: removed ${cleaned} corrupted entries, recovered ${recovered.length} valid entries`);
  return { cleaned, recovered: recovered.length };
}

// Test current behavior
function testCurrentBehavior() {
  console.log('🎭 Simulating current component behavior...');
  
  const currentInstanceId = localStorage.getItem('workflow_editor_current_instance');
  console.log('Step 1: currentInstanceId =', currentInstanceId || 'undefined');
  
  // Simulate EnhancedExecutionPanel logic
  let autoLoadTriggered = false;
  let finalData = { logs: 0, events: 0, status: null };
  
  if (!currentInstanceId) {
    console.log('Step 2: No instanceId, checking for auto-load...');
    
    const instancesList = localStorage.getItem('workflow_execution_instances');
    if (instancesList) {
      try {
        const instances = JSON.parse(instancesList);
        if (instances.length > 0) {
          const mostRecent = instances[instances.length - 1];
          const data = localStorage.getItem(`workflow_execution_${mostRecent}`);
          if (data) {
            const parsed = JSON.parse(data);
            autoLoadTriggered = true;
            finalData = {
              logs: parsed.executionLogs?.length || 0,
              events: parsed.executionEvents?.length || 0,
              status: parsed.executionStatus?.status
            };
            console.log('Step 3: Auto-load triggered for:', mostRecent.slice(0, 8) + '...');
          }
        }
      } catch (e) {
        console.error('Auto-load failed:', e);
      }
    }
  } else {
    console.log('Step 2: Has instanceId, loading stored data...');
    const data = localStorage.getItem(`workflow_execution_${currentInstanceId}`);
    if (data) {
      try {
        const parsed = JSON.parse(data);
        finalData = {
          logs: parsed.executionLogs?.length || 0,
          events: parsed.executionEvents?.length || 0,
          status: parsed.executionStatus?.status
        };
        console.log('Step 3: Stored data loaded');
      } catch (e) {
        console.error('Failed to load stored data:', e);
      }
    } else {
      console.log('Step 3: No stored data for current instance');
    }
  }
  
  console.log('Final result:', {
    autoLoadTriggered,
    dataLoaded: finalData.logs > 0 || finalData.events > 0,
    ...finalData
  });
  
  if (finalData.logs === 0 && finalData.events === 0) {
    console.warn('❌ No data would be displayed - this matches your issue!');
  } else {
    console.log('✅ Data should be displayed correctly');
  }
  
  return finalData;
}

// Export functions
window.testWorkflowRecovery = testWorkflowRecovery;
window.forceRecovery = forceRecovery;
window.cleanupStorage = cleanupStorage;
window.testCurrentBehavior = testCurrentBehavior;

console.log('🔧 Workflow Recovery Tools loaded!');
console.log('Available functions:');
console.log('  testWorkflowRecovery() - Analyze current state');
console.log('  forceRecovery() - Force set most recent as current');
console.log('  cleanupStorage() - Clean corrupted data');
console.log('  testCurrentBehavior() - Simulate component logic');
