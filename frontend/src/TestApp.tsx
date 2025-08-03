/**
 * Simple test app to demonstrate ExecutionPanel with demo data
 */
import { ThemeProvider } from './contexts/ThemeContext';
import { ExecutionPanelDemo } from './components/WorkflowEditor';

export default function TestApp() {
  return (
    <ThemeProvider>
      <ExecutionPanelDemo />
    </ThemeProvider>
  );
}
