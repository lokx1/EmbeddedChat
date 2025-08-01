/**
 * Visual Workflow Editor - Simplified Version
 */
import { useState, useCallback, useRef } from 'react';
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
import { useTheme } from '../../contexts/ThemeContext';

// Initial empty state
const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

let id = 0;
const getId = () => `node_${id++}`;

interface WorkflowEditorProps {
  workflowId?: string;
  onBack?: () => void;
}

function WorkflowEditorInner({ onBack }: WorkflowEditorProps) {
  const { isDark } = useTheme() || { isDark: false };
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onViewportChange = useCallback((_event: MouseEvent | TouchEvent, viewport: { x: number; y: number; zoom: number }) => {
    setViewport(viewport);
  }, []);

  const handleResetView = useCallback(() => {
    if (reactFlowInstance) {
      reactFlowInstance.setViewport({ x: 0, y: 0, zoom: 1 });
    }
  }, [reactFlowInstance]);

  const handleFitView = useCallback(() => {
    if (reactFlowInstance && nodes.length > 0) {
      reactFlowInstance.fitView({ padding: 0.1, minZoom: 0.5, maxZoom: 1.5 });
    }
  }, [reactFlowInstance, nodes]);

  const handlePan = useCallback((direction: 'up' | 'down' | 'left' | 'right') => {
    if (reactFlowInstance) {
      const currentViewport = reactFlowInstance.getViewport();
      const panAmount = 100;
      
      let newX = currentViewport.x;
      let newY = currentViewport.y;
      
      switch (direction) {
        case 'up':
          newY += panAmount;
          break;
        case 'down':
          newY -= panAmount;
          break;
        case 'left':
          newX += panAmount;
          break;
        case 'right':
          newX -= panAmount;
          break;
      }
      
      reactFlowInstance.setViewport({ x: newX, y: newY, zoom: currentViewport.zoom });
    }
  }, [reactFlowInstance]);

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
            
            <h1 className={`text-xl font-bold ${isDark ? 'text-gray-100' : 'text-gray-900'}`}>
              New Workflow
            </h1>
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
            
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Save
            </button>
            
            <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
              Execute
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1">
        {/* Sidebar */}
        {sidebarOpen && <WorkflowSidebar />}

        {/* Canvas */}
        <div className="flex-1 overflow-hidden" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onMove={onViewportChange}
            nodeTypes={nodeTypes}
            className={isDark ? 'bg-gray-900' : 'bg-gray-50'}
            panOnScroll={true}
            panOnScrollSpeed={0.5}
            zoomOnScroll={true}
            zoomOnPinch={true}
            panOnDrag={true}
            selectionOnDrag={false}
            zoomOnDoubleClick={false}
            preventScrolling={false}
          >
            <Controls className={isDark ? 'bg-gray-800 text-white' : 'bg-white'} />
            <MiniMap className={isDark ? 'bg-gray-800' : 'bg-white'} />
            <Background variant={BackgroundVariant.Dots} />
            
            {/* Custom Scroll Controls */}
            <div className="absolute top-4 right-4 flex flex-col gap-2 z-10">
              <button
                onClick={handleFitView}
                className={`p-3 rounded-lg shadow-lg transition-all duration-200 hover:scale-105 ${
                  isDark ? 'bg-gray-800 text-gray-200 hover:bg-gray-700' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title="Fit view to all nodes"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4m-4 0l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              </button>
              
              <button
                onClick={handleResetView}
                className={`p-3 rounded-lg shadow-lg transition-all duration-200 hover:scale-105 ${
                  isDark ? 'bg-gray-800 text-gray-200 hover:bg-gray-700' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title="Reset view to center"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4V1m6 8h3m-6 8v3m-6-3v3m-6-8H1m11-6l6 6-6 6-6-6 6-6z" />
                </svg>
              </button>
              
              {/* Zoom Level Indicator */}
              <div className={`px-3 py-2 rounded-lg shadow-lg text-sm font-medium ${
                isDark ? 'bg-gray-800 text-gray-200' : 'bg-white text-gray-700'
              }`}>
                {Math.round(viewport.zoom * 100)}%
              </div>
            </div>

            {/* Pan Navigation Controls */}
            <div className="absolute top-4 left-4 z-10">
              <div className={`bg-opacity-90 backdrop-blur-sm rounded-xl p-2 shadow-lg ${
                isDark ? 'bg-gray-800' : 'bg-white'
              }`}>
                <div className="grid grid-cols-3 gap-1">
                  {/* Top Row */}
                  <div></div>
                  <button
                    onClick={() => handlePan('up')}
                    className={`p-2 rounded-lg transition-all duration-200 hover:scale-105 ${
                      isDark ? 'text-gray-200 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    title="Pan up"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                  </button>
                  <div></div>
                  
                  {/* Middle Row */}
                  <button
                    onClick={() => handlePan('left')}
                    className={`p-2 rounded-lg transition-all duration-200 hover:scale-105 ${
                      isDark ? 'text-gray-200 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    title="Pan left"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>
                  <div className={`p-2 rounded-lg ${
                    isDark ? 'bg-gray-700' : 'bg-gray-100'
                  }`}>
                    <div className="w-4 h-4 flex items-center justify-center">
                      <div className={`w-2 h-2 rounded-full ${
                        isDark ? 'bg-gray-400' : 'bg-gray-500'
                      }`}></div>
                    </div>
                  </div>
                  <button
                    onClick={() => handlePan('right')}
                    className={`p-2 rounded-lg transition-all duration-200 hover:scale-105 ${
                      isDark ? 'text-gray-200 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    title="Pan right"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                  
                  {/* Bottom Row */}
                  <div></div>
                  <button
                    onClick={() => handlePan('down')}
                    className={`p-2 rounded-lg transition-all duration-200 hover:scale-105 ${
                      isDark ? 'text-gray-200 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    title="Pan down"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  <div></div>
                </div>
              </div>
            </div>
            
            {/* Empty State */}
            {nodes.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h3 className={`text-xl font-bold mb-2 ${isDark ? 'text-gray-100' : 'text-gray-900'}`}>
                    Start building your workflow
                  </h3>
                  <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Drag components from the sidebar to create your workflow
                  </p>
                </div>
              </div>
            )}
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}

export function WorkflowEditor(props: WorkflowEditorProps) {
  return (
    <ReactFlowProvider>
      <WorkflowEditorInner {...props} />
    </ReactFlowProvider>
  );
}
