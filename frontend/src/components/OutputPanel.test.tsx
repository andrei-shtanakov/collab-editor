import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OutputPanel } from './OutputPanel';

describe('OutputPanel', () => {
  it('shows placeholder when no result', () => {
    render(<OutputPanel result={null} isRunning={false} />);

    expect(screen.getByText(/Click "Run" to execute/i)).toBeInTheDocument();
  });

  it('shows loading state when running', () => {
    render(<OutputPanel result={null} isRunning={true} />);

    expect(screen.getByText(/Running.../i)).toBeInTheDocument();
  });

  it('displays successful output', () => {
    render(
      <OutputPanel
        result={{
          success: true,
          output: 'Hello, World!',
          execution_time_ms: 42,
        }}
        isRunning={false}
      />
    );

    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    expect(screen.getByText('42ms')).toBeInTheDocument();
  });

  it('displays error output', () => {
    render(
      <OutputPanel
        result={{
          success: false,
          output: '',
          error: 'SyntaxError: invalid syntax',
          error_type: 'syntax_error',
        }}
        isRunning={false}
      />
    );

    expect(screen.getByText(/SyntaxError: invalid syntax/)).toBeInTheDocument();
    expect(screen.getByText(/\[syntax_error\]/)).toBeInTheDocument();
  });

  it('displays stderr output', () => {
    render(
      <OutputPanel
        result={{
          success: true,
          output: 'stdout',
          stderr: 'Warning: deprecated',
        }}
        isRunning={false}
      />
    );

    expect(screen.getByText('stdout')).toBeInTheDocument();
    expect(screen.getByText('Warning: deprecated')).toBeInTheDocument();
  });

  it('shows (No output) for empty successful execution', () => {
    render(
      <OutputPanel
        result={{
          success: true,
          output: '',
        }}
        isRunning={false}
      />
    );

    expect(screen.getByText('(No output)')).toBeInTheDocument();
  });
});
