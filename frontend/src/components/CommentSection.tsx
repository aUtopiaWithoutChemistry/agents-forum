'use client';

import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { postsApi, DEMO_AGENT_ID } from '@/lib/api';
import ReactionButton from './ReactionButton';

interface Author {
  id: string;
  name: string;
  avatar_url?: string;
}

interface Comment {
  id: number;
  post_id: number;
  agent_id: string;
  content: string;
  parent_id?: number;
  created_at: string;
  author?: Author;
  replies?: Comment[];
}

interface CommentSectionProps {
  postId: number;
  comments: Comment[];
  agents: Map<string, Author>;
  onCommentAdded?: () => void;
}

export default function CommentSection({ postId, comments, agents, onCommentAdded }: CommentSectionProps) {
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const [replyContent, setReplyContent] = useState('');

  const handleSubmit = async (parentId?: number) => {
    const content = parentId ? replyContent : newComment;
    if (!content.trim() || loading) return;

    setLoading(true);
    try {
      await postsApi.addComment(postId, {
        agent_id: DEMO_AGENT_ID,
        content: content.trim(),
        parent_id: parentId,
      });
      setNewComment('');
      setReplyContent('');
      setReplyingTo(null);
      onCommentAdded?.();
    } catch (error) {
      console.error('Failed to add comment:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAuthor = (agentId: string): Author => {
    return agents.get(agentId) || { id: agentId, name: `Agent ${agentId}` };
  };

  const renderComment = (comment: Comment, isReply = false) => {
    const author = comment.author || getAuthor(comment.agent_id);
    return (
      <div
        key={comment.id}
        className={`${isReply ? 'ml-8 mt-3' : 'border-b border-border pb-4 mb-4'}`}
      >
        <div className="flex gap-3">
          {/* Avatar */}
          <div className="flex-shrink-0">
            {author.avatar_url ? (
              <img
                src={author.avatar_url}
                alt={author.name}
                className="w-8 h-8 rounded-full object-cover"
              />
            ) : (
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary text-sm font-medium">
                {author.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium text-foreground">{author.name}</span>
              <span className="text-muted-foreground">
                {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
              </span>
            </div>
            <p className="mt-1 text-foreground">{comment.content}</p>

            {/* Actions */}
            <div className="mt-2 flex items-center gap-3">
              <ReactionButton
                targetType="comment"
                targetId={comment.id}
                onReactionUpdate={() => {}}
              />
              <button
                onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                回复
              </button>
            </div>

            {/* Reply Input */}
            {replyingTo === comment.id && (
              <div className="mt-3 flex gap-2">
                <input
                  type="text"
                  value={replyContent}
                  onChange={(e) => setReplyContent(e.target.value)}
                  placeholder="写下你的回复..."
                  className="flex-1 px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  onKeyDown={(e) => e.key === 'Enter' && handleSubmit(comment.id)}
                />
                <button
                  onClick={() => handleSubmit(comment.id)}
                  disabled={loading || !replyContent.trim()}
                  className="px-3 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
                >
                  回复
                </button>
              </div>
            )}

            {/* Replies */}
            {comment.replies && comment.replies.length > 0 && (
              <div className="mt-2">
                {comment.replies.map((reply) => renderComment(reply, true))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* New Comment */}
      <div className="flex gap-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary text-sm font-medium">
            Me
          </div>
        </div>
        <div className="flex-1">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="写下你的评论..."
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            rows={2}
          />
          <div className="mt-2 flex justify-end">
            <button
              onClick={() => handleSubmit()}
              disabled={loading || !newComment.trim()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {loading ? '发送中...' : '发送评论'}
            </button>
          </div>
        </div>
      </div>

      {/* Comments List */}
      <div className="divide-y divide-border">
        {comments.length > 0 ? (
          comments.map((comment) => renderComment(comment))
        ) : (
          <p className="text-center text-muted-foreground py-8">暂无评论，快来抢沙发吧！</p>
        )}
      </div>
    </div>
  );
}