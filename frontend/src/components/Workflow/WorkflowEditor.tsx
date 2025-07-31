import React, { useState, useCallback, useRef } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Node,
  Edge,
  Connection,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useTheme } from '../../contexts/ThemeContext';

import WorkflowNode from './WorkflowNode';
import WorkflowToolbar from './WorkflowToolbar';
import WorkflowSidebar from './WorkflowSidebar';
import NodePropertiesPanel from './NodePropertiesPanel';

const nodeTypes = {
  workflowNode: WorkflowNode,
};

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'workflowNode',
    position: { x: 250, y: 200 },
    data: {
      label: 'Start',
      type: 'input',
      config: {},
    },
  },
];

const initialEdges: Edge[] = [];

interface WorkflowEditorProps {
  onSave?: (nodes: Node[], edges: Edge[]) => void;
}

export const WorkflowEditor: React.FC<WorkflowEditorProps> = ({
  onSave,
}) => {
  const { isDark } = useTheme();
  
  // Modern ReactFlow-inspired color scheme
  const theme = {
    primary: isDark ? '#2a8af6' : '#3b82f6',
    secondary: isDark ? '#06b6d4' : '#0891b2', 
    accent: isDark ? '#ae53ba' : '#9333ea',
    background: isDark ? '#0f0f23' : '#ffffff',
    canvasBackground: isDark ? '#0f0f23' : '#ffffff',
    surface: isDark ? '#1a1a2e' : '#f8fafc',
    surfaceHover: isDark ? '#16213e' : '#f1f5f9',
    nodeBackground: isDark ? '#1a1a2e' : '#ffffff',
    border: isDark ? '#292a47' : '#e2e8f0',
    borderLight: isDark ? '#1e1e3b' : '#f1f5f9',
    borderColor: isDark ? '#292a47' : '#e2e8f0',
    text: isDark ? '#ffffff' : '#0f172a',
    textColor: isDark ? '#ffffff' : '#0f172a',
    textSecondary: isDark ? '#94a3b8' : '#64748b',
    textMuted: isDark ? '#64748b' : '#94a3b8',
    success: isDark ? '#22c55e' : '#16a34a',
    warning: isDark ? '#f59e0b' : '#d97706',
    error: isDark ? '#ef4444' : '#dc2626',
    controlsBackground: isDark ? 'rgba(26, 26, 46, 0.95)' : 'rgba(248, 250, 252, 0.95)',
    gridColor: isDark ? '#1e1e3b' : '#f1f5f9',
    shadowColor: isDark ? 'rgba(0, 0, 0, 0.3)' : 'rgba(0, 0, 0, 0.1)',
    shadow: isDark ? '0 4px 6px -1px rgba(0, 0, 0, 0.3)' : '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    shadowLg: isDark ? '0 10px 15px -3px rgba(0, 0, 0, 0.3)' : '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    node: {
      ai: 'linear-gradient(135deg, #ae53ba 0%, #2a8af6 100%)',
      trigger: isDark ? 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)' : 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
      action: isDark ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' : 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
      default: isDark ? 'linear-gradient(135deg, #2a8af6 0%, #1d4ed8 100%)' : 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)'
    }
  };

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [propertiesPanelOpen, setPropertiesPanelOpen] = useState(false);
  
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    setPropertiesPanelOpen(true);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
    setPropertiesPanelOpen(false);
  }, []);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.setData('application/nodedata', JSON.stringify({
      label: nodeType.charAt(0).toUpperCase() + nodeType.slice(1),
      type: nodeType,
      config: {}
    }));
    event.dataTransfer.effectAllowed = 'move';
  };

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');
      const nodeData = JSON.parse(event.dataTransfer.getData('application/nodedata'));

      if (typeof type === 'undefined' || !type || !reactFlowBounds) {
        return;
      }

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode: Node = {
        id: `${Date.now()}`,
        type: 'workflowNode',
        position,
        data: {
          ...nodeData,
          config: nodeData.defaultConfig || {},
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const updateNodeData = useCallback((nodeId: string, newData: any) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...newData } }
          : node
      )
    );
  }, [setNodes]);

  const handleSave = useCallback(() => {
    if (onSave) {
      onSave(nodes, edges);
    }
  }, [nodes, edges, onSave]);

  const executeWorkflow = useCallback(async () => {
    // TODO: Implement workflow execution
    console.log('Executing workflow...', { nodes, edges });
  }, [nodes, edges]);

  const handleLoad = useCallback(() => {
    // TODO: Implement workflow loading
    console.log('Loading workflow...');
  }, []);

  const handleClear = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);
    setPropertiesPanelOpen(false);
  }, [setNodes, setEdges]);

  const [isExecuting] = useState(false);

  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      display: 'flex', 
      background: theme.background,
      overflow: 'hidden'
    }}>
      {/* Main Editor - Full width */}
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column'
      }}>
        {/* Toolbar */}
        <WorkflowToolbar
          onSave={handleSave}
          onLoad={handleLoad}
          onClear={handleClear}
          onRun={executeWorkflow}
          isRunning={isExecuting}
          theme={theme}
        />

        {/* Workflow Canvas with floating sidebar */}
        <div style={{ 
          flex: 1, 
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div ref={reactFlowWrapper} style={{ 
            width: '100%', 
            height: '100%' 
          }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={onNodeClick}
              onPaneClick={onPaneClick}
              onInit={setReactFlowInstance}
              onDrop={onDrop}
              onDragOver={onDragOver}
              nodeTypes={nodeTypes}
              fitView
              style={{ 
                width: '100%', 
                height: '100%',
                background: theme.canvasBackground
              }}
            >
              <Controls 
                style={{ 
                  background: theme.controlsBackground, 
                  border: `1px solid ${theme.border}`,
                  borderRadius: '8px',
                  boxShadow: theme.shadow,
                  backdropFilter: 'blur(8px)'
                }} 
              />
              <MiniMap 
                style={{ 
                  background: theme.controlsBackground, 
                  border: `1px solid ${theme.border}`,
                  borderRadius: '8px',
                  boxShadow: theme.shadow,
                  backdropFilter: 'blur(8px)'
                }}
                nodeColor={theme.primary}
                maskColor={isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}
              />
              <Background 
                variant={BackgroundVariant.Dots} 
                gap={20} 
                size={1} 
                color={theme.gridColor}
                style={{
                  backgroundColor: theme.canvasBackground
                }}
              />
            </ReactFlow>
          </div>

          {/* Floating Sidebar inside ReactFlow */}
          <WorkflowSidebar 
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
            onDragStart={onDragStart}
            theme={theme}
          />

          {/* Floating Properties Panel */}
          {propertiesPanelOpen && selectedNode && (
            <div style={{
              position: 'absolute',
              top: '20px',
              right: '20px',
              width: '320px',
              maxHeight: 'calc(100vh - 120px)',
              background: theme.controlsBackground,
              borderRadius: '12px',
              border: `1px solid ${theme.borderColor}`,
              boxShadow: `0 8px 32px ${theme.shadowColor}`,
              zIndex: 1000,
              backdropFilter: 'blur(16px)',
              overflow: 'hidden'
            }}>
              <NodePropertiesPanel
                isOpen={propertiesPanelOpen}
                selectedNode={selectedNode}
                onUpdateNode={updateNodeData}
                onClose={() => setPropertiesPanelOpen(false)}
                theme={theme}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkflowEditor;
