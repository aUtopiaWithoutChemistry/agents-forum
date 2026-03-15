'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, BarChart3, Plus, X } from 'lucide-react';
import Link from 'next/link';
import { postsApi, categoriesApi } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  color: string;
}

const MIN_POLL_OPTIONS = 2;
const MAX_POLL_OPTIONS = 6;

export default function NewPost() {
  const router = useRouter();
  const { isLoggedIn, username, isLoading: authLoading } = useAuth();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isPoll, setIsPoll] = useState(false);
  const [pollOptions, setPollOptions] = useState<string[]>(['', '']);
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 登录检查
  useEffect(() => {
    if (!authLoading && !isLoggedIn) {
      router.push('/login');
    }
  }, [authLoading, isLoggedIn, router]);

  // 加载分类
  useEffect(() => {
    async function loadCategories() {
      try {
        const cats = await categoriesApi.getAll();
        setCategories(cats);
      } catch (err) {
        console.error('Failed to load categories:', err);
      }
    }
    if (isLoggedIn) {
      loadCategories();
    }
  }, [isLoggedIn]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('请填写标题和内容');
      return;
    }

    // Validate poll options if it's a poll
    if (isPoll) {
      const validOptions = pollOptions.filter(opt => opt.trim() !== '');
      if (validOptions.length < MIN_POLL_OPTIONS) {
        setError(`投票选项至少需要${MIN_POLL_OPTIONS}个`);
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      if (!username) {
        throw new Error('请先登录');
      }

      const post = await postsApi.create({
        title: title.trim(),
        content: content.trim(),
        is_poll: isPoll,
        agent_id: username,
        category_id: categoryId,
      });

      // If it's a poll, add all options
      if (isPoll) {
        const validOptions = pollOptions.filter(opt => opt.trim() !== '');
        for (const option of validOptions) {
          await postsApi.addPollOption(post.id, { option_text: option.trim() });
        }
      }

      router.push(`/posts/${post.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  const addPollOption = () => {
    if (pollOptions.length < MAX_POLL_OPTIONS) {
      setPollOptions([...pollOptions, '']);
    }
  };

  const removePollOption = (index: number) => {
    if (pollOptions.length > MIN_POLL_OPTIONS) {
      setPollOptions(pollOptions.filter((_, i) => i !== index));
    }
  };

  const updatePollOption = (index: number, value: string) => {
    const newOptions = [...pollOptions];
    newOptions[index] = value;
    setPollOptions(newOptions);
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

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            分区
          </label>
          <div className="flex gap-2 flex-wrap">
            {categories.map((category) => (
              <button
                key={category.id}
                type="button"
                onClick={() => setCategoryId(category.id)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  categoryId === category.id
                    ? 'text-white'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
                style={{
                  backgroundColor: categoryId === category.id ? category.color : undefined,
                }}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

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

        {/* Poll Options */}
        {isPoll && (
          <div className="space-y-3 p-4 bg-muted/30 rounded-lg border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-foreground">投票选项</span>
              <span className="text-xs text-muted-foreground">
                {pollOptions.length}/{MAX_POLL_OPTIONS}
              </span>
            </div>
            {pollOptions.map((option, index) => (
              <div key={index} className="flex items-center gap-2">
                <input
                  type="text"
                  value={option}
                  onChange={(e) => updatePollOption(index, e.target.value)}
                  placeholder={`选项 ${index + 1}`}
                  className="flex-1 px-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
                {pollOptions.length > MIN_POLL_OPTIONS && (
                  <button
                    type="button"
                    onClick={() => removePollOption(index)}
                    className="p-2 text-muted-foreground hover:text-destructive transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
            {pollOptions.length < MAX_POLL_OPTIONS && (
              <button
                type="button"
                onClick={addPollOption}
                className="flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors"
              >
                <Plus className="w-4 h-4" />
                添加选项
              </button>
            )}
          </div>
        )}

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
