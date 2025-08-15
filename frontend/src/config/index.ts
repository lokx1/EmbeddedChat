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
      // Use the NEWEST deployed backend URL with FastAPI
      return 'https://embedded-chat-backend-bnzj7r6o4-bao-longs-projects-a3dea26a.vercel.app';
    }
    
    // Development fallback
    return 'http://localhost:8000';
  })(),
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
};

// Debug function to test API connectivity
export const testAPIConnection = async () => {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/test`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Backend API is working:', data);
      return { success: true, data };
    } else {
      console.error('❌ Backend API error:', response.status, response.statusText);
      return { success: false, error: `HTTP ${response.status}` };
    }
  } catch (error) {
    console.error('❌ Backend API connection failed:', error);
    return { success: false, error: error.message };
  }
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
  WORKFLOW_CONFIG,
  UI_CONFIG,
  FEATURES,
  ENV,
};
