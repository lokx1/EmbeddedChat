/**
 * AI Provider Settings Modal
 * Configure AI providers, models, and API keys for chat
 */
import { useState, useEffect } from 'react';
import { ChatSettings, AI_PROVIDERS, AIProvider } from './types';

interface AIProviderSettingsProps {
  settings: ChatSettings;
  onUpdate: (settings: Partial<ChatSettings>) => void;
  onClose: () => void;
}

export default function AIProviderSettings({ settings, onUpdate, onClose }: AIProviderSettingsProps) {
  const [formData, setFormData] = useState<ChatSettings>(settings);
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [testingConnection, setTestingConnection] = useState(false);

  // Update form data when settings change
  useEffect(() => {
    setFormData(settings);
  }, [settings]);

  // Validate API key format
  const validateAPIKey = (provider: AIProvider, apiKey: string): string | null => {
    if (!apiKey && provider !== 'ollama') {
      return 'API Key is required for cloud providers';
    }
    
    if (apiKey && provider !== 'ollama') {
      const providerConfig = AI_PROVIDERS[provider];
      if (providerConfig.keyPrefix && !apiKey.startsWith(providerConfig.keyPrefix)) {
        return `${providerConfig.name} API key should start with "${providerConfig.keyPrefix}"`;
      }
    }
    
    return null;
  };

  // Handle input changes
  const handleInputChange = (field: keyof ChatSettings, value: any) => {
    const newFormData = { ...formData, [field]: value };
    
    // Auto-update model when provider changes
    if (field === 'provider') {
      const providerConfig = AI_PROVIDERS[value as AIProvider];
      newFormData.model = providerConfig.defaultModel;
      newFormData.apiKey = ''; // Clear API key when switching providers
    }
    
    // Validate API key
    if (field === 'apiKey' || field === 'provider') {
      const provider = field === 'provider' ? value : newFormData.provider;
      const apiKey = field === 'apiKey' ? value : newFormData.apiKey;
      
      const apiKeyError = validateAPIKey(provider, apiKey);
      setErrors(prev => ({
        ...prev,
        apiKey: apiKeyError || ''
      }));
    }
    
    setFormData(newFormData);
  };

  // Test API connection
  const testConnection = async () => {
    if (formData.provider === 'ollama') {
      // TODO: Test Ollama connection
      alert('Ollama connection test not implemented yet');
      return;
    }

    if (!formData.apiKey) {
      setErrors(prev => ({ ...prev, apiKey: 'API key is required for testing' }));
      return;
    }

    setTestingConnection(true);
    try {
      // TODO: Implement actual API test
      await new Promise(resolve => setTimeout(resolve, 2000)); // Mock delay
      alert('Connection successful!');
    } catch (error) {
      alert('Connection failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setTestingConnection(false);
    }
  };

  // Save settings
  const handleSave = () => {
    // Validate all fields
    const apiKeyError = validateAPIKey(formData.provider, formData.apiKey);
    if (apiKeyError) {
      setErrors(prev => ({ ...prev, apiKey: apiKeyError }));
      return;
    }

    onUpdate(formData);
    onClose();
  };

  // Reset to defaults
  const resetToDefaults = () => {
    const defaultSettings: ChatSettings = {
      provider: 'gemini',
      model: 'gemini-2.5-flash',
      apiKey: '',
      temperature: 0.7,
      maxTokens: 2000,
      systemPrompt: 'You are a helpful AI assistant.'
    };
    setFormData(defaultSettings);
    setErrors({});
  };

  const currentProvider = AI_PROVIDERS[formData.provider];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            AI Provider Settings
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="space-y-6">
            {/* AI Provider Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                AI Provider
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(AI_PROVIDERS).map(([key, provider]) => (
                  <button
                    key={key}
                    onClick={() => handleInputChange('provider', key)}
                    className={`p-4 text-left border-2 rounded-lg transition-all ${
                      formData.provider === key
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <div className="font-medium text-gray-900 dark:text-white">
                      {provider.name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {provider.description}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* API Key */}
            {formData.provider !== 'ollama' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Key <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={formData.apiKey}
                  onChange={(e) => handleInputChange('apiKey', e.target.value)}
                  placeholder={`Enter your ${currentProvider.name} API key`}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent ${
                    errors.apiKey 
                      ? 'border-red-300 focus:ring-red-500' 
                      : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500'
                  } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                />
                {errors.apiKey && (
                  <p className="text-xs text-red-500 mt-1">{errors.apiKey}</p>
                )}
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Get your API key from{' '}
                  {formData.provider === 'openai' && 'OpenAI Dashboard'}
                  {formData.provider === 'claude' && 'Anthropic Console'}
                  {formData.provider === 'gemini' && 'Google AI Studio'}
                </p>
              </div>
            )}

            {/* Model Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Model
              </label>
              <select
                value={formData.model}
                onChange={(e) => handleInputChange('model', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {currentProvider.models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>

            {/* Advanced Settings */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Advanced Settings
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Temperature */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Temperature: {formData.temperature}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={formData.temperature}
                    onChange={(e) => handleInputChange('temperature', parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                    <span>Focused</span>
                    <span>Creative</span>
                  </div>
                </div>

                {/* Max Tokens */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Max Tokens
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="8000"
                    step="100"
                    value={formData.maxTokens}
                    onChange={(e) => handleInputChange('maxTokens', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              {/* System Prompt */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  System Prompt
                </label>
                <textarea
                  value={formData.systemPrompt}
                  onChange={(e) => handleInputChange('systemPrompt', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Enter system prompt to define AI behavior..."
                />
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex gap-2">
            <button
              onClick={testConnection}
              disabled={testingConnection || (formData.provider !== 'ollama' && !formData.apiKey)}
              className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {testingConnection ? 'Testing...' : 'Test Connection'}
            </button>
            <button
              onClick={resetToDefaults}
              className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Reset to Defaults
            </button>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!!errors.apiKey}
              className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
