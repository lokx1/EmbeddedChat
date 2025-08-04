/**
 * Email Report Panel - Component for sending workflow execution reports
 */
import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';

interface EmailReportPanelProps {
  instanceId?: string;
  workflowName?: string;
  executionStatus?: any;
  onClose?: () => void;
}

const EmailReportPanel: React.FC<EmailReportPanelProps> = ({
  instanceId,
  workflowName,
  executionStatus,
  onClose
}) => {
  const { isDark } = useTheme() || { isDark: false };
  const [recipientEmail, setRecipientEmail] = useState('');
  const [includeAnalytics, setIncludeAnalytics] = useState(true);
  const [includeDetailedLogs, setIncludeDetailedLogs] = useState(true);
  const [reportType, setReportType] = useState<'execution' | 'daily'>('execution');
  const [isSending, setIsSending] = useState(false);
  const [sendResult, setSendResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSendExecutionReport = async () => {
    if (!recipientEmail || !instanceId) return;

    setIsSending(true);
    setSendResult(null);

    try {
      const response = await fetch(`/api/v1/workflow/instances/${instanceId}/send-report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipient_email: recipientEmail,
          include_analytics: includeAnalytics,
          include_detailed_logs: includeDetailedLogs
        })
      });

      const result = await response.json();
      
      setSendResult({
        success: result.success,
        message: result.message || (result.success ? 'Report sent successfully!' : 'Failed to send report')
      });

    } catch (error) {
      setSendResult({
        success: false,
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleSendDailyReport = async () => {
    if (!recipientEmail) return;

    setIsSending(true);
    setSendResult(null);

    try {
      const response = await fetch('/api/v1/workflow/reports/daily-analytics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipient_email: recipientEmail,
          date: new Date().toISOString().split('T')[0] // Today's date
        })
      });

      const result = await response.json();
      
      setSendResult({
        success: result.success,
        message: result.message || (result.success ? 'Daily report sent successfully!' : 'Failed to send daily report')
      });

    } catch (error) {
      setSendResult({
        success: false,
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleSendReport = () => {
    if (reportType === 'execution') {
      handleSendExecutionReport();
    } else {
      handleSendDailyReport();
    }
  };

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50`}>
      <div className={`
        w-full max-w-lg mx-4 rounded-lg shadow-xl
        ${isDark ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}
      `}>
        {/* Header */}
        <div className={`
          px-6 py-4 border-b rounded-t-lg
          ${isDark ? 'border-gray-700 bg-blue-900' : 'border-gray-200 bg-blue-50'}
        `}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <span className="text-2xl">📧</span>
              <span>Send Email Report</span>
            </h3>
            {onClose && (
              <button
                onClick={onClose}
                className={`
                  p-2 rounded-md transition-colors text-gray-500 hover:text-gray-700
                  ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}
                `}
              >
                ✕
              </button>
            )}
          </div>
          <p className={`text-sm mt-1 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
            Send comprehensive workflow reports with analytics and logs
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-5">
          {/* Report Type Selection */}
          <div>
            <label className="block text-sm font-medium mb-3">
              📊 Report Type
            </label>
            <div className="space-y-3">
              <label className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${
                reportType === 'execution' 
                  ? isDark ? 'bg-blue-900 border-blue-600' : 'bg-blue-50 border-blue-300'
                  : isDark ? 'border-gray-600 hover:border-gray-500' : 'border-gray-300 hover:border-gray-400'
              }`}>
                <input
                  type="radio"
                  value="execution"
                  checked={reportType === 'execution'}
                  onChange={(e) => setReportType(e.target.value as 'execution')}
                  className="mr-3 text-blue-600"
                  disabled={!instanceId}
                />
                <div className={!instanceId ? 'opacity-50' : ''}>
                  <span className="font-medium">📋 Workflow Execution Report</span>
                  <span className="text-sm block mt-1 ml-6 text-gray-500">
                    Detailed report for this specific workflow run
                  </span>
                  {instanceId && workflowName && (
                    <span className="text-xs text-blue-600 block ml-6 mt-1">
                      {workflowName} • ID: {instanceId.slice(0, 8)}...
                    </span>
                  )}
                </div>
              </label>
              
              <label className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${
                reportType === 'daily' 
                  ? isDark ? 'bg-blue-900 border-blue-600' : 'bg-blue-50 border-blue-300'
                  : isDark ? 'border-gray-600 hover:border-gray-500' : 'border-gray-300 hover:border-gray-400'
              }`}>
                <input
                  type="radio"
                  value="daily"
                  checked={reportType === 'daily'}
                  onChange={(e) => setReportType(e.target.value as 'daily')}
                  className="mr-3 text-blue-600"
                />
                <div>
                  <span className="font-medium">📈 Daily Analytics Report</span>
                  <span className="text-sm block mt-1 ml-6 text-gray-500">
                    Today's workflow performance summary with charts
                  </span>
                </div>
              </label>
            </div>
          </div>

          {/* Recipient Email */}
          <div>
            <label className="block text-sm font-medium mb-2">
              📧 Recipient Email *
            </label>
            <input
              type="email"
              value={recipientEmail}
              onChange={(e) => setRecipientEmail(e.target.value)}
              placeholder="Enter email address"
              className={`
                w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors
                ${isDark 
                  ? 'bg-gray-700 border-gray-600 focus:ring-blue-500' 
                  : 'bg-white border-gray-300 focus:ring-blue-500'
                }
              `}
              required
            />
          </div>

          {/* Options for Execution Report */}
          {reportType === 'execution' && (
            <div className="space-y-3">
              <div className="text-sm font-medium">Report Options</div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeAnalytics}
                  onChange={(e) => setIncludeAnalytics(e.target.checked)}
                  className="mr-2"
                />
                <span>
                  Include Analytics Chart
                  <span className="text-sm text-gray-500 block ml-6">
                    Success rate, timeline, and performance visualizations
                  </span>
                </span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeDetailedLogs}
                  onChange={(e) => setIncludeDetailedLogs(e.target.checked)}
                  className="mr-2"
                />
                <span>
                  Include Detailed Logs
                  <span className="text-sm text-gray-500 block ml-6">
                    Full execution logs and JSON data attachment
                  </span>
                </span>
              </label>
            </div>
          )}

          {/* Execution Status Info */}
          {reportType === 'execution' && executionStatus && (
            <div className={`
              p-3 rounded-md text-sm
              ${isDark ? 'bg-gray-700' : 'bg-gray-100'}
            `}>
              <div className="font-medium mb-1">Workflow Status</div>
              <div className="flex items-center justify-between">
                <span>Status:</span>
                <span className={`
                  px-2 py-1 rounded text-xs font-medium
                  ${executionStatus.status === 'completed' 
                    ? 'bg-green-100 text-green-800' 
                    : executionStatus.status === 'failed'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                  }
                `}>
                  {executionStatus.status?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
              {executionStatus.execution_time && (
                <div className="flex items-center justify-between mt-1">
                  <span>Duration:</span>
                  <span>{(executionStatus.execution_time / 1000).toFixed(2)}s</span>
                </div>
              )}
            </div>
          )}

          {/* Send Result */}
          {sendResult && (
            <div className={`
              p-3 rounded-md text-sm
              ${sendResult.success 
                ? (isDark ? 'bg-green-900 text-green-200' : 'bg-green-100 text-green-800')
                : (isDark ? 'bg-red-900 text-red-200' : 'bg-red-100 text-red-800')
              }
            `}>
              <div className="flex items-center">
                <span className="mr-2">
                  {sendResult.success ? '✅' : '❌'}
                </span>
                <span>{sendResult.message}</span>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className={`
          px-6 py-4 border-t rounded-b-lg
          ${isDark ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-50'}
        `}>
          <div className="flex justify-between">
            <button
              onClick={onClose}
              className={`
                px-4 py-2 rounded-md transition-colors
                ${isDark 
                  ? 'bg-gray-700 hover:bg-gray-600 text-white' 
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
                }
              `}
            >
              Cancel
            </button>
            <button
              onClick={handleSendReport}
              disabled={!recipientEmail || isSending || (reportType === 'execution' && !instanceId)}
              className={`
                px-4 py-2 rounded-md transition-colors flex items-center
                ${!recipientEmail || isSending || (reportType === 'execution' && !instanceId)
                  ? 'bg-gray-400 cursor-not-allowed text-gray-600'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
                }
              `}
            >
              {isSending ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Sending...
                </>
              ) : (
                <>
                  📧 Send Report
                </>
              )}
            </button>
          </div>
        </div>

        {/* Help Text */}
        <div className={`
          px-6 py-3 text-xs border-t
          ${isDark ? 'border-gray-700 text-gray-400 bg-gray-800' : 'border-gray-200 text-gray-600 bg-gray-50'}
        `}>
          <div className="space-y-1">
            <div><strong>Execution Report:</strong> Detailed workflow analysis with charts and logs</div>
            <div><strong>Daily Report:</strong> Performance summary for all workflows today</div>
            <div><strong>Email Format:</strong> Professional HTML with charts and JSON attachments</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailReportPanel;
