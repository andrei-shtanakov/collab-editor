/**
 * Main application component for Collaborative Code Editor
 */

import { useState, useCallback, useEffect } from 'react';
import { Play, Users } from 'lucide-react';

import { CodeEditor } from './components/CodeEditor';
import { LanguageSelector } from './components/LanguageSelector';
import { OutputPanel } from './components/OutputPanel';
import { ShareButton } from './components/ShareButton';
import { useYjs } from './hooks/useYjs';
import { api } from './lib/api';
import { executeCode, supportsExecution } from './lib/executor';
import type { ProgrammingLanguage, ExecuteResult, Session } from './types';
import { DEFAULT_CODE } from './types';

function App() {
  // Session state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isCreatingSession, setIsCreatingSession] = useState(false);

  // Editor state
  const [language, setLanguage] = useState<ProgrammingLanguage>('python');
  const [code, setCode] = useState(DEFAULT_CODE.python);

  // Execution state
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<ExecuteResult | null>(null);

  // Yjs collaboration
  const {
    isConnected,
    isLoading: isYjsLoading,
    error: yjsError,
    participantsCount,
    bindEditor,
  } = useYjs({ sessionId, initialCode: code });

  // Check for session ID in URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlSessionId = params.get('session');

    if (urlSessionId) {
      // Load existing session
      api.getSession(urlSessionId)
        .then((sess) => {
          setSession(sess);
          setSessionId(sess.id);
          setLanguage(sess.language);
        })
        .catch((err) => {
          console.error('Failed to load session:', err);
          // Remove invalid session from URL
          window.history.replaceState({}, '', window.location.pathname);
        });
    }
  }, []);

  // Create a new session
  const handleCreateSession = useCallback(async () => {
    setIsCreatingSession(true);
    try {
      const newSession = await api.createSession({
        language,
        initial_code: code,
      });
      setSession(newSession);
      setSessionId(newSession.id);

      // Update URL
      const url = new URL(window.location.href);
      url.searchParams.set('session', newSession.id);
      window.history.pushState({}, '', url.toString());
    } catch (err) {
      console.error('Failed to create session:', err);
    } finally {
      setIsCreatingSession(false);
    }
  }, [language, code]);

  // Handle language change
  const handleLanguageChange = useCallback(
    async (newLanguage: ProgrammingLanguage) => {
      setLanguage(newLanguage);

      // Update code template if not connected to session
      if (!sessionId) {
        setCode(DEFAULT_CODE[newLanguage]);
      }

      // Update session if exists
      if (sessionId) {
        try {
          await api.updateSession(sessionId, { language: newLanguage });
        } catch (err) {
          console.error('Failed to update session language:', err);
        }
      }
    },
    [sessionId]
  );

  // Run code
  const handleRunCode = useCallback(async () => {
    if (!supportsExecution(language)) {
      setResult({
        success: false,
        output: '',
        error: `Browser execution not supported for ${language}. Only Python and JavaScript are available.`,
        error_type: 'unsupported',
      });
      return;
    }

    setIsRunning(true);
    setResult(null);

    try {
      const execResult = await executeCode(code, language);
      setResult(execResult);
    } catch (err: any) {
      setResult({
        success: false,
        output: '',
        error: err.message || 'Execution failed',
        error_type: 'runtime_error',
      });
    } finally {
      setIsRunning(false);
    }
  }, [code, language]);

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold">Collaborative Editor</h1>
          <LanguageSelector
            value={language}
            onChange={handleLanguageChange}
            disabled={isYjsLoading}
          />
        </div>

        <div className="flex items-center gap-3">
          {/* Connection status */}
          {sessionId && (
            <div className="flex items-center gap-2 text-sm">
              <div
                className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-yellow-500'
                }`}
              />
              <span className="text-gray-400">
                {isConnected ? 'Connected' : 'Connecting...'}
              </span>
              {participantsCount > 0 && (
                <span className="flex items-center gap-1 text-gray-400">
                  <Users className="w-4 h-4" />
                  {participantsCount}
                </span>
              )}
            </div>
          )}

          {/* Run button */}
          <button
            onClick={handleRunCode}
            disabled={isRunning}
            className="flex items-center gap-2 px-4 py-1.5 bg-green-600 hover:bg-green-700
                       text-white rounded text-sm font-medium transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunning ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run
              </>
            )}
          </button>

          {/* Share button */}
          <ShareButton
            sessionId={sessionId}
            onCreateSession={handleCreateSession}
            isCreating={isCreatingSession}
          />
        </div>
      </header>

      {/* Error banner */}
      {yjsError && (
        <div className="px-4 py-2 bg-red-900/50 border-b border-red-700 text-red-300 text-sm">
          {yjsError}
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex min-h-0">
        {/* Code editor */}
        <div className="flex-1 min-w-0">
          <CodeEditor
            language={language}
            onMount={bindEditor}
            onChange={(value) => setCode(value || '')}
          />
        </div>

        {/* Output panel */}
        <div className="w-96 border-l border-gray-700">
          <OutputPanel result={result} isRunning={isRunning} />
        </div>
      </div>
    </div>
  );
}

export default App;
