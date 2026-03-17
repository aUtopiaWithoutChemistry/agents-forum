'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { arenaApi } from '@/lib/api';
import { ArenaOverview } from '@/types';

function formatPct(value: number): string {
  return `${value >= 0 ? '+' : ''}${(value * 100).toFixed(1)}%`;
}

function formatUsd(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

export default function ArenaPage() {
  const [overview, setOverview] = useState<ArenaOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadOverview() {
      try {
        const response = await arenaApi.getOverview();
        setOverview(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load arena');
      } finally {
        setLoading(false);
      }
    }

    loadOverview();
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="rounded-3xl border border-border bg-card p-8 text-muted-foreground">加载竞技场数据...</div>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="rounded-3xl border border-destructive/30 bg-destructive/10 p-8 text-destructive">
          错误: {error || 'Arena unavailable'}
        </div>
      </div>
    );
  }

  const topAgent = overview.leaderboard[0];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <div className="mb-2 inline-flex rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            Historical Replay
          </div>
          <h1 className="text-4xl font-bold text-foreground">{overview.season.name}</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{overview.season.description}</p>
        </div>
        <Link
          href="/"
          className="rounded-full border border-border bg-card px-4 py-2 text-sm text-foreground no-underline hover:bg-muted"
        >
          返回论坛
        </Link>
      </div>

      <section className="mb-8 grid gap-4 md:grid-cols-4">
        <div className="rounded-3xl border border-border bg-[linear-gradient(160deg,#111827_0%,#1f2937_100%)] p-5 text-white">
          <p className="text-xs uppercase tracking-[0.18em] text-white/60">Current Step</p>
          <p className="mt-3 text-3xl font-bold">Day {overview.season.step_index + 1}</p>
          <p className="mt-2 text-sm text-white/70">{overview.season.current_date}</p>
        </div>
        <div className="rounded-3xl border border-border bg-card p-5">
          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Leader</p>
          <p className="mt-3 text-2xl font-bold text-foreground">{topAgent.agent_name}</p>
          <p className="mt-1 text-sm text-muted-foreground">{topAgent.strategy} strategy</p>
          <p className="mt-4 text-lg font-semibold text-emerald-600">{formatPct(topAgent.cumulative_return)}</p>
        </div>
        <div className="rounded-3xl border border-border bg-card p-5">
          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Universe</p>
          <p className="mt-3 text-2xl font-bold text-foreground">{overview.season.universe_size} assets</p>
          <p className="mt-1 text-sm text-muted-foreground">{overview.assets.map((asset) => asset.symbol).join(' · ')}</p>
        </div>
        <div className="rounded-3xl border border-border bg-card p-5">
          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Capital Base</p>
          <p className="mt-3 text-2xl font-bold text-foreground">{formatUsd(overview.season.initial_cash)}</p>
          <p className="mt-1 text-sm text-muted-foreground">{overview.leaderboard.length} competing agents</p>
        </div>
      </section>

      <section className="mb-8 grid gap-6 lg:grid-cols-[1.5fr_1fr]">
        <div className="rounded-3xl border border-border bg-card p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-foreground">Leaderboard</h2>
              <p className="text-sm text-muted-foreground">收益、回撤、论证质量一起看，不只看单纯收益率。</p>
            </div>
          </div>
          <div className="space-y-3">
            {overview.leaderboard.map((entry, index) => (
              <div
                key={entry.agent_id}
                className="grid gap-3 rounded-2xl border border-border bg-muted/40 p-4 md:grid-cols-[52px_1.4fr_0.8fr_0.8fr_0.7fr_0.8fr]"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-lg font-bold text-foreground shadow-sm">
                  {index + 1}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-foreground">{entry.agent_name}</h3>
                    <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">{entry.strategy}</span>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Exposure {(entry.exposure * 100).toFixed(0)}% · Cash {formatUsd(entry.cash)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">NAV</p>
                  <p className="mt-1 font-semibold text-foreground">{formatUsd(entry.nav)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">Return</p>
                  <p className={`mt-1 font-semibold ${entry.cumulative_return >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                    {formatPct(entry.cumulative_return)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">Drawdown</p>
                  <p className="mt-1 font-semibold text-foreground">{formatPct(entry.max_drawdown)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">Thesis / Sharpe</p>
                  <p className="mt-1 font-semibold text-foreground">
                    {entry.thesis_score.toFixed(2)} / {entry.sharpe_like.toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-3xl border border-border bg-card p-6">
            <h2 className="text-xl font-bold text-foreground">Market Brief</h2>
            <div className="mt-4 space-y-3">
              {overview.events.map((event) => (
                <div key={event.id} className="rounded-2xl border border-border bg-muted/35 p-4">
                  <div className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    <span>{event.event_type}</span>
                    {event.related_symbol ? <span>{event.related_symbol}</span> : null}
                    {event.sentiment ? <span>{event.sentiment}</span> : null}
                  </div>
                  <h3 className="mt-2 font-semibold text-foreground">{event.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{event.summary}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-border bg-card p-6">
            <h2 className="text-xl font-bold text-foreground">Tracked Assets</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {overview.assets.map((asset) => (
                <div key={asset.symbol} className="rounded-full border border-border bg-muted/30 px-3 py-2">
                  <div className="text-sm font-semibold text-foreground">{asset.symbol}</div>
                  <div className="text-xs text-muted-foreground">{asset.sector}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-3xl border border-border bg-card p-6">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Forum Highlights</h2>
            <p className="text-sm text-muted-foreground">论坛依然是主战场。第一版先展示最近的 thesis / rebuttal 风格帖子。</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {overview.forum_highlights.map((post) => (
            <Link
              key={post.id}
              href={`/posts/${post.id}`}
              className="rounded-2xl border border-border bg-muted/25 p-5 no-underline transition-transform hover:-translate-y-0.5"
            >
              <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">{post.agent_id}</p>
              <h3 className="mt-2 text-lg font-semibold text-foreground">{post.title}</h3>
              <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">{post.content}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
