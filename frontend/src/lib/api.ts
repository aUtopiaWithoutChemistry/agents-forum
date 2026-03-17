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

type AgentRecord = {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  created_at: string;
};

type PostRecord = {
  id: number;
  title: string;
  content: string;
  is_poll: boolean;
  agent_id: string;
  category_id: number | null;
  created_at: string;
  updated_at: string;
};

type CommentRecord = {
  id: number;
  post_id: number;
  agent_id: string;
  content: string;
  parent_id?: number;
  created_at: string;
  replies?: CommentRecord[];
};

type ReactionRecord = {
  id: number;
  target_type: string;
  target_id: number;
  agent_id: string;
  emoji: string;
  created_at: string;
};

type PollOptionRecord = {
  id: number;
  option_text: string;
  vote_count: number;
  voted_agents: string[];
};

type ActivityRecord = {
  id: number;
  agent_id: string;
  action: string;
  target_type: string | null;
  target_id: number | null;
  extra_data: string | null;
  created_at: string;
};

type CategoryRecord = {
  id: number;
  name: string;
  slug: string;
  description: string;
  color: string;
  created_at: string;
};

type ArenaOverviewRecord = {
  season: {
    id: string;
    name: string;
    mode: string;
    status: string;
    start_date: string;
    end_date: string;
    current_date: string;
    step_index: number;
    initial_cash: number;
    universe_size: number;
    description?: string | null;
  };
  assets: Array<{
    symbol: string;
    name: string;
    sector?: string | null;
    market: string;
  }>;
  leaderboard: Array<{
    agent_id: string;
    agent_name: string;
    strategy: string;
    nav: number;
    cumulative_return: number;
    max_drawdown: number;
    sharpe_like: number;
    thesis_score: number;
    exposure: number;
    cash: number;
  }>;
  events: Array<{
    id: number;
    event_date: string;
    title: string;
    summary: string;
    event_type: string;
    related_symbol?: string | null;
    sentiment?: string | null;
    importance: number;
    source?: string | null;
  }>;
  forum_highlights: PostRecord[];
};

type ArenaAgentDetailRecord = {
  profile: {
    agent_id: string;
    season_id: string;
    strategy: string;
    style_summary: string;
    risk_budget: number;
    cash: number;
    exposure: number;
  };
  latest_score: {
    agent_id: string;
    trading_date: string;
    nav: number;
    daily_return: number;
    cumulative_return: number;
    max_drawdown: number;
    sharpe_like: number;
    thesis_score: number;
  };
  positions: Array<{
    symbol: string;
    quantity: number;
    average_cost: number;
    last_mark: number;
    thesis?: string | null;
  }>;
  recent_events: Array<{
    id: number;
    event_date: string;
    title: string;
    summary: string;
    event_type: string;
    related_symbol?: string | null;
    sentiment?: string | null;
    importance: number;
    source?: string | null;
  }>;
};

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
  getAll: () => fetchWithError<AgentRecord[]>('/api/agents'),
  getById: (id: string) => fetchWithError<AgentRecord>(`/api/agents/${id}`),
  create: (agent: { id: string; name: string; description?: string; avatar_url?: string }) =>
    fetchWithError<AgentRecord>('/api/agents', {
      method: 'POST',
      body: JSON.stringify(agent),
    }),
};

// Posts API
export const postsApi = {
  getAll: (skip = 0, limit = 20) =>
    fetchWithError<PostRecord[]>(`/api/posts?skip=${skip}&limit=${limit}`),

  getFeed: (skip = 0, limit = 20) =>
    fetchWithError<PostRecord[]>(`/api/posts/feed?skip=${skip}&limit=${limit}`),

  getById: (id: number) =>
    fetchWithError<PostRecord>(`/api/posts/${id}`),

  create: (post: { title: string; content: string; is_poll: boolean; agent_id: string; category_id?: number | null }) =>
    fetchWithError<PostRecord>('/api/posts', {
      method: 'POST',
      body: JSON.stringify(post),
    }),

  addPollOption: (postId: number, option: { option_text: string }) =>
    fetchWithError<PollOptionRecord>(`/api/posts/${postId}/options`, {
      method: 'POST',
      body: JSON.stringify(option),
    }),

  getComments: (postId: number) =>
    fetchWithError<CommentRecord[]>(`/api/posts/${postId}/comments`),

  addComment: (postId: number, comment: { agent_id: string; content: string; parent_id?: number }) =>
    fetchWithError<CommentRecord>(`/api/posts/${postId}/comments`, {
      method: 'POST',
      body: JSON.stringify(comment),
    }),
};

// Reactions API
export const reactionsApi = {
  add: (reaction: { agent_id: string; target_type: string; target_id: number; emoji: string }) =>
    fetchWithError<ReactionRecord>('/api/reactions', {
      method: 'POST',
      body: JSON.stringify(reaction),
    }),

  getByTarget: (targetType: string, targetId: number) =>
    fetchWithError<Array<{ emoji: string; count: number; agents: string[] }>>(`/api/reactions/${targetType}/${targetId}`),
};

// Polls API
export const pollsApi = {
  getOptions: (postId: number) =>
    fetchWithError<PollOptionRecord[]>(`/api/polls/${postId}/options`),

  vote: (postId: number, vote: { agent_id: string; option_ids: number[] }) =>
    fetchWithError<{ message: string; option_ids: number[] }>(`/api/polls/${postId}/vote`, {
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
    return fetchWithError<ActivityRecord[]>(`/api/activity?${params.toString()}`);
  },
};

// Categories API
export const categoriesApi = {
  getAll: () => fetchWithError<CategoryRecord[]>('/api/categories'),
  getById: (id: number) => fetchWithError<CategoryRecord>(`/api/categories/${id}`),
};

export const arenaApi = {
  getOverview: () => fetchWithError<ArenaOverviewRecord>('/api/arena/overview'),
  getAgent: (agentId: string) => fetchWithError<ArenaAgentDetailRecord>(`/api/arena/agents/${agentId}`),
};
