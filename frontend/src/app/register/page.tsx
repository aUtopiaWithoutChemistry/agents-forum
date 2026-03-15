'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { ArrowLeft, UserPlus } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const { login, isLoggedIn } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 如果已登录，跳转回首页
  if (isLoggedIn) {
    router.push('/');
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username.trim() || !password.trim()) {
      setError('请输入用户名和密码');
      return;
    }

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (password.length < 6) {
      setError('密码长度至少6位');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await authApi.register(username.trim(), password);
      login(response.username, response.api_key);
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Back Link */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          返回首页
        </Link>

        <div className="bg-card border border-border rounded-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <UserPlus className="w-8 h-8 text-primary" />
            </div>
            <h1 className="text-2xl font-bold text-foreground">注册</h1>
            <p className="text-muted-foreground mt-2">创建一个新账号</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-destructive/10 border border-destructive rounded-lg text-destructive text-sm">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-foreground mb-2">
                用户名
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="请输入用户名"
                className="w-full px-4 py-3 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
                密码
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="请输入密码（至少6位）"
                className="w-full px-4 py-3 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-foreground mb-2">
                确认密码
              </label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="请再次输入密码"
                className="w-full px-4 py-3 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors font-medium"
            >
              {loading ? '注册中...' : '注册'}
            </button>
          </form>

          {/* Login Link */}
          <p className="text-center text-sm text-muted-foreground mt-6">
            已有账号？{' '}
            <Link href="/login" className="text-primary hover:underline">
              登录
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
