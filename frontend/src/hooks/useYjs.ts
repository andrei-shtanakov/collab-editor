/**
 * Hook for Yjs synchronization with Monaco editor
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import type { editor } from 'monaco-editor';
import { MonacoBinding } from 'y-monaco';

interface UseYjsOptions {
  sessionId: string | null;
  initialCode?: string;
}

interface UseYjsReturn {
  doc: Y.Doc | null;
  provider: WebsocketProvider | null;
  binding: MonacoBinding | null;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  participantsCount: number;
  bindEditor: (editor: editor.IStandaloneCodeEditor) => void;
}

export function useYjs({ sessionId, initialCode = '' }: UseYjsOptions): UseYjsReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [participantsCount, setParticipantsCount] = useState(0);

  const docRef = useRef<Y.Doc | null>(null);
  const providerRef = useRef<WebsocketProvider | null>(null);
  const bindingRef = useRef<MonacoBinding | null>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  // Cleanup function
  const cleanup = useCallback(() => {
    if (bindingRef.current) {
      bindingRef.current.destroy();
      bindingRef.current = null;
    }
    if (providerRef.current) {
      providerRef.current.destroy();
      providerRef.current = null;
    }
    if (docRef.current) {
      docRef.current.destroy();
      docRef.current = null;
    }
    setIsConnected(false);
    setParticipantsCount(0);
  }, []);

  // Initialize Yjs when sessionId changes
  useEffect(() => {
    if (!sessionId) {
      cleanup();
      return;
    }

    setIsLoading(true);
    setError(null);

    // Create Yjs document
    const doc = new Y.Doc();
    docRef.current = doc;

    // Get the shared text type
    const yText = doc.getText('monaco');

    // Set initial code if document is empty and we have initial code
    if (yText.length === 0 && initialCode) {
      yText.insert(0, initialCode);
    }

    // Determine WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host;
    const wsUrl = `${wsProtocol}//${wsHost}/ws/${sessionId}`;

    // Create WebSocket provider
    const provider = new WebsocketProvider(wsUrl, sessionId, doc, {
      connect: true,
    });
    providerRef.current = provider;

    // Connection status handlers
    provider.on('status', (event: { status: string }) => {
      setIsConnected(event.status === 'connected');
      setIsLoading(event.status === 'connecting');
    });

    // Awareness (participants count)
    provider.awareness.on('change', () => {
      const states = provider.awareness.getStates();
      setParticipantsCount(states.size);
    });

    // Set local awareness state
    provider.awareness.setLocalState({
      user: {
        name: `User-${Math.random().toString(36).substring(2, 6)}`,
        color: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
      },
    });

    // Handle connection errors
    provider.on('connection-error', (event: Event) => {
      console.error('WebSocket connection error:', event);
      setError('Failed to connect to collaboration server');
      setIsLoading(false);
    });

    provider.on('connection-close', (event: CloseEvent) => {
      if (event.code === 4004) {
        setError('Session not found');
      }
      setIsConnected(false);
    });

    // If editor is already mounted, bind it
    if (editorRef.current) {
      const binding = new MonacoBinding(
        yText,
        editorRef.current.getModel()!,
        new Set([editorRef.current]),
        provider.awareness
      );
      bindingRef.current = binding;
    }

    return cleanup;
  }, [sessionId, initialCode, cleanup]);

  // Function to bind Monaco editor
  const bindEditor = useCallback((editor: editor.IStandaloneCodeEditor) => {
    editorRef.current = editor;

    // If Yjs is already initialized, create binding
    if (docRef.current && providerRef.current) {
      const yText = docRef.current.getText('monaco');

      // Destroy existing binding
      if (bindingRef.current) {
        bindingRef.current.destroy();
      }

      const binding = new MonacoBinding(
        yText,
        editor.getModel()!,
        new Set([editor]),
        providerRef.current.awareness
      );
      bindingRef.current = binding;
    }
  }, []);

  return {
    doc: docRef.current,
    provider: providerRef.current,
    binding: bindingRef.current,
    isConnected,
    isLoading,
    error,
    participantsCount,
    bindEditor,
  };
}
