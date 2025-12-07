/**
 * Monaco Code Editor with Yjs collaboration
 */

import { useRef, useCallback } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import type { ProgrammingLanguage } from '../types';
import { LANGUAGE_MAP } from '../types';

interface CodeEditorProps {
  language: ProgrammingLanguage;
  onMount?: (editor: editor.IStandaloneCodeEditor) => void;
  onChange?: (value: string | undefined) => void;
  readOnly?: boolean;
}

export function CodeEditor({
  language,
  onMount,
  onChange,
  readOnly = false,
}: CodeEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleEditorMount: OnMount = useCallback(
    (editor) => {
      editorRef.current = editor;

      // Configure editor options
      editor.updateOptions({
        fontSize: 14,
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        lineNumbers: 'on',
        renderLineHighlight: 'all',
        tabSize: 4,
        insertSpaces: true,
        automaticLayout: true,
        wordWrap: 'on',
        readOnly,
      });

      // Notify parent
      onMount?.(editor);
    },
    [onMount, readOnly]
  );

  const handleChange = useCallback(
    (value: string | undefined) => {
      onChange?.(value);
    },
    [onChange]
  );

  return (
    <Editor
      height="100%"
      language={LANGUAGE_MAP[language]}
      theme="vs-dark"
      onMount={handleEditorMount}
      onChange={handleChange}
      options={{
        readOnly,
        fontSize: 14,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
      }}
      loading={
        <div className="flex items-center justify-center h-full bg-gray-900 text-gray-400">
          Loading editor...
        </div>
      }
    />
  );
}
