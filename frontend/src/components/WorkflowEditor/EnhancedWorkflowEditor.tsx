/**
 * Enhanced Visual Workflow Editor with Save/Execute Integration
 */
import React, { useState, useCallback, useRef, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
  ReactFlowProvider,
  ReactFlowInstance,
  ConnectionMode,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { nodeTypes } from './NodeTypes';
import DynamicWorkflowSidebar from './DynamicWorkflowSidebar';
import EnhancedExecutionPanel from './EnhancedExecutionPanel';
import FloatingExecutionMonitor from './FloatingExecutionMonitor';
import DynamicNodeConfigPanel from './DynamicNodeConfigPanel';
import { useTheme } from '../../contexts/ThemeContext';
import { useWorkflowEditor, useWorkflowExecution, useWorkflowComponents } from '../../hooks/useEnhancedWorkflow';
import { useExecutionMonitor } from '../../hooks/useExecutionMonitor';

// Initial empty state
const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

let id = 0;
const getId = () => `node_${id++}`;

interface EnhancedWorkflowEditorProps {
  workflowId?: string;
  onBack?: () => void;
}

function EnhancedWorkflowEditorInner({ workflowId, onBack }: EnhancedWorkflowEditorProps) {
  const { isDark } = useTheme() || { isDark: false };
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [executionPanelOpen, setExecutionPanelOpen] = useState(false);
  const [configPanelOpen, setConfigPanelOpen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });
  const [currentInstanceId, setCurrentInstanceId] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState('New Workflow');
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [isModified, setIsModified] = useState(false);

  // Enhanced hooks
  const { components } = useWorkflowComponents();
  const {
    currentWorkflow,
    loading: editorLoading,
    error: editorError,
    saveWorkflow,
    loadWorkflow,
    convertReactFlowData,
    setCurrentWorkflow
  } = useWorkflowEditor();

  const {
    executionStatus,
    isConnected,
    loading: executionLoading,
    error: executionError,
    executeWorkflow,
    stopExecution,
  } = useWorkflowExecution(); // Removed auto-connection - no instanceId passed

  // Execution monitoring
  const executionMonitor = useExecutionMonitor();

  // Load workflow if workflowId is provided
  useEffect(() => {
    console.log('EnhancedWorkflowEditor useEffect - workflowId:', workflowId);
    if (workflowId) {
      console.log('Loading workflow with ID:', workflowId);
      loadWorkflow(workflowId);
    }
  }, [workflowId, loadWorkflow]);

  // Update editor when workflow is loaded
  useEffect(() => {
    if (currentWorkflow) {
      const workflowData = currentWorkflow.workflow_data;
      setWorkflowName(currentWorkflow.name);
      setWorkflowDescription(currentWorkflow.description || '');
      
      // Convert to React Flow format
      const reactFlowNodes: Node[] = workflowData.nodes.map(node => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: node.data
      }));

      const reactFlowEdges: Edge[] = workflowData.edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle || null,
        targetHandle: edge.targetHandle || null
      }));

      setNodes(reactFlowNodes);
      setEdges(reactFlowEdges);

      if (workflowData.viewport) {
        setViewport(workflowData.viewport);
        reactFlowInstance?.setViewport(workflowData.viewport);
      }

      setIsModified(false);
    }
  }, [currentWorkflow, setNodes, setEdges, reactFlowInstance]);

  // Track modifications
  useEffect(() => {
    if (currentWorkflow) {
      setIsModified(true);
    }
  }, [nodes, edges, workflowName, workflowDescription]);

  const onConnect = useCallback(
    (params: Edge | Connection) => {
      console.log('Connection attempt:', params);
      setEdges((eds) => addEdge(params, eds));
      setIsModified(true);
    },
    [setEdges]
  );

  const onViewportChange = useCallback((_event: MouseEvent | TouchEvent, newViewport: { x: number; y: number; zoom: number }) => {
    setViewport(newViewport);
  }, []);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'move';
    }
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!event.dataTransfer || !reactFlowInstance) {
        return;
      }

      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      // Find component metadata
      const component = components.find(c => c.type === type);
      const label = component ? component.name : `${type.charAt(0).toUpperCase() + type.slice(1)} Node`;

      const newNode: Node = {
        id: getId(),
        type,
        position,
        data: { 
          label,
          type: type,
          config: {}
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes, components]
  );

  // Handle node click to open config panel
  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    setConfigPanelOpen(true);
  }, []);

  // Handle node update from config panel
  const onUpdateNode = useCallback((nodeId: string, newData: any) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...newData } }
          : node
      )
    );
    setIsModified(true);
  }, [setNodes]);

  // Handle node delete from config panel
  const onDeleteNode = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
    setConfigPanelOpen(false);
    setSelectedNode(null);
    setIsModified(true);
  }, [setNodes, setEdges]);

  const handleSave = useCallback(() => {
    if (!workflowName.trim()) {
      alert('Please enter a workflow name');
      return Promise.reject(new Error('No workflow name'));
    }

    const workflowData = convertReactFlowData(nodes, edges, viewport);
    
    const saveRequest = {
      name: workflowName,
      description: workflowDescription,
      category: 'custom',
      workflow_data: workflowData,
      is_public: false
    };

    return saveWorkflow(saveRequest)
      .then(result => {
        if (result.success) {
          setIsModified(false);
          alert('Workflow saved successfully!');
          
          // If this is a new workflow, we could navigate to edit it
          if (result.data?.id && !workflowId) {
            setCurrentWorkflow({
              id: result.data.id,
              name: workflowName,
              description: workflowDescription,
              workflow_data: workflowData,
              status: 'draft',
              created_at: new Date().toISOString()
            });
          }
          return result;
        } else {
          alert(`Failed to save workflow: ${result.error}`);
          throw new Error(result.error || 'Save failed');
        }
      });
  }, [workflowName, workflowDescription, nodes, edges, viewport, convertReactFlowData, saveWorkflow, workflowId, setCurrentWorkflow]);

  const handleExecute = useCallback(() => {
    if (!currentWorkflow) {
      // Save first if not saved
      if (isModified) {
        handleSave()
          .then(() => {
            if (!currentWorkflow) return;
            executeWorkflowInternal();
          });
      } else {
        alert('Please save the workflow first');
        return;
      }
    } else {
      executeWorkflowInternal();
    }

    function executeWorkflowInternal() {
      // Check if workflow has nodes
      if (nodes.length === 0) {
        alert('Cannot execute empty workflow');
        return;
      }

      // Create a real instance for execution
      const workflowData = convertReactFlowData(nodes, edges, viewport);
      const instanceData = {
        name: `${workflowName} - Execution ${new Date().toLocaleTimeString()}`,
        template_id: currentWorkflow?.id,
        workflow_data: workflowData,
        input_data: {},
        created_by: 'frontend_user'
      };

      // Use the createInstance function from useWorkflowEditor hook
      fetch('http://localhost:8000/api/v1/workflow/instances', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(instanceData)
      })
      .then(createInstanceResponse => {
        if (!createInstanceResponse.ok) {
          throw new Error(`Failed to create instance: ${createInstanceResponse.status}`);
        }
        return createInstanceResponse.json();
      })
      .then(instanceResult => {
        const newInstanceId = instanceResult.instance_id;

        if (!newInstanceId) {
          throw new Error('No instance ID returned from server');
        }

        console.log('Created instance:', newInstanceId);
        setCurrentInstanceId(newInstanceId);
        
        // Integrate with execution monitor
        executionMonitor.setWorkflowInstance(newInstanceId);
        executionMonitor.showPanel(newInstanceId);
        
        setExecutionPanelOpen(true);

        // Execute the workflow with real instance ID
        return executeWorkflow(newInstanceId, {});
      })
      .then(result => {
        if (!result.success) {
          alert(`Failed to execute workflow: ${result.error}`);
        }
      })
      .catch(error => {
        console.error('Execution error:', error);
        alert(`Failed to execute workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
      });
    }
  }, [currentWorkflow, isModified, handleSave, nodes, edges, viewport, workflowName, convertReactFlowData, executeWorkflow]);

  const handleStop = useCallback(() => {
    if (currentInstanceId && executionStatus?.is_running) {
      stopExecution(currentInstanceId)
        .then(result => {
          if (!result.success) {
            alert(`Failed to stop execution: ${result.error}`);
          }
        })
        .catch(error => {
          alert(`Failed to stop execution: ${error instanceof Error ? error.message : 'Unknown error'}`);
        });
    }
  }, [currentInstanceId, executionStatus, stopExecution]);

  return (
    <div className={`h-screen flex flex-col ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <div className={`border-b px-6 py-4 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {onBack && (
              <button
                onClick={onBack}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                  isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Dashboard
              </button>
            )}
            
            <div className="flex flex-col">
              <input
                type="text"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                className={`text-xl font-bold bg-transparent border-none outline-none ${
                  isDark ? 'text-gray-100' : 'text-gray-900'
                }`}
                placeholder="Workflow Name"
              />
              <input
                type="text"
                value={workflowDescription}
                onChange={(e) => setWorkflowDescription(e.target.value)}
                className={`text-sm bg-transparent border-none outline-none ${
                  isDark ? 'text-gray-400' : 'text-gray-600'
                }`}
                placeholder="Description (optional)"
              />
            </div>
            
            {isModified && (
              <span className="text-xs text-orange-500 font-medium">• Unsaved changes</span>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className={`p-2 rounded-lg ${
                isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <button
              onClick={() => {
                const newState = !executionPanelOpen;
                setExecutionPanelOpen(newState);
                if (newState) {
                  executionMonitor.showPanel(currentInstanceId || undefined);
                } else {
                  executionMonitor.hidePanel();
                }
              }}
              className={`p-2 rounded-lg ${
                isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'
              } ${executionPanelOpen ? 'bg-blue-100 text-blue-600' : ''}`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </button>
            
            <button
              onClick={handleSave}
              disabled={editorLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {editorLoading ? 'Saving...' : 'Save'}
            </button>
            
            {executionStatus?.is_running ? (
              <button
                onClick={handleStop}
                disabled={executionLoading}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {executionLoading ? 'Stopping...' : 'Stop'}
              </button>
            ) : (
              <button
                onClick={handleExecute}
                disabled={executionLoading || nodes.length === 0}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {executionLoading ? 'Starting...' : 'Execute'}
              </button>
            )}
          </div>
        </div>
        
        {/* Status indicators */}
        <div className="flex items-center gap-4 mt-2">
          {editorError && (
            <div className="text-red-500 text-sm">Error: {editorError}</div>
          )}
          {executionError && (
            <div className="text-red-500 text-sm">Execution Error: {executionError}</div>
          )}
          {executionStatus && (
            <div className={`text-sm px-2 py-1 rounded ${
              executionStatus.status === 'running' ? 'bg-blue-100 text-blue-800' :
              executionStatus.status === 'completed' ? 'bg-green-100 text-green-800' :
              executionStatus.status === 'failed' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              Status: {executionStatus.status}
            </div>
          )}
          {isConnected && (
            <div className="text-green-500 text-sm flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              Live Updates
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        {sidebarOpen && (
          <DynamicWorkflowSidebar 
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(false)}
          />
        )}

        {/* Canvas */}
        <div className="flex-1 overflow-hidden" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onMove={onViewportChange}
            nodeTypes={nodeTypes}
            className={isDark ? 'dark' : ''}
            fitView
            snapToGrid={true}
            snapGrid={[20, 20]}
            connectionMode={ConnectionMode.Loose}
          >
            <Controls />
            <MiniMap />
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
          </ReactFlow>
        </div>

        {/* Enhanced Execution Panel */}
        <EnhancedExecutionPanel
          workflowInstanceId={currentInstanceId || undefined}
          onClose={() => {
            setExecutionPanelOpen(false);
            executionMonitor.hidePanel();
          }}
          isVisible={executionMonitor.isVisible}
        />

        {/* Config Panel */}
        {configPanelOpen && selectedNode && (
          <div className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 overflow-y-auto">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Configure Node
              </h3>
              <button
                onClick={() => {
                  setConfigPanelOpen(false);
                  setSelectedNode(null);
                }}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4">
              <DynamicNodeConfigPanel
                node={selectedNode}
                onUpdateNode={onUpdateNode}
                onDeleteNode={onDeleteNode}
              />
            </div>
          </div>
        )}
        
        {/* Floating Execution Monitor */}
        <FloatingExecutionMonitor position="bottom-right" />
      </div>
    </div>
  );
}

export default function EnhancedWorkflowEditor(props: EnhancedWorkflowEditorProps) {
  return (
    <ReactFlowProvider>
      <EnhancedWorkflowEditorInner {...props} />
    </ReactFlowProvider>
  );
}
