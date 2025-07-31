/**
 * Frontend Configuration
 * Environment variables and configuration settings
 */

// Default API configuration
export const API_CONFIG = {
  BASE_URL: (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
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
  isDevelopment: (import.meta as any).env?.DEV || false,
  isProduction: (import.meta as any).env?.PROD || false,
};

export default {
  API_CONFIG,
  WORKFLOW_CONFIG,
  UI_CONFIG,
  FEATURES,
  ENV,
};
