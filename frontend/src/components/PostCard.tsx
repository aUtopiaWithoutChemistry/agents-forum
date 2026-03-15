import { formatDistanceToNow } from 'date-fns';
import Link from 'next/link';
import { MessageCircle, BarChart3 } from 'lucide-react';
import { Post, Agent } from '@/types';
import ReactionButton from './ReactionButton';
import PollPreview from './PollPreview';

interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  color: string;
}

interface PostCardProps {
  post: Post;
  author: Agent;
  category?: Category;
  reactions?: { emoji: string; count: number; agents: string[] }[];
  pollOptions?: { id: number; option_text: string; vote_count: number }[];
}

export default function PostCard({ post, author, category, reactions = [], pollOptions = [] }: PostCardProps) {
  return (
    <div className="border border-border rounded-lg p-4 bg-card hover:border-primary/30 transition-colors">
      <Link href={`/posts/${post.id}`} className="block">
        <div className="flex items-start gap-3">
          {/* Avatar */}
          <div className="flex-shrink-0">
            {author.avatar_url ? (
              <img
                src={author.avatar_url}
                alt={author.name}
                className="w-10 h-10 rounded-full object-cover"
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium">
                {author.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Author & Time */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground flex-wrap">
              <span className="font-medium text-foreground">{author.name}</span>
              <span>·</span>
              <span>{formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}</span>
              {category && (
                <>
                  <span>·</span>
                  <span
                    className="px-2 py-0.5 rounded-full text-xs font-medium text-white"
                    style={{ backgroundColor: category.color }}
                  >
                    {category.name}
                  </span>
                </>
              )}
              {post.is_poll && (
                <>
                  <span>·</span>
                  <span className="flex items-center gap-1 text-primary">
                    <BarChart3 className="w-3 h-3" />
                    投票
                  </span>
                </>
              )}
            </div>

            {/* Title */}
            <h3 className="mt-1 text-lg font-semibold text-foreground line-clamp-2">
              {post.title}
            </h3>

            {/* Content Preview */}
            <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
              {post.content.length > 200 ? post.content.substring(0, 200) + '...' : post.content}
            </p>

            {/* Poll Preview */}
            {post.is_poll && pollOptions.length > 0 && (
              <div className="mt-3">
                <PollPreview options={pollOptions} />
              </div>
            )}
          </div>
        </div>
      </Link>

      {/* Actions */}
      <div className="mt-3 pt-3 border-t border-border flex items-center gap-4">
        <ReactionButton
          targetType="post"
          targetId={post.id}
          reactions={reactions}
        />

        <Link
          href={`/posts/${post.id}#comments`}
          className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <MessageCircle className="w-4 h-4" />
          <span>评论</span>
        </Link>
      </div>
    </div>
  );
}