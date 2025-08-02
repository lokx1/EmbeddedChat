/**
 * Custom Node Types for Workflow Editor - n8n Style
 */
import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

// Base Node Component
interface BaseNodeProps extends NodeProps {
  icon: string;
  title: string;
  subtitle?: string;
  color: string;
  bgColor: string;
}

const BaseNode: React.FC<BaseNodeProps> = ({ 
  data, 
  selected, 
  icon, 
  title, 
  subtitle, 
  color, 
  bgColor 
}) => {
  console.log('BaseNode rendered:', { title, selected, data });
  return (
  <div className={`relative rounded-lg border-2 min-w-[160px] shadow-sm transition-all duration-200 ${
    selected 
      ? 'border-blue-500 shadow-lg transform scale-105' 
      : 'border-gray-300 hover:border-gray-400 hover:shadow-md'
  }`}
  style={{ backgroundColor: bgColor }}
  >
    <Handle 
      type="target" 
      position={Position.Top} 
      className="w-3 h-3 !bg-gray-400 !border-2 !border-white hover:!bg-gray-600 transition-colors"
      style={{ top: -6 }}
    />
    
    <div className="p-3">
      <div className="flex items-center justify-center mb-2">
        <div 
          className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-sm"
          style={{ backgroundColor: color }}
        >
          {icon}
        </div>
      </div>
      
      <div className="text-center">
        <div className="text-sm font-semibold text-gray-800 mb-1">{title}</div>
        {subtitle && (
          <div className="text-xs text-gray-600 leading-tight">{subtitle}</div>
        )}
        {data?.label && data.label !== title && (
          <div className="text-xs text-gray-500 mt-1 truncate">{data.label}</div>
        )}
      </div>
    </div>
    
    <Handle 
      type="source" 
      position={Position.Bottom} 
      className="w-3 h-3 !bg-gray-400 !border-2 !border-white hover:!bg-gray-600 transition-colors"
      style={{ bottom: -6 }}
    />
  </div>
  );
};

// Start Node
export const StartNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="▶️"
    title="Start"
    subtitle="Trigger point"
    color="#10b981"
    bgColor="#f0fdf4"
  />
);

// Schedule Node
export const ScheduleNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="⏰"
    title="Schedule"
    subtitle="Time-based trigger"
    color="#3b82f6"
    bgColor="#eff6ff"
  />
);

// Webhook Node
export const WebhookNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🔗"
    title="Webhook"
    subtitle="HTTP trigger"
    color="#8b5cf6"
    bgColor="#f5f3ff"
  />
);

// Google Sheets Node
export const GoogleSheetsNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="📊"
    title="Google Sheets"
    subtitle="Read spreadsheet data"
    color="#059669"
    bgColor="#ecfdf5"
  />
);

// Database Node
export const DatabaseNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🗄️"
    title="Database"
    subtitle="Database operations"
    color="#4b5563"
    bgColor="#f9fafb"
  />
);

// API Node
export const APINode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🌐"
    title="HTTP Request"
    subtitle="Make API calls"
    color="#2563eb"
    bgColor="#eff6ff"
  />
);

// AI Processing Node
export const AIProcessingNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🧠"
    title="AI Processing"
    subtitle="OpenAI, Claude, Ollama"
    color="#4f46e5"
    bgColor="#eef2ff"
  />
);

// Transform Node
export const TransformNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🔄"
    title="Transform"
    subtitle="Manipulate data"
    color="#f59e0b"
    bgColor="#fefbf3"
  />
);

// Filter Node
export const FilterNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🔍"
    title="Filter"
    subtitle="Filter data"
    color="#eab308"
    bgColor="#fefce8"
  />
);

// Condition Node
export const ConditionNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🔀"
    title="If/Condition"
    subtitle="Conditional logic"
    color="#7c3aed"
    bgColor="#f5f3ff"
  />
);

// Delay Node
export const DelayNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="⏸️"
    title="Wait/Delay"
    subtitle="Pause execution"
    color="#6b7280"
    bgColor="#f9fafb"
  />
);

// Loop Node
export const LoopNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🔁"
    title="Loop"
    subtitle="Iterate over data"
    color="#06b6d4"
    bgColor="#f0fdfa"
  />
);

// Google Drive Node
export const GoogleDriveNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="💾"
    title="Google Drive"
    subtitle="Save to Drive"
    color="#1d4ed8"
    bgColor="#eff6ff"
  />
);

// Notification Node
export const NotificationNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="📧"
    title="Send Notification"
    subtitle="Email or Slack"
    color="#dc2626"
    bgColor="#fef2f2"
  />
);

// Analytics Node
export const AnalyticsNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="📈"
    title="Analytics"
    subtitle="Track workflow data"
    color="#ec4899"
    bgColor="#fdf2f8"
  />
);

// End Node
export const EndNode = (props: NodeProps) => (
  <BaseNode
    {...props}
    icon="🏁"
    title="End"
    subtitle="Completion point"
    color="#dc2626"
    bgColor="#fef2f2"
  />
);

// Node Types mapping - Updated to match backend component types
export const nodeTypes = {
  // Backend component types (primary)
  manual_trigger: StartNode,
  webhook: WebhookNode,
  http_request: APINode,
  google_sheets: GoogleSheetsNode,
  google_sheets_write: GoogleSheetsNode,  // Add missing write component
  ai_processing: AIProcessingNode,
  data_transform: TransformNode,
  email_sender: NotificationNode,
  database_write: DatabaseNode,
  
  // Additional triggers
  schedule: ScheduleNode,
  
  // Additional data sources
  database: DatabaseNode,
  
  // Additional control flow
  filter: FilterNode,
  condition: ConditionNode,
  delay: DelayNode,
  loop: LoopNode,
  
  // Additional output actions
  drive: GoogleDriveNode,
  analytics: AnalyticsNode,
  
  // Legacy/Compatibility mappings
  httpTrigger: WebhookNode,
  googleSheets: GoogleSheetsNode,
  start: StartNode,
  end: EndNode,
  input: StartNode,
  ai: AIProcessingNode,
  output: EndNode,
  sheets: GoogleSheetsNode,
  transform: TransformNode,
  pdf: EndNode,
};
