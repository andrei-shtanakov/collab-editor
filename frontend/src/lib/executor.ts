/**
 * Code executors for browser-side execution using WebAssembly.
 * 
 * Supports:
 * - Python via Pyodide
 * - JavaScript via eval (sandboxed)
 */

import type { ExecuteResult, ProgrammingLanguage } from '../types';

// Pyodide instance (lazy loaded)
let pyodideInstance: any = null;
let pyodideLoading: Promise<any> | null = null;

/**
 * Load Pyodide (Python WASM runtime)
 */
async function loadPyodide(): Promise<any> {
  if (pyodideInstance) {
    return pyodideInstance;
  }

  if (pyodideLoading) {
    return pyodideLoading;
  }

  pyodideLoading = (async () => {
    // Load Pyodide from CDN
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js';
    document.head.appendChild(script);

    await new Promise<void>((resolve, reject) => {
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Pyodide'));
    });

    // Initialize Pyodide
    // @ts-expect-error - loadPyodide is loaded from CDN
    pyodideInstance = await window.loadPyodide({
      indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/',
    });

    return pyodideInstance;
  })();

  return pyodideLoading;
}

/**
 * Execute Python code using Pyodide
 */
async function executePython(code: string): Promise<ExecuteResult> {
  const startTime = performance.now();

  try {
    const pyodide = await loadPyodide();

    // Redirect stdout/stderr
    pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
sys.stderr = StringIO()
    `);

    // Execute the code
    try {
      pyodide.runPython(code);
    } catch (e: any) {
      const stderr = pyodide.runPython('sys.stderr.getvalue()');
      return {
        success: false,
        output: '',
        stderr: stderr || e.message,
        error: e.message,
        error_type: 'runtime_error',
        execution_time_ms: Math.round(performance.now() - startTime),
      };
    }

    // Get output
    const stdout = pyodide.runPython('sys.stdout.getvalue()');
    const stderr = pyodide.runPython('sys.stderr.getvalue()');

    return {
      success: true,
      output: stdout,
      stderr: stderr,
      execution_time_ms: Math.round(performance.now() - startTime),
    };
  } catch (error: any) {
    return {
      success: false,
      output: '',
      error: error.message,
      error_type: 'runtime_error',
      execution_time_ms: Math.round(performance.now() - startTime),
    };
  }
}

/**
 * Execute JavaScript code in a sandboxed environment
 */
async function executeJavaScript(code: string): Promise<ExecuteResult> {
  const startTime = performance.now();
  const logs: string[] = [];

  try {
    // Create sandboxed console
    const sandboxConsole = {
      log: (...args: any[]) => logs.push(args.map(String).join(' ')),
      error: (...args: any[]) => logs.push('[ERROR] ' + args.map(String).join(' ')),
      warn: (...args: any[]) => logs.push('[WARN] ' + args.map(String).join(' ')),
      info: (...args: any[]) => logs.push(args.map(String).join(' ')),
    };

    // Create a sandboxed function
    const sandboxedCode = `
      "use strict";
      const console = __console__;
      ${code}
    `;

    // Execute with timeout
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Execution timeout (10s)')), 10000);
    });

    const executePromise = new Promise<void>((resolve, reject) => {
      try {
        const fn = new Function('__console__', sandboxedCode);
        fn(sandboxConsole);
        resolve();
      } catch (e) {
        reject(e);
      }
    });

    await Promise.race([executePromise, timeoutPromise]);

    return {
      success: true,
      output: logs.join('\n'),
      stderr: '',
      execution_time_ms: Math.round(performance.now() - startTime),
    };
  } catch (error: any) {
    return {
      success: false,
      output: logs.join('\n'),
      error: error.message,
      error_type: error.name === 'SyntaxError' ? 'syntax_error' : 'runtime_error',
      execution_time_ms: Math.round(performance.now() - startTime),
    };
  }
}

/**
 * Execute code based on language
 */
export async function executeCode(
  code: string,
  language: ProgrammingLanguage
): Promise<ExecuteResult> {
  switch (language) {
    case 'python':
      return executePython(code);
    case 'javascript':
    case 'typescript': // TypeScript runs as JS (no type checking)
      return executeJavaScript(code);
    default:
      return {
        success: false,
        output: '',
        error: `Language "${language}" is not supported for browser execution. Use Python or JavaScript.`,
        error_type: 'runtime_error',
      };
  }
}

/**
 * Check if a language supports browser execution
 */
export function supportsExecution(language: ProgrammingLanguage): boolean {
  return ['python', 'javascript', 'typescript'].includes(language);
}
