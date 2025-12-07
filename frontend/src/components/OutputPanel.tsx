/**
 * Output panel for code execution results
 */

import { Terminal, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import type { ExecuteResult } from '../types';

interface OutputPanelProps {
  result: ExecuteResult | null;
  isRunning: boolean;
}

export function OutputPanel({ result, isRunning }: OutputPanelProps) {
  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-800 border-b border-gray-700">
        <Terminal className="w-4 h-4 text-gray-400" />
        <span className="text-sm font-medium text-gray-300">Output</span>
        
        {result && (
          <div className="flex items-center gap-2 ml-auto text-xs">
            {result.success ? (
              <CheckCircle className="w-3.5 h-3.5 text-green-500" />
            ) : (
              <AlertCircle className="w-3.5 h-3.5 text-red-500" />
            )}
            {result.execution_time_ms !== undefined && (
              <span className="text-gray-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {result.execution_time_ms}ms
              </span>
            )}
          </div>
        )}
      </div>

      {/* Output content */}
      <div className="flex-1 overflow-auto p-3 font-mono text-sm">
        {isRunning ? (
          <div className="flex items-center gap-2 text-gray-400">
            <div className="w-4 h-4 border-2 border-gray-500 border-t-blue-500 rounded-full animate-spin" />
            Running...
          </div>
        ) : result ? (
          <div>
            {/* stdout */}
            {result.output && (
              <pre className="text-green-400 whitespace-pre-wrap">{result.output}</pre>
            )}
            
            {/* stderr */}
            {result.stderr && (
              <pre className="text-yellow-400 whitespace-pre-wrap mt-2">
                {result.stderr}
              </pre>
            )}
            
            {/* Error */}
            {result.error && (
              <pre className="text-red-400 whitespace-pre-wrap mt-2">
                {result.error_type && (
                  <span className="text-red-500">[{result.error_type}] </span>
                )}
                {result.error}
              </pre>
            )}
            
            {/* Empty output */}
            {!result.output && !result.stderr && !result.error && (
              <span className="text-gray-500">
                (No output)
              </span>
            )}
          </div>
        ) : (
          <span className="text-gray-500">
            Click "Run" to execute your code
          </span>
        )}
      </div>
    </div>
  );
}
