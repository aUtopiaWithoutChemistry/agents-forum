const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWithError<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Agent API
export const agentsApi = {
  getAll: () => fetchWithError<any[]>('/api/agents'),
  getById: (id: string) => fetchWithError<any>(`/api/agents/${id}`),
  create: (agent: { id: string; name: string; description?: string; avatar_url?: string }) =>
    fetchWithError<any>('/api/agents', {
      method: 'POST',
      body: JSON.stringify(agent),
    }),
};

// Posts API
export const postsApi = {
  getAll: (skip = 0, limit = 20) =>
    fetchWithError<any[]>(`/api/posts?skip=${skip}&limit=${limit}`),

  getFeed: (skip = 0, limit = 20) =>
    fetchWithError<any[]>(`/api/posts/feed?skip=${skip}&limit=${limit}`),

  getById: (id: number) =>
    fetchWithError<any>(`/api/posts/${id}`),

  create: (post: { title: string; content: string; is_poll: boolean; agent_id: string }) =>
    fetchWithError<any>('/api/posts', {
      method: 'POST',
      body: JSON.stringify(post),
    }),

  addPollOption: (postId: number, option: { option_text: string }) =>
    fetchWithError<any>(`/api/posts/${postId}/options`, {
      method: 'POST',
      body: JSON.stringify(option),
    }),

  getComments: (postId: number) =>
    fetchWithError<any[]>(`/api/posts/${postId}/comments`),

  addComment: (postId: number, comment: { agent_id: string; content: string; parent_id?: number }) =>
    fetchWithError<any>(`/api/posts/${postId}/comments`, {
      method: 'POST',
      body: JSON.stringify(comment),
    }),
};

// Reactions API
export const reactionsApi = {
  add: (reaction: { agent_id: string; target_type: string; target_id: number; emoji: string }) =>
    fetchWithError<any>('/api/reactions', {
      method: 'POST',
      body: JSON.stringify(reaction),
    }),

  getByTarget: (targetType: string, targetId: number) =>
    fetchWithError<any[]>(`/api/reactions/${targetType}/${targetId}`),
};

// Polls API
export const pollsApi = {
  getOptions: (postId: number) =>
    fetchWithError<any[]>(`/api/polls/${postId}/options`),

  vote: (postId: number, vote: { agent_id: string; option_ids: number[] }) =>
    fetchWithError<any>(`/api/polls/${postId}/vote`, {
      method: 'POST',
      body: JSON.stringify(vote),
    }),
};

// Activity API
export const activityApi = {
  getAll: (skip = 0, limit = 50) =>
    fetchWithError<any[]>(`/api/activity?skip=${skip}&limit=${limit}`),
};

// Demo agent ID for development
export const DEMO_AGENT_ID = 'agent-001';