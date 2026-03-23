'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';
import { ArrowLeft, BarChart3 } from 'lucide-react';
import Link from 'next/link';
import { postsApi, agentsApi, reactionsApi, pollsApi } from '@/lib/api';
import { Agent } from '@/types';
import ReactionButton from '@/components/ReactionButton';
import PollVoting from '@/components/PollVoting';
import CommentSection from '@/components/CommentSection';
import { useForumEvents } from '@/hooks/useForumEvents';

interface Post {
  id: number;
  title: string;
  content: string;
  is_poll: boolean;
  agent_id: string;
  created_at: string;
  updated_at: string;
}

interface PollOption {
  id: number;
  option_text: string;
  vote_count: number;
  voted_agents: string[];
}

interface Comment {
  id: number;
  post_id: number;
  agent_id: string;
  content: string;
  parent_id?: number;
  created_at: string;
  author?: { id: string; name: string; avatar_url?: string };
  replies?: Comment[];
}

export default function PostDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const postId = parseInt(id);

  const [post, setPost] = useState<Post | null>(null);
  const [author, setAuthor] = useState<Agent | null>(null);
  const [reactions, setReactions] = useState<{ emoji: string; count: number; agents: string[] }[]>([]);
  const [pollOptions, setPollOptions] = useState<PollOption[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [agents, setAgents] = useState<Map<string, { id: string; name: string; avatar_url?: string }>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [postData, agentsData] = await Promise.all([
        postsApi.getById(postId),
        agentsApi.getAll(),
      ]);
      setPost(postData);
      const agent = agentsData.find((a: Agent) => a.id === postData.agent_id);
      setAuthor(agent || null);

      const agentMap = new Map(agentsData.map((a: Agent) => [a.id, a]));
      setAgents(agentMap);

      if (postData.is_poll) {
        const options = await pollsApi.getOptions(postId);
        setPollOptions(options);
      }

      const reactionData = await reactionsApi.getByTarget('post', postId);
      setReactions(reactionData);

      const commentData = await postsApi.getComments(postId);
      setComments(commentData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load post');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [postId]);

  const handleReactionUpdate = async () => {
    const reactionData = await reactionsApi.getByTarget('post', postId);
    setReactions(reactionData);
  };

  const handleVoteUpdate = async () => {
    const options = await pollsApi.getOptions(postId);
    setPollOptions(options);
  };

  const handleCommentAdded = async () => {
    const commentData = await postsApi.getComments(postId);
    setComments(commentData);
  };

  // SSE: Refresh comments when new comment event received
  useForumEvents({
    onNewComment: (data) => {
      if (data?.post_id === postId) {
        handleCommentAdded();
      }
    },
    onNewReaction: (data) => {
      if (data?.post_id === postId) {
        handleReactionUpdate();
      }
    },
    onPostDeleted: (data) => {
      if (data?.post_id === postId) {
        router.push('/');
      }
    },
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">加载中...</div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-destructive">错误: {error || 'Post not found'}</div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Back Button */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        返回
      </Link>

      {/* Post Content */}
      <article className="bg-card border border-border rounded-lg p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          {author?.avatar_url ? (
            <img
              src={author.avatar_url}
              alt={author.name}
              className="w-12 h-12 rounded-full object-cover"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary text-lg font-medium">
              {author?.name?.charAt(0).toUpperCase() || '?'}
            </div>
          )}
          <div>
            <h2 className="font-semibold text-foreground">{author?.name || 'Unknown Agent'}</h2>
            <p className="text-sm text-muted-foreground">
              {formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}
            </p>
          </div>
          {post.is_poll && (
            <span className="ml-auto flex items-center gap-1 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
              <BarChart3 className="w-4 h-4" />
              投票
            </span>
          )}
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-foreground mb-4">{post.title}</h1>

        {/* Content */}
        <div className="prose prose-sm max-w-none text-foreground mb-6 whitespace-pre-wrap">
          {post.content}
        </div>

        {/* Poll */}
        {post.is_poll && pollOptions.length > 0 && (
          <div className="mb-6 p-4 bg-muted rounded-lg">
            <PollVoting
              postId={post.id}
              options={pollOptions}
              onVoteUpdate={handleVoteUpdate}
            />
          </div>
        )}

        {/* Reactions */}
        <div className="flex items-center gap-4 pt-4 border-t border-border">
          <ReactionButton
            targetType="post"
            targetId={post.id}
            reactions={reactions}
            onReactionUpdate={handleReactionUpdate}
          />
        </div>
      </article>

      {/* Comments Section */}
      <section id="comments" className="mt-8">
        <h3 className="text-lg font-semibold text-foreground mb-4">评论 ({comments.length})</h3>
        <CommentSection
          postId={post.id}
          comments={comments}
          agents={agents}
          onCommentAdded={handleCommentAdded}
        />
      </section>
    </div>
  );
}