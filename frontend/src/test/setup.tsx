import '@testing-library/jest-dom';

// Mock Monaco Editor (not available in jsdom)
vi.mock('@monaco-editor/react', () => ({
  default: ({ onMount }: { onMount?: (editor: unknown) => void }) => {
    // Simulate editor mount
    if (onMount) {
      const mockEditor = {
        getValue: () => '// test code',
        setValue: vi.fn(),
        getModel: () => ({}),
        updateOptions: vi.fn(),
      };
      setTimeout(() => onMount(mockEditor), 0);
    }
    return <div data-testid="monaco-editor">Monaco Editor Mock</div>;
  },
}));

// Mock y-websocket
vi.mock('y-websocket', () => ({
  WebsocketProvider: vi.fn().mockImplementation(() => ({
    awareness: {
      on: vi.fn(),
      setLocalState: vi.fn(),
      getStates: () => new Map(),
    },
    on: vi.fn(),
    destroy: vi.fn(),
  })),
}));

// Mock y-monaco
vi.mock('y-monaco', () => ({
  MonacoBinding: vi.fn().mockImplementation(() => ({
    destroy: vi.fn(),
  })),
}));
