import React, { useState, useEffect, useCallback } from 'react';
import { createRoot } from 'react-dom/client';

// Type definitions for window.openai API
declare global {
  interface Window {
    openai: {
      theme: 'light' | 'dark';
      userAgent: {
        device: { type: 'mobile' | 'tablet' | 'desktop' | 'unknown' };
        capabilities: { hover: boolean; touch: boolean };
      };
      locale: string;
      maxHeight: number;
      displayMode: 'pip' | 'inline' | 'fullscreen';
      safeArea: {
        insets: { top: number; bottom: number; left: number; right: number };
      };
      toolInput: any;
      toolOutput: any;
      toolResponseMetadata: any;
      widgetState: any;
      callTool: (name: string, args: Record<string, unknown>) => Promise<any>;
      sendFollowUpMessage: (args: { prompt: string }) => Promise<void>;
      openExternal: (payload: { href: string }) => void;
      requestDisplayMode: (args: { mode: 'pip' | 'inline' | 'fullscreen' }) => Promise<{ mode: string }>;
      setWidgetState: (state: any) => Promise<void>;
    };
  }
}

// Hook to subscribe to window.openai global changes
function useOpenAiGlobal<K extends keyof typeof window.openai>(
  key: K
): typeof window.openai[K] {
  const [value, setValue] = useState(() => window.openai?.[key]);

  useEffect(() => {
    const handleSetGlobal = (event: CustomEvent) => {
      const newValue = event.detail?.globals?.[key];
      if (newValue !== undefined) {
        setValue(newValue);
      }
    };

    window.addEventListener('openai:set_globals', handleSetGlobal as EventListener, {
      passive: true,
    });

    return () => {
      window.removeEventListener('openai:set_globals', handleSetGlobal as EventListener);
    };
  }, [key]);

  return value;
}

// Main demo component
function OneAgentUXDemo() {
  const theme = useOpenAiGlobal('theme');
  const displayMode = useOpenAiGlobal('displayMode');
  const toolOutput = useOpenAiGlobal('toolOutput');
  const maxHeight = useOpenAiGlobal('maxHeight');
  const userAgent = useOpenAiGlobal('userAgent');

  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const handleRefreshData = useCallback(async () => {
    try {
      await window.openai?.callTool('demo_ux_component', {});
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  }, []);

  const handleRequestFullscreen = useCallback(async () => {
    try {
      await window.openai?.requestDisplayMode({ mode: 'fullscreen' });
    } catch (error) {
      console.error('Failed to request fullscreen:', error);
    }
  }, []);

  const handleSendMessage = useCallback(async () => {
    try {
      await window.openai?.sendFollowUpMessage({
        prompt: 'Can you show me more details about the organization theme?'
      });
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }, []);

  if (!isLoaded) {
    return (
      <div style={{
        padding: '20px',
        textAlign: 'center',
        color: theme === 'dark' ? '#ffffff' : '#000000'
      }}>
        Loading OneAgent UX Demo...
      </div>
    );
  }

  const containerStyle: React.CSSProperties = {
    fontFamily: 'system-ui, -apple-system, sans-serif',
    padding: '20px',
    borderRadius: '12px',
    backgroundColor: theme === 'dark' ? '#1a1a1a' : '#ffffff',
    color: theme === 'dark' ? '#ffffff' : '#000000',
    border: `1px solid ${theme === 'dark' ? '#333333' : '#e0e0e0'}`,
    maxHeight: `${maxHeight}px`,
    overflow: 'auto',
    boxShadow: theme === 'dark' 
      ? '0 4px 12px rgba(0, 0, 0, 0.3)' 
      : '0 4px 12px rgba(0, 0, 0, 0.1)',
  };

  const buttonStyle: React.CSSProperties = {
    padding: '8px 16px',
    margin: '4px',
    borderRadius: '6px',
    border: 'none',
    backgroundColor: theme === 'dark' ? '#4a9eff' : '#0066cc',
    color: 'white',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  };

  const colorSwatchStyle = (color: string): React.CSSProperties => ({
    width: '40px',
    height: '40px',
    borderRadius: '8px',
    backgroundColor: color,
    border: `2px solid ${theme === 'dark' ? '#333333' : '#e0e0e0'}`,
    display: 'inline-block',
    margin: '4px',
  });

  return (
    <div style={containerStyle}>
      <h2 style={{ margin: '0 0 20px 0', fontSize: '24px', fontWeight: '600' }}>
        🎨 OneAgent UX Demo
      </h2>
      
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '18px' }}>Environment Info</h3>
        <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
          <div><strong>Theme:</strong> {theme}</div>
          <div><strong>Display Mode:</strong> {displayMode}</div>
          <div><strong>Device:</strong> {userAgent?.device?.type || 'unknown'}</div>
          <div><strong>Max Height:</strong> {maxHeight}px</div>
          <div><strong>Touch Support:</strong> {userAgent?.capabilities?.touch ? 'Yes' : 'No'}</div>
        </div>
      </div>

      {toolOutput && (
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: '18px' }}>Organization Data</h3>
          <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
            <div><strong>Organization ID:</strong> {toolOutput.organizationId || 'N/A'}</div>
            <div><strong>Organization Name:</strong> {toolOutput.organizationName || 'N/A'}</div>
            {toolOutput.logoUrl && (
              <div style={{ marginTop: '8px' }}>
                <strong>Logo:</strong>
                <img 
                  src={toolOutput.logoUrl} 
                  alt="Organization Logo" 
                  style={{ 
                    maxWidth: '100px', 
                    maxHeight: '50px', 
                    marginLeft: '8px',
                    borderRadius: '4px'
                  }} 
                />
              </div>
            )}
          </div>
        </div>
      )}

      {toolOutput?.themeTokens && (
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: '18px' }}>Theme Colors</h3>
          <div style={{ fontSize: '14px' }}>
            {toolOutput.themeTokens.ref?.palette && (
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontWeight: '600', marginBottom: '8px' }}>Primary Colors:</div>
                {Object.entries(toolOutput.themeTokens.ref.palette).map(([key, color]) => (
                  <div key={key} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                    <div style={colorSwatchStyle(color as string)}></div>
                    <span style={{ marginLeft: '8px' }}>{key}: {color}</span>
                  </div>
                ))}
              </div>
            )}
            {toolOutput.themeTokens.comp?.layout && (
              <div>
                <div style={{ fontWeight: '600', marginBottom: '8px' }}>Layout Colors:</div>
                {Object.entries(toolOutput.themeTokens.comp.layout).map(([key, color]) => (
                  <div key={key} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                    <div style={colorSwatchStyle(color as string)}></div>
                    <span style={{ marginLeft: '8px' }}>{key}: {color}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '18px' }}>Interactive Features</h3>
        <div>
          <button style={buttonStyle} onClick={handleRefreshData}>
            🔄 Refresh Data
          </button>
          <button style={buttonStyle} onClick={handleRequestFullscreen}>
            📺 Request Fullscreen
          </button>
          <button style={buttonStyle} onClick={handleSendMessage}>
            💬 Send Follow-up Message
          </button>
        </div>
      </div>

      <div style={{ 
        marginTop: '20px', 
        padding: '12px', 
        backgroundColor: theme === 'dark' ? '#2a2a2a' : '#f5f5f5',
        borderRadius: '8px',
        fontSize: '12px',
        color: theme === 'dark' ? '#cccccc' : '#666666'
      }}>
        <strong>Demo Features:</strong> This component demonstrates basic window.openai integration, 
        theme responsiveness, tool output display, and interactive capabilities. 
        It serves as a foundation for building more complex UX components.
      </div>
    </div>
  );
}

// Mount the component
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<OneAgentUXDemo />);
} else {
  console.error('Root element not found');
}
