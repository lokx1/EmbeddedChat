import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/apiService';

interface ApiState {
  isConnected: boolean;
  isLoading: boolean;
  endpoint: string;
  error: string | null;
}

export const useApi = () => {
  const [state, setState] = useState<ApiState>({
    isConnected: false,
    isLoading: true,
    endpoint: '',
    error: null,
  });

  const initialize = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const connected = await apiService.initialize();
      setState({
        isConnected: connected,
        isLoading: false,
        endpoint: apiService.getCurrentEndpoint(),
        error: connected ? null : 'Failed to connect to backend',
      });
    } catch (error) {
      setState({
        isConnected: false,
        isLoading: false,
        endpoint: '',
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }, []);

  const reconnect = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const connected = await apiService.reconnect();
      setState(prev => ({
        ...prev,
        isConnected: connected,
        isLoading: false,
        endpoint: apiService.getCurrentEndpoint(),
        error: connected ? null : 'Failed to reconnect to backend',
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnected: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
    }
  }, []);

  const healthCheck = useCallback(async () => {
    try {
      await apiService.healthCheck();
      setState(prev => ({ ...prev, isConnected: true, error: null }));
      return true;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isConnected: false, 
        error: 'Health check failed' 
      }));
      return false;
    }
  }, []);

  useEffect(() => {
    initialize();
  }, [initialize]);

  // Periodic health check
  useEffect(() => {
    if (!state.isConnected) return;

    const interval = setInterval(() => {
      healthCheck();
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [state.isConnected, healthCheck]);

  return {
    ...state,
    reconnect,
    healthCheck,
    api: apiService,
  };
};

export default useApi; 