// Script để tạo demo workflow với Google Sheets Write node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const demoWorkflow = {
  nodes: [
    {
      id: 'node_1',
      type: 'sheets',
      position: { x: 100, y: 100 },
      data: { 
        label: 'Google Sheets Read',
        type: 'sheets'
      }
    },
    {
      id: 'node_2', 
      type: 'ai_processing',
      position: { x: 400, y: 100 },
      data: {
        label: 'AI Processing',
        type: 'ai_processing'
      }
    },
    {
      id: 'node_3',
      type: 'google_sheets_write',
      position: { x: 700, y: 50 },
      data: {
        label: 'Google Sheets Write',
        type: 'google_sheets_write'
      }
    },
    {
      id: 'node_4',
      type: 'google_drive_write',
      position: { x: 700, y: 150 },
      data: {
        label: 'Google Drive Write (CSV)',
        type: 'google_drive_write'
      }
    }
  ],
  edges: [
    {
      id: 'edge_1',
      source: 'node_1',
      target: 'node_2',
      type: 'smoothstep'
    },
    {
      id: 'edge_2',
      source: 'node_2',
      target: 'node_3',
      type: 'smoothstep'
    },
    {
      id: 'edge_3',
      source: 'node_2', 
      target: 'node_4',
      type: 'smoothstep'
    }
  ]
};

// Tạo workflow config file
const configPath = path.join(__dirname, 'src', 'data', 'demo_workflow.json');
const configDir = path.dirname(configPath);

// Tạo thư mục nếu chưa có
if (!fs.existsSync(configDir)) {
  fs.mkdirSync(configDir, { recursive: true });
}

// Lưu file
fs.writeFileSync(configPath, JSON.stringify(demoWorkflow, null, 2));
console.log('Demo workflow created at:', configPath);
