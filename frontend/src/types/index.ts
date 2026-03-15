// Types for the Agents Forum application

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
  created_at: string;
  updated_at: string;
}

export interface PostCreate {
  title: string;
  content: string;
  is_poll: boolean;
  agent_id: string;
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
  target_type?: string;
  target_id?: number;
  metadata?: string;
  created_at: string;
}

// API Response types
export interface PostWithDetails extends Post {
  author: Agent;
  reactions: ReactionGroup[];
  poll_options: PollOption[];
}