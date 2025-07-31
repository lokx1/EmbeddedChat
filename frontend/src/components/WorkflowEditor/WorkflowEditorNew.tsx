/**
 * Visual Workflow Editor - N8N Style UI
 */
import React, { useState, useCallback, useRef, DragEvent, useEffect } from 'react';
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
} from 'reactflow';
import 'reactflow/dist/style.css';

import { nodeTypes } from './NodeTypes';
import WorkflowSidebar from './WorkflowSidebar';
import NodeConfigPanel from './NodeConfigPanel';
import { useWorkflowEditor } from '../../hooks/useWorkflowEditor';
import { WorkflowEditorData } from '../../services/workflowEditorApi';

// Initial empty state
const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

let id = 0;
const getId = () => `node_${id++}`;

interface WorkflowEditorProps {
  workflowId?: string;
  onBack?: () => void;
}

interface SaveDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, description: string, category: string) => void;
  initialName?: string;
  initialDescription?: string;
  initialCategory?: string;
}

const SaveDialog: React.FC<SaveDialogProps> = ({ 
  isOpen, 
  onClose, 
  onSave, 
  initialName = '', 
  initialDescription = '', 
  initialCategory = 'custom' 
}) => {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);
  const [category, setCategory] = useState(initialCategory);

  useEffect(() => {
    setName(initialName);
    setDescription(initialDescription);
    setCategory(initialCategory);
  }, [initialName, initialDescription, initialCategory]);

  const handleSave = () => {
    if (name.trim()) {
      onSave(name.trim(), description.trim(), category);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl p-6 w-96 border border-gray-200">
        <h2 className="text-xl font-bold mb-4 text-gray-800">Save Workflow</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Workflow Name *
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter workflow name"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
            placeholder="Enter workflow description"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="custom">Custom</option>
            <option value="data-processing">Data Processing</option>
            <option value="automation">Automation</option>
            <option value="ai">AI & Machine Learning</option>
            <option value="integration">Integration</option>
          </select>
        </div>

        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!name.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

function WorkflowEditorInner({ workflowId, onBack }: WorkflowEditorProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const {
    loading,
    error,
    currentWorkflow,
    saveWorkflow,
    loadWorkflow,
    updateWorkflow,
    createNewWorkflow,
    setError
  } = useWorkflowEditor();

  // Load workflow if workflowId provided
  useEffect(() => {
    if (workflowId) {
      loadWorkflow(workflowId);
    } else {
      createNewWorkflow();
    }
  }, [workflowId, loadWorkflow, createNewWorkflow]);

  // Update nodes and edges when workflow loads
  useEffect(() => {
    if (currentWorkflow?.workflow_data) {
      setNodes(currentWorkflow.workflow_data.nodes || []);
      setEdges(currentWorkflow.workflow_data.edges || []);
      setHasUnsavedChanges(false);
    }
  }, [currentWorkflow, setNodes, setEdges]);

  // Track changes
  useEffect(() => {
    if (currentWorkflow) {
      setHasUnsavedChanges(true);
    }
  }, [nodes, edges, currentWorkflow]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type || !reactFlowInstance) {
        return;
      }

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: getId(),
        type,
        position,
        data: { 
          label: `${type.charAt(0).toUpperCase() + type.slice(1)} Node`,
          type: type
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const updateNodeData = useCallback((nodeId: string, newData: any) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...newData } } : node
      )
    );
  }, [setNodes]);

  const deleteNode = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
    setSelectedNode(null);
  }, [setNodes, setEdges]);

  const handleSave = useCallback(async (name: string, description: string, category: string) => {
    const workflowData: WorkflowEditorData = {
      nodes: nodes.map(node => ({
        id: node.id,
        type: node.type || 'default',
        position: node.position,
        data: node.data
      })),
      edges: edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle || undefined,
        targetHandle: edge.targetHandle || undefined
      })),
      viewport: reactFlowInstance?.getViewport()
    };

    try {
      if (currentWorkflow?.id) {
        const result = await updateWorkflow(currentWorkflow.id, {
          name,
          description,
          category,
          workflow_data: workflowData
        });
        if (result.success) {
          setHasUnsavedChanges(false);
          alert('Workflow updated successfully!');
        }
      } else {
        const result = await saveWorkflow({
          name,
          description,
          category,
          workflow_data: workflowData,
          is_public: false
        });
        if (result.success) {
          setHasUnsavedChanges(false);
          alert('Workflow saved successfully!');
        }
      }
    } catch (err) {
      console.error('Error saving workflow:', err);
    }
  }, [nodes, edges, reactFlowInstance, currentWorkflow, saveWorkflow, updateWorkflow]);

  const handleQuickSave = useCallback(async () => {
    if (currentWorkflow?.id && currentWorkflow.name) {
      const workflowData: WorkflowEditorData = {
        nodes: nodes.map(node => ({
          id: node.id,
          type: node.type || 'default',
          position: node.position,
          data: node.data
        })),
        edges: edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          sourceHandle: edge.sourceHandle || undefined,
          targetHandle: edge.targetHandle || undefined
        })),
        viewport: reactFlowInstance?.getViewport()
      };

      const result = await updateWorkflow(currentWorkflow.id, {
        workflow_data: workflowData
      });
      
      if (result.success) {
        setHasUnsavedChanges(false);
        alert('Workflow saved!');
      }
    } else {
      setShowSaveDialog(true);
    }
  }, [nodes, edges, reactFlowInstance, currentWorkflow, updateWorkflow]);

  const handleExecute = useCallback(async () => {
    if (!currentWorkflow?.id) {
      alert('Please save the workflow first before executing');
      return;
    }
    alert('Workflow execution not implemented yet');
  }, [currentWorkflow]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-lg text-gray-600">Loading workflow...</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Top Header - N8N Style */}
      <div className="absolute top-0 left-0 right-0 z-30 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            {onBack && (
              <button
                onClick={onBack}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Dashboard
              </button>
            )}
            
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  {currentWorkflow?.name || 'Untitled Workflow'}
                  {hasUnsavedChanges && <span className="text-orange-500 ml-2">•</span>}
                </h1>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span>{nodes.length} nodes</span>
                  <span>•</span>
                  <span>{edges.length} connections</span>
                  {currentWorkflow?.description && (
                    <>
                      <span>•</span>
                      <span>{currentWorkflow.description}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title={sidebarOpen ? 'Hide nodes panel' : 'Show nodes panel'}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            {currentWorkflow?.id && (
              <button
                onClick={handleQuickSave}
                disabled={!hasUnsavedChanges || loading}
                className="px-4 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                title="Save current changes"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                Save
              </button>
            )}
            
            <button
              onClick={() => setShowSaveDialog(true)}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              title="Save as new workflow"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Save As
            </button>
            
            <button
              onClick={handleExecute}
              disabled={!currentWorkflow?.id || nodes.length === 0}
              className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center gap-2"
              title="Execute workflow"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Execute
            </button>
          </div>
        </div>
        
        {error && (
          <div className="mx-4 mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            <div className="flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="text-red-500 hover:text-red-700"
              >
                ×
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Left Sidebar - Node Palette */}
      {sidebarOpen && (
        <div className="w-80 bg-white border-r border-gray-200 mt-16 flex flex-col shadow-sm">
          <WorkflowSidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
        </div>
      )}

      {/* Main Canvas */}
      <div className="flex-1 mt-16" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-gray-50"
          attributionPosition="bottom-left"
        >
          <Controls 
            className="bg-white border border-gray-200 rounded-lg shadow-sm"
            showInteractive={false}
          />
          <MiniMap 
            className="bg-white border border-gray-200 rounded-lg shadow-sm"
            maskColor="rgba(0, 0, 0, 0.1)"
            nodeColor="#3b82f6"
          />
          <Background 
            variant={BackgroundVariant.Dots} 
            gap={20} 
            size={1} 
            color="#e5e7eb"
          />
          
          {/* Empty State - N8N Style */}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <svg className="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Start building your workflow</h3>
                <p className="text-gray-500 mb-6 max-w-md">
                  Drag and drop nodes from the sidebar to create powerful automations. 
                  Connect them together to build your workflow logic.
                </p>
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  💡 Tip: Start with a trigger node from the sidebar
                </div>
              </div>
            </div>
          )}
        </ReactFlow>
      </div>

      {/* Right Panel - Node Configuration */}
      {selectedNode && (
        <div className="w-80 bg-white border-l border-gray-200 mt-16 flex flex-col shadow-sm">
          <NodeConfigPanel
            node={selectedNode}
            onUpdateNode={updateNodeData}
            onDeleteNode={deleteNode}
          />
        </div>
      )}

      {/* Save Dialog */}
      <SaveDialog
        isOpen={showSaveDialog}
        onClose={() => setShowSaveDialog(false)}
        onSave={handleSave}
        initialName={currentWorkflow?.name}
        initialDescription={currentWorkflow?.description}
        initialCategory={currentWorkflow?.category}
      />
    </div>
  );
}

export default function WorkflowEditor(props: WorkflowEditorProps) {
  return (
    <ReactFlowProvider>
      <WorkflowEditorInner {...props} />
    </ReactFlowProvider>
  );
}
