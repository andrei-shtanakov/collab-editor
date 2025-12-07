/**
 * API client for backend communication
 */

import type { Session, CreateSessionRequest } from '../types';

// In production, use VITE_API_URL env var; in dev, use relative path (proxied by Vite)
const API_BASE = import.meta.env.VITE_API_URL || '/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

export const api = {
  /**
   * Create a new coding session
   */
  createSession: (data?: CreateSessionRequest): Promise<Session> => {
    return request('/sessions', {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * Get session by ID
   */
  getSession: (sessionId: string): Promise<Session> => {
    return request(`/sessions/${sessionId}`);
  },

  /**
   * Update session (language, title)
   */
  updateSession: (
    sessionId: string,
    data: { language?: string; title?: string }
  ): Promise<Session> => {
    return request(`/sessions/${sessionId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete session
   */
  deleteSession: (sessionId: string): Promise<void> => {
    return request(`/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  },

  /**
   * List all sessions
   */
  listSessions: (limit = 50, offset = 0): Promise<{ sessions: Session[]; total: number }> => {
    return request(`/sessions?limit=${limit}&offset=${offset}`);
  },
};

export { ApiError };
