/**
 * Frontend Configuration
 * Environment variables and configuration settings
 */

// Get the current environment
const isProduction = import.meta.env?.PROD || false;
const isDevelopment = import.meta.env?.DEV || false;

// Default API configuration
export const API_CONFIG = {
  BASE_URL: (() => {
    // If VITE_API_BASE_URL is explicitly set, use it
    if ((import.meta as any).env?.VITE_API_BASE_URL) {
      return (import.meta as any).env.VITE_API_BASE_URL;
    }
    
    // Production environment detection
    if (isProduction || window.location.hostname.includes('vercel.app')) {
      // Railway backend URL (update this when Railway deployment is ready)
      // For now, fallback to a working endpoint
      const railwayUrl = 'https://embedded-chat-backend-production.up.railway.app'; // Update this
      const vercelBackup = 'https://embedded-chat-backend-bnzj7r6o4-bao-longs-projects-a3dea26a.vercel.app';
      
      // Try Railway first, fallback to Vercel if needed
      return railwayUrl;
    }
    
    // Development fallback
    return 'http://localhost:8000';
  })(),
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
};

// Enhanced API connection test with fallback
export const testAPIConnection = async () => {
  const endpoints = [
    API_CONFIG.BASE_URL,
    'https://embedded-chat-backend-bnzj7r6o4-bao-longs-projects-a3dea26a.vercel.app' // Backup
  ];

  for (const endpoint of endpoints) {
    try {
      console.log(`🔄 Testing API endpoint: ${endpoint}`);
      
      const response = await fetch(`${endpoint}/health`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Backend API is working at: ${endpoint}`, data);
        
        // Update the API_CONFIG to use the working endpoint
        (API_CONFIG as any).BASE_URL = endpoint;
        
        return { success: true, data, endpoint };
      } else {
        console.error(`❌ Backend API error at ${endpoint}:`, response.status, response.statusText);
      }
    } catch (error) {
      console.error(`❌ Backend API connection failed for ${endpoint}:`, error);
    }
  }
  
  return { success: false, error: 'All backend endpoints failed' };
};

// API Helper functions
export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Request failed for ${url}:`, error);
    throw error;
  }
};

// Specific API endpoints for your app
export const API_ENDPOINTS = {
  // Health checks
  HEALTH: '/health',
  HEALTH_V1: '/api/v1/health',
  
  // Authentication
  AUTH: '/api/v1/auth',
  LOGIN: '/api/v1/auth/login',
  REGISTER: '/api/v1/auth/register',
  
  // Chat
  CHAT: '/api/v1/chat',
  CHAT_HISTORY: '/api/v1/chat/history',
  
  // Documents
  DOCUMENTS: '/api/v1/documents',
  UPLOAD: '/api/v1/documents/upload',
  
  // Dashboard
  DASHBOARD: '/api/v1/dashboard',
  STATS: '/api/v1/dashboard/stats',
  
  // Workflow
  WORKFLOW: '/api/v1/workflow',
  WORKFLOW_EXECUTE: '/api/v1/workflow/execute',
  
  // Test endpoint
  TEST: '/api/test',
};

// Workflow configuration
export const WORKFLOW_CONFIG = {
  AUTO_REFRESH_INTERVAL: 2000, // 2 seconds for running workflows
  MAX_LOG_ENTRIES: 1000,
  HEALTH_CHECK_INTERVAL: 30000, // 30 seconds
};

// UI configuration
export const UI_CONFIG = {
  TOAST_DURATION: 5000, // 5 seconds
  DEBOUNCE_DELAY: 300, // 300ms
};

// Feature flags
export const FEATURES = {
  WORKFLOW_AUTOMATION: true,
  GOOGLE_SHEETS_INTEGRATION: true,
  AI_PROVIDERS: {
    OPENAI: true,
    CLAUDE: true,
    OLLAMA: true,
  },
  ANALYTICS: true,
  NOTIFICATIONS: {
    EMAIL: true,
    SLACK: true,
  },
};

// Environment detection
export const ENV = {
  isDevelopment,
  isProduction,
  apiBaseUrl: API_CONFIG.BASE_URL,
};

export default {
  API_CONFIG,
  API_ENDPOINTS,
  WORKFLOW_CONFIG,
  UI_CONFIG,
  FEATURES,
  ENV,
  testAPIConnection,
  apiRequest,
};
