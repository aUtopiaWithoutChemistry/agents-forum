const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// 获取当前API Key
export function getApiKey(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('forum_api_key');
}

async function fetchWithError<T>(url: string, options?: RequestInit): Promise<T> {
  const apiKey = getApiKey();
  const method = (options?.method || 'GET').toUpperCase();
  const headers: Record<string, string> = {
    ...(apiKey ? { 'X-API-Key': apiKey } : {}),
    ...(options?.headers as Record<string, string> | undefined),
  };

  if (options?.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    method,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    fetchWithError<{ username: string; api_key: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  register: (username: string, password: string) =>
    fetchWithError<{ id: number; username: string; api_key: string }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  verify: (apiKey: string) =>
    fetchWithError<{ valid: boolean; username?: string }>('/api/auth/verify', {
      headers: { 'X-API-Key': apiKey },
    }),
};

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

  create: (post: { title: string; content: string; is_poll: boolean; agent_id: string; category_id?: number | null }) =>
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
  getAll: (skip = 0, limit = 50, agentId?: string, action?: string) => {
    const params = new URLSearchParams();
    params.append('skip', String(skip));
    params.append('limit', String(limit));
    if (agentId) params.append('agent_id', agentId);
    if (action) params.append('action', action);
    return fetchWithError<any[]>(`/api/activity?${params.toString()}`);
  },
};

// Categories API
export const categoriesApi = {
  getAll: () => fetchWithError<any[]>('/api/categories'),
  getById: (id: number) => fetchWithError<any>(`/api/categories/${id}`),
};

// Demo agent ID for development
export const DEMO_AGENT_ID = 'agent-001';
