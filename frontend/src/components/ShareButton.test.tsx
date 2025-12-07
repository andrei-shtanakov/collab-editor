import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ShareButton } from './ShareButton';

describe('ShareButton', () => {
  it('shows create button when no session', () => {
    render(
      <ShareButton
        sessionId={null}
        onCreateSession={() => Promise.resolve()}
      />
    );

    expect(screen.getByText('Create & Share')).toBeInTheDocument();
  });

  it('shows loading state when creating', () => {
    render(
      <ShareButton
        sessionId={null}
        onCreateSession={() => Promise.resolve()}
        isCreating={true}
      />
    );

    expect(screen.getByText('Creating...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('calls onCreateSession when clicked', () => {
    const handleCreate = vi.fn(() => Promise.resolve());
    render(
      <ShareButton
        sessionId={null}
        onCreateSession={handleCreate}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    expect(handleCreate).toHaveBeenCalled();
  });

  it('shows session ID when session exists', () => {
    render(
      <ShareButton
        sessionId="abc123"
        onCreateSession={() => Promise.resolve()}
      />
    );

    expect(screen.getByText('abc123')).toBeInTheDocument();
    expect(screen.getByText('Copy Link')).toBeInTheDocument();
  });

  it('copies link to clipboard when copy clicked', async () => {
    // Mock clipboard
    const writeText = vi.fn(() => Promise.resolve());
    Object.assign(navigator, {
      clipboard: { writeText },
    });

    render(
      <ShareButton
        sessionId="abc123"
        onCreateSession={() => Promise.resolve()}
      />
    );

    fireEvent.click(screen.getByText('Copy Link'));

    expect(writeText).toHaveBeenCalledWith(
      expect.stringContaining('session=abc123')
    );
  });
});
