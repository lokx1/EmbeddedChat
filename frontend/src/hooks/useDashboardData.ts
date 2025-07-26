// Custom hook for dashboard data
import { useState, useEffect } from 'react';

interface DashboardStats {
  overview: {
    total_chats: number;
    active_users: number;
    total_documents: number;
    system_status: string;
  };
  performance: {
    memory_usage: {
      percent: number;
      used_gb: number;
      total_gb: number;
    };
    cpu_usage: {
      percent: number;
    };
    uptime: string;
  };
  recent_activity: Array<{
    action: string;
    details: string;
    time: string;
    type: string;
  }>;
  analytics: {
    daily_messages: Array<{
      date: string;
      messages: number;
    }>;
    total_period: number;
  };
  documents: {
    total_documents: number;
    indexed_documents: number;
    storage_used_gb: number;
    categories: Record<string, number>;
  };
  timestamp: string;
}

interface UseDashboardDataReturn {
  data: DashboardStats | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export const useDashboardData = (): UseDashboardDataReturn => {
  const [data, setData] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/v1/dashboard/stats/all');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
      
      // Fallback to mock data if API fails
      setData({
        overview: {
          total_chats: 742,
          active_users: 23,
          total_documents: 156,
          system_status: 'Healthy'
        },
        performance: {
          memory_usage: { percent: 67, used_gb: 2.1, total_gb: 8.0 },
          cpu_usage: { percent: 23 },
          uptime: '2:34:15'
        },
        recent_activity: [
          {
            action: 'New message',
            details: 'User started a new conversation',
            time: '2 minutes ago',
            type: 'message'
          },
          {
            action: 'Document uploaded',
            details: 'API Documentation.pdf processed',
            time: '15 minutes ago',
            type: 'document'
          }
        ],
        analytics: {
          daily_messages: [
            { date: '2025-07-20', messages: 45 },
            { date: '2025-07-21', messages: 67 },
            { date: '2025-07-22', messages: 52 },
            { date: '2025-07-23', messages: 89 },
            { date: '2025-07-24', messages: 76 },
            { date: '2025-07-25', messages: 94 },
            { date: '2025-07-26', messages: 112 }
          ],
          total_period: 7
        },
        documents: {
          total_documents: 156,
          indexed_documents: 142,
          storage_used_gb: 2.4,
          categories: {
            'Technical': 45,
            'Business': 32,
            'Personal': 79
          }
        },
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const refetch = () => {
    fetchData();
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error, refetch };
};

// Hook for overview stats only
export const useOverviewStats = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const response = await fetch('/api/v1/dashboard/stats/overview');
        if (!response.ok) throw new Error('Failed to fetch overview');
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch');
        // Fallback data
        setData({
          total_chats: 742,
          active_users: 23,
          total_documents: 156,
          system_status: 'Healthy'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchOverview();
  }, []);

  return { data, loading, error };
};

// Hook for performance stats
export const usePerformanceStats = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPerformance = async () => {
      try {
        const response = await fetch('/api/v1/dashboard/stats/performance');
        if (!response.ok) throw new Error('Failed to fetch performance');
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch');
        // Fallback data
        setData({
          memory_usage: { percent: 67, used_gb: 2.1, total_gb: 8.0 },
          cpu_usage: { percent: 23 },
          uptime: '2:34:15'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchPerformance();
    
    // Auto-refresh every 5 seconds for performance data
    const interval = setInterval(fetchPerformance, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error };
};
