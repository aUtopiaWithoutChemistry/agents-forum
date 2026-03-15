// Types for the Agents Forum application

// User (for admin)
export interface User {
  id: number;
  username: string;
  api_key: string;
  is_active: boolean;
  created_at: string;
}

// Category
export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  color: string;
  created_at: string;
}

// Agent
export interface Agent {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  created_at: string;
}

export interface AgentCreate {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
}

// Post
export interface Post {
  id: number;
  title: string;
  content: string;
  is_poll: boolean;
  agent_id: string;
  category_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface PostCreate {
  title: string;
  content: string;
  is_poll: boolean;
  agent_id: string;
  category_id?: number | null;
}

// Comment
export interface Comment {
  id: number;
  post_id: number;
  agent_id: string;
  content: string;
  parent_id?: number;
  created_at: string;
  author?: Agent;
  replies?: Comment[];
}

// Reaction
export interface Reaction {
  id: number;
  target_type: string;
  target_id: number;
  agent_id: string;
  emoji: string;
  created_at: string;
}

export interface ReactionGroup {
  emoji: string;
  count: number;
  agents: string[];
}

// Poll
export interface PollOption {
  id: number;
  option_text: string;
  vote_count: number;
  voted_agents: string[];
}

export interface PollVoteCreate {
  agent_id: string;
  option_ids: number[];
}

// Activity
export interface ActivityLog {
  id: number;
  agent_id: string;
  action: string;
  target_type?: string | null;
  target_id?: number | null;
  extra_data?: string | null;
  created_at: string;
}

// API Response types
export interface PostWithDetails extends Post {
  author: Agent;
  reactions: ReactionGroup[];
  poll_options: PollOption[];
}