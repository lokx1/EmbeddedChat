// Main authentication component that handles login/register switching
import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { LoginForm } from './LoginForm';
import { RegisterForm, RegisterData } from './RegisterForm';
import { Toast } from '../UI/Toast';

interface AuthPageProps {
  onAuthSuccess?: () => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess }) => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'success' | 'error'>('success');

  const { login, register, loading, error, clearError } = useAuth();

  const showSuccessToast = (message: string) => {
    setToastMessage(message);
    setToastType('success');
    setShowToast(true);
  };

  const showErrorToast = (message: string) => {
    setToastMessage(message);
    setToastType('error');
    setShowToast(true);
  };

  const handleLogin = async (username: string, password: string) => {
    try {
      clearError();
      await login({ username, password });
      showSuccessToast('Welcome back! You have been logged in successfully.');
      onAuthSuccess?.();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 
        (typeof err === 'string' ? err : 'Login failed. Please try again.');
      showErrorToast(errorMessage);
    }
  };

  const handleRegister = async (registerData: RegisterData) => {
    try {
      clearError();
      await register(registerData);
      showSuccessToast('Account created successfully! Welcome to EmbeddedChat.');
      onAuthSuccess?.();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 
        (typeof err === 'string' ? err : 'Registration failed. Please try again.');
      showErrorToast(errorMessage);
    }
  };

  const switchToRegister = () => {
    clearError();
    setIsLoginMode(false);
  };

  const switchToLogin = () => {
    clearError();
    setIsLoginMode(true);
  };

  return (
    <>
      {isLoginMode ? (
        <LoginForm
          onLogin={handleLogin}
          onSwitchToRegister={switchToRegister}
          loading={loading}
          error={error || undefined}
        />
      ) : (
        <RegisterForm
          onRegister={handleRegister}
          onSwitchToLogin={switchToLogin}
          loading={loading}
          error={error || undefined}
        />
      )}

      {showToast && (
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setShowToast(false)}
        />
      )}
    </>
  );
};
