/**
 * Demo component for testing ExecutionPanel with sample data
 */
import React, { useState } from 'react';
import ExecutionPanel from './ExecutionPanel';
import { ExecutionStatus, ExecutionLog, ExecutionEvent } from '../../services/enhancedWorkflowEditorApi';

// Sample data based on the JSON output from the image
const sampleExecutionStatus: ExecutionStatus = {
  instance_id: "8a70d57e-a460-46b3-93be-ad71ffa65360",
  status: 'completed',
  is_running: false,
  started_at: "2024-12-28T19:21:39.000Z",
  completed_at: "2024-12-28T19:23:15.000Z"
};

const sampleExecutionEvents: ExecutionEvent[] = [
  {
    event_type: 'execution_started',
    timestamp: "2024-12-28T19:21:39.000Z",
    data: {
      instance_id: "8a70d57e-a460-46b3-93be-ad71ffa65360",
      workflow_name: "Demo Workflow"
    }
  },
  {
    event_type: 'execution_completed',
    timestamp: "2024-12-28T19:23:15.000Z",
    data: {
      instance_id: "8a70d57e-a460-46b3-93be-ad71ffa65360",
      output_data: {
        node_outputs: {
          "start-1": {
            operation: "Manual Trigger",
            status: "completed",
            execution_time_ms: 150
          },
          "sheets-read-2": {
            operation: "Google Sheets Read",
            status: "completed",
            execution_time_ms: 1200,
            sheets_data: [
              ["Description", "Example Asset URL", "Desired Output Format", "Model Specification"],
              ["Design a Task Manager app logo", "https://static.wikia.nocookie.net/logopedia/images/c/cb=20240127035026", "PNG", "OpenAI"],
              ["Summer Sale banner for a fashion store", "", "", ""]
            ],
            values: [
              ["Description", "Example Asset URL", "Desired Output Format", "Model Specification"],
              ["Design a Task Manager app logo", "https://static.wikia.nocookie.net/logopedia/images/c/cb=20240127035026", "PNG", "OpenAI"],
              ["Summer Sale banner for a fashion store", "", "", ""]
            ]
          },
          "ai-processing-3": {
            operation: "AI Content Generation",
            status: "completed",
            execution_time_ms: 8500,
            values: [
              "Create a professional Task Manager app logo with modern design elements",
              "Design a vibrant Summer Sale banner for a fashion store targeting young adults"
            ],
            processed_results: [
              {
                prompt: "Create a professional Task Manager app logo with modern design elements. The logo should be clean, minimalist, and suitable for both mobile and desktop applications. Consider using task/productivity related icons like checkmarks, lists, or organizational elements. The design should convey efficiency, organization, and modern technology. Please provide detailed design specifications including color schemes, typography recommendations, and scalability considerations for different screen sizes.",
                response: "TASK MANAGER LOGO DESIGN SPECIFICATIONS\n\nConcept: Modern minimalist logo featuring a stylized checklist icon combined with clean typography\n\nDesign Elements:\n• Primary Icon: Geometric checklist with gradient checkmarks\n• Typography: Sans-serif font (Montserrat or similar)\n• Layout: Icon positioned left of wordmark\n\nColor Scheme:\n• Primary: #2563EB (Professional Blue)\n• Secondary: #10B981 (Success Green for checkmarks)\n• Neutral: #374151 (Dark Gray for text)\n• Gradient: Linear gradient from #2563EB to #10B981\n\nScalability:\n• Minimum size: 16x16px for favicons\n• Recommended sizes: 32px, 64px, 128px, 256px\n• Vector format (SVG) for infinite scalability\n• Simplified version for small sizes (icon only)\n\nUsage Guidelines:\n• Maintain minimum clear space of 0.5x logo height\n• Use on light backgrounds primarily\n• Dark variant available for light backgrounds\n• Monochrome version for single-color applications",
                metadata: {
                  model: "gpt-4-vision-preview",
                  provider: "openai",
                  tokens_used: 425,
                  processing_time_ms: 3200,
                  temperature: 0.7,
                  max_tokens: 800,
                  image_analysis: true,
                  design_complexity: "medium"
                }
              },
              {
                prompt: "Design a vibrant Summer Sale banner for a fashion store targeting young adults. The banner should be eye-catching, trendy, and convey excitement about summer fashion deals. Include recommendations for layout, color schemes, typography, and visual elements that would appeal to the 18-30 age demographic. Consider both digital and print applications. The design should communicate urgency and value while maintaining brand sophistication.",
                response: "SUMMER SALE FASHION BANNER DESIGN\n\nConcept: Energetic tropical-inspired banner with bold typography and fashion elements\n\nVisual Elements:\n• Background: Gradient sunset colors (coral pink to orange)\n• Accent Graphics: Palm leaves, sunglasses, geometric shapes\n• Fashion Elements: Silhouettes of trendy clothing items\n• Typography: Bold sans-serif headers with script accent fonts\n\nColor Palette:\n• Primary: #FF6B6B (Coral Pink)\n• Secondary: #FFD93D (Sunny Yellow)\n• Accent: #4ECDC4 (Turquoise)\n• Background: Gradient from #FF8E8E to #FF9F1C\n• Text: #FFFFFF (White) and #2C3E50 (Dark Blue)\n\nLayout Structure:\n• Header: \"SUMMER SALE\" in large bold letters\n• Subheader: \"Up to 70% OFF\" with emphasis styling\n• CTA: \"Shop Now\" button in contrasting color\n• Decorative elements scattered around text\n\nTarget Audience Appeal:\n• Instagram-worthy aesthetic\n• Mobile-first responsive design\n• Trendy geometric patterns\n• Millennial/Gen-Z color preferences\n• Clean but energetic composition\n\nApplications:\n• Digital: Social media, website banners, email campaigns\n• Print: Store window displays, flyers, posters\n• Dimensions: Multiple sizes for various platforms",
                metadata: {
                  model: "claude-3-sonnet",
                  provider: "anthropic", 
                  tokens_used: 387,
                  processing_time_ms: 2800,
                  temperature: 0.8,
                  max_tokens: 1000,
                  creativity_level: "high",
                  brand_alignment: "fashion_retail"
                }
              }
            ],
            metadata: {
              total_processed: 2,
              successful: 2,
              failed: 0,
              average_processing_time: 3000,
              total_tokens_used: 812,
              processing_quality: "high",
              model_diversity: true
            }
          },
          "sheets-write-4": {
            operation: "Google Sheets Write",
            status: "completed",
            execution_time_ms: 800,
            written_rows: 2,
            sheet_url: "https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
          }
        }
      }
    }
  }
];

const sampleExecutionLogs: ExecutionLog[] = [
  {
    id: "log-1",
    step_name: "Manual Trigger",
    status: "completed",
    created_at: "2024-12-28T19:21:39.000Z",
    execution_time_ms: 150
  },
  {
    id: "log-2", 
    step_name: "Google Sheets Read",
    status: "completed",
    created_at: "2024-12-28T19:21:41.000Z",
    execution_time_ms: 1200
  },
  {
    id: "log-3",
    step_name: "AI Content Generation", 
    status: "completed",
    created_at: "2024-12-28T19:21:45.000Z",
    execution_time_ms: 8500
  },
  {
    id: "log-4",
    step_name: "Google Sheets Write",
    status: "completed", 
    created_at: "2024-12-28T19:23:10.000Z",
    execution_time_ms: 800
  }
];

const ExecutionPanelDemo: React.FC = () => {
  const [isOpen, setIsOpen] = useState(true);

  if (!isOpen) {
    return (
      <div className="p-8">
        <button 
          onClick={() => setIsOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Open Execution Panel Demo
        </button>
      </div>
    );
  }

  return (
    <div className="h-screen flex">
      {/* Main content area */}
      <div className="flex-1 bg-gray-100 dark:bg-gray-900 p-8">
        <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
          Execution Panel Demo
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          This demo shows how the ExecutionPanel processes and displays workflow execution data.
        </p>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Sample Workflow Execution
          </h2>
          <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
            <div>📋 <strong>Instance ID:</strong> 8a70d57e-a460-46b3-93be-ad71ffa65360</div>
            <div>🔄 <strong>Status:</strong> Completed</div>
            <div>⏱️ <strong>Duration:</strong> 1m 36s</div>
            <div>📊 <strong>Steps:</strong> 4 completed</div>
          </div>
        </div>
      </div>

      {/* ExecutionPanel */}
      <ExecutionPanel
        executionStatus={sampleExecutionStatus}
        executionLogs={sampleExecutionLogs}
        executionEvents={sampleExecutionEvents}
        onClose={() => setIsOpen(false)}
      />
    </div>
  );
};

export default ExecutionPanelDemo;
