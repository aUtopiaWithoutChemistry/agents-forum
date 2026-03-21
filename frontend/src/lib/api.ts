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
  forum_highlights: PostRecord[];
};

type ArenaAgentDetailRecord = {
  agent: {
    id: string;
    name: string;
    description?: string | null;
  };
  account: {
    balance: number;
    nav: number;
    cumulative_return: number;
    exposure: number;
  };
  positions: Array<{
    symbol: string;
    quantity: number;
    average_cost: number;
    current_price: number;
    current_value: number;
    unrealized_pnl: number;
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

  getFeed: (skip = 0, limit = 20, categoryId?: number | null) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (categoryId) params.set('category_id', String(categoryId));
    return fetchWithError<PostRecord[]>(`/api/posts/feed?${params}`);
  },

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

// Market Data API
type MarketDataRecord = {
  ticker: string;
  name: string;
  market_type: string;
  price: number;
  volume: number;
  timestamp: string;
  change?: number;
  changePercent?: number;
};

type MarketHistoryRecord = {
  ticker: string;
  name: string;
  history: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
};

type MarketAlertRecord = {
  id: number;
  agent_id: string;
  ticker: string;
  target_price: number;
  direction: string;
  is_triggered: boolean;
  created_at: string;
  triggered_at?: string;
};

type MarketBatchRecord = {
  data: MarketDataRecord[];
  cached_count: number;
  fresh_count: number;
  timestamp: string;
};

export const marketApi = {
  getQuote: (ticker: string) =>
    fetchWithError<MarketDataRecord>(`/api/market/${ticker}`),

  getBatch: (tickers: string[], forceRefresh = false) =>
    fetchWithError<MarketBatchRecord>('/api/market/batch', {
      method: 'POST',
      body: JSON.stringify({ tickers, force_refresh: forceRefresh }),
    }),

  getHistory: (ticker: string, start: string, end: string) =>
    fetchWithError<MarketHistoryRecord>(`/api/market/${ticker}/history?start=${start}&end=${end}`),

  createAlert: (alert: { agent_id: string; ticker: string; target_price: number; direction: string }) =>
    fetchWithError<MarketAlertRecord>('/api/market/alerts', {
      method: 'POST',
      body: JSON.stringify(alert),
    }),

  getAlerts: (agentId: string) =>
    fetchWithError<MarketAlertRecord[]>(`/api/market/alerts?agent_id=${agentId}`),
};

// Trading API
type TradingAccountRecord = {
  id: number;
  agent_id: string;
  balance: number;
  created_at: string;
  updated_at: string;
};

type PositionRecord = {
  id: number;
  ticker: string;
  quantity: number;
  average_cost: number;
  current_value?: number;
  unrealized_pnl?: number;
};

type BalanceRecord = {
  agent_id: string;
  balance: number;
  positions: PositionRecord[];
  total_value: number;
};

type OrderRecord = {
  id: number;
  account_id: number;
  ticker: string;
  order_type: string;
  quantity: number;
  price: number;
  status: string;
  created_at: string;
  executed_at?: string;
  closed_at?: string;
};

export const tradingApi = {
  getAccount: (agentId: string) =>
    fetchWithError<TradingAccountRecord>(`/api/trading/account?agent_id=${agentId}`),

  getBalance: (agentId: string) =>
    fetchWithError<BalanceRecord>(`/api/trading/balance?agent_id=${agentId}`),

  getPositions: (agentId: string) =>
    fetchWithError<PositionRecord[]>(`/api/trading/positions?agent_id=${agentId}`),

  getOrders: (agentId: string, status?: string) => {
    const url = status
      ? `/api/trading/orders?agent_id=${agentId}&status=${status}`
      : `/api/trading/orders?agent_id=${agentId}`;
    return fetchWithError<OrderRecord[]>(url);
  },

  createOrder: (order: { agent_id: string; ticker: string; order_type: string; quantity: number }) =>
    fetchWithError<OrderRecord>('/api/trading/order', {
      method: 'POST',
      body: JSON.stringify(order),
    }),
};

// Audit API
type AuditLogRecord = {
  id: number;
  agent_id: string;
  action: string;
  target_type?: string;
  target_id?: number;
  details?: string;
  created_at: string;
};

export const auditApi = {
  getLogs: (params?: {
    agent_id?: string;
    action?: string;
    target_type?: string;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.agent_id) searchParams.append('agent_id', params.agent_id);
    if (params?.action) searchParams.append('action', params.action);
    if (params?.target_type) searchParams.append('target_type', params.target_type);
    if (params?.limit) searchParams.append('limit', String(params.limit));
    return fetchWithError<AuditLogRecord[]>(`/api/audit?${searchParams.toString()}`);
  },

  getActionTypes: () => fetchWithError<string[]>('/api/audit/actions'),
};
