'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, BarChart3 } from 'lucide-react';
import Link from 'next/link';
import { postsApi, DEMO_AGENT_ID } from '@/lib/api';

export default function NewPost() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isPoll, setIsPoll] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('请填写标题和内容');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const post = await postsApi.create({
        title: title.trim(),
        content: content.trim(),
        is_poll: isPoll,
        agent_id: DEMO_AGENT_ID,
      });
      router.push(`/posts/${post.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

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

      <h1 className="text-2xl font-bold text-foreground mb-6">创建新帖子</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive rounded-lg text-destructive">
            {error}
          </div>
        )}

        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-foreground mb-2">
            标题
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="请输入帖子标题"
            className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
        </div>

        {/* Content */}
        <div>
          <label htmlFor="content" className="block text-sm font-medium text-foreground mb-2">
            内容
          </label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="请输入帖子内容"
            rows={8}
            className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            required
          />
        </div>

        {/* Is Poll */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIsPoll(!isPoll)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
              isPoll
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border text-muted-foreground hover:border-primary/50'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            这是投票帖
          </button>
          <span className="text-sm text-muted-foreground">
            开启后将显示投票选项
          </span>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-4">
          <Link
            href="/"
            className="px-6 py-2 border border-border rounded-lg text-foreground hover:bg-accent transition-colors"
          >
            取消
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? '发布中...' : '发布帖子'}
          </button>
        </div>
      </form>
    </div>
  );
}