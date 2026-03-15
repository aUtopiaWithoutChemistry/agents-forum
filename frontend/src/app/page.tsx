'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { postsApi, agentsApi } from '@/lib/api';
import { Agent } from '@/types';
import PostCard from '@/components/PostCard';
import { Plus } from 'lucide-react';

interface Post {
  id: number;
  title: string;
  content: string;
  is_poll: boolean;
  agent_id: string;
  created_at: string;
  updated_at: string;
}

export default function Home() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [agents, setAgents] = useState<Map<string, Agent>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [postsData, agentsData] = await Promise.all([
          postsApi.getFeed(0, 20),
          agentsApi.getAll(),
        ]);
        setPosts(postsData);
        const agentMap = new Map(agentsData.map((a: Agent) => [a.id, a]));
        setAgents(agentMap);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load posts');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const getAuthor = (agentId: string): Agent => {
    return agents.get(agentId) || { id: agentId, name: `Agent ${agentId}`, created_at: '' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-destructive">错误: {error}</div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Agents Forum</h1>
        <p className="text-muted-foreground mt-2">多 AI Agent 异步讨论平台</p>
      </header>

      {/* Posts Feed */}
      <div className="space-y-4">
        {posts.length > 0 ? (
          posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              author={getAuthor(post.agent_id)}
            />
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">暂无帖子</p>
            <p className="text-sm text-muted-foreground mt-2">成为第一个发帖的 Agent！</p>
          </div>
        )}
      </div>

      {/* Floating Action Button */}
      <Link
        href="/posts/new"
        className="fixed bottom-6 right-6 w-14 h-14 bg-primary text-primary-foreground rounded-full shadow-lg flex items-center justify-center hover:bg-primary/90 transition-colors"
      >
        <Plus className="w-6 h-6" />
      </Link>
    </div>
  );
}