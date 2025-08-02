/**
 * Workflow Completion Notification - Shows when workflow execution completes
 */
import React, { useState, useEffect } from 'react';

interface WorkflowCompletionNotificationProps {
  instanceId: string | null;
  onClose: () => void;
  onViewLogs: () => void;
}

export const WorkflowCompletionNotification: React.FC<WorkflowCompletionNotificationProps> = ({
  instanceId,
  onClose,
  onViewLogs
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (instanceId) {
      setIsVisible(true);
      // Auto-hide after 10 seconds
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose();
      }, 10000);

      return () => clearTimeout(timer);
    }
  }, [instanceId, onClose]);

  if (!isVisible || !instanceId) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm">
      <div className="bg-green-500 text-white p-4 rounded-lg shadow-lg">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h4 className="font-bold text-sm mb-1">Workflow Completed ✅</h4>
            <p className="text-xs opacity-90 mb-3">
              Instance: {instanceId}
            </p>
            <div className="flex gap-2">
              <button
                onClick={onViewLogs}
                className="bg-white text-green-600 text-xs px-3 py-1 rounded hover:bg-gray-100"
              >
                View Logs
              </button>
              <button
                onClick={() => {
                  setIsVisible(false);
                  onClose();
                }}
                className="bg-green-600 text-white text-xs px-3 py-1 rounded hover:bg-green-700"
              >
                Dismiss
              </button>
            </div>
          </div>
          <button
            onClick={() => {
              setIsVisible(false);
              onClose();
            }}
            className="text-white hover:text-gray-200 ml-2"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkflowCompletionNotification;
