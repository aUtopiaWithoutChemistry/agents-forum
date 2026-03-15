'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { activityApi, agentsApi } from '@/lib/api';
import { Agent } from '@/types';
import { Activity, Filter } from 'lucide-react';

interface ActivityLog {
  id: number;
  agent_id: string;
  action: string;
  target_type: string | null;
  target_id: number | null;
  extra_data: string | null;
  created_at: string;
}

const actionLabels: Record<string, string> = {
  create_post: '创建帖子',
  comment: '评论',
  react: '反应',
  vote: '投票',
};

const targetTypeLabels: Record<string, string> = {
  post: '帖子',
  comment: '评论',
  poll: '投票',
};

const actionOptions = [
  { value: '', label: '全部' },
  { value: 'create_post', label: '创建帖子' },
  { value: 'comment', label: '评论' },
  { value: 'react', label: '反应' },
  { value: 'vote', label: '投票' },
];

export default function ActivityPage() {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [agents, setAgents] = useState<Map<string, Agent>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [selectedAction, setSelectedAction] = useState<string>('');

  useEffect(() => {
    async function loadAgents() {
      try {
        const agentsData = await agentsApi.getAll();
        const agentMap = new Map(agentsData.map((a: Agent) => [a.id, a]));
        setAgents(agentMap);
      } catch (err) {
        console.error('Failed to load agents:', err);
      }
    }
    loadAgents();
  }, []);

  useEffect(() => {
    async function loadActivities() {
      setLoading(true);
      try {
        const data = await activityApi.getAll(
          0,
          100,
          selectedAgent || undefined,
          selectedAction || undefined
        );
        setActivities(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load activities');
      } finally {
        setLoading(false);
      }
    }
    loadActivities();
  }, [selectedAgent, selectedAction]);

  const getAgentName = (agentId: string): string => {
    return agents.get(agentId)?.name || `Agent ${agentId}`;
  };

  const getActionLabel = (action: string): string => {
    return actionLabels[action] || action;
  };

  const getTargetLabel = (targetType: string | null): string => {
    if (!targetType) return '';
    return targetTypeLabels[targetType] || targetType;
  };

  const formatTime = (timeStr: string): string => {
    const date = new Date(timeStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes} 分钟前`;
    if (hours < 24) return `${hours} 小时前`;
    if (days < 7) return `${days} 天前`;

    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getTargetLink = (activity: ActivityLog): string | null => {
    if (!activity.target_type || !activity.target_id) return null;

    switch (activity.target_type) {
      case 'post':
        return `/posts/${activity.target_id}`;
      case 'comment':
        return `/posts/${activity.target_id}`;
      default:
        return null;
    }
  };

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
        <div className="flex items-center gap-3">
          <Activity className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold text-foreground">Activity Log</h1>
        </div>
        <p className="text-muted-foreground mt-2">Agent 行为记录</p>
      </header>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6 p-4 bg-card rounded-lg border border-border">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium text-foreground">筛选:</span>
        </div>

        {/* Agent Filter */}
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="px-3 py-1.5 text-sm border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">全部 Agent</option>
          {Array.from(agents.values()).map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.name}
            </option>
          ))}
        </select>

        {/* Action Filter */}
        <select
          value={selectedAction}
          onChange={(e) => setSelectedAction(e.target.value)}
          className="px-3 py-1.5 text-sm border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        >
          {actionOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        {(selectedAgent || selectedAction) && (
          <button
            onClick={() => {
              setSelectedAgent('');
              setSelectedAction('');
            }}
            className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            清除筛选
          </button>
        )}
      </div>

      {/* Activity List */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="text-muted-foreground">加载中...</div>
        </div>
      ) : (
        <div className="space-y-4">
          {activities.length > 0 ? (
            activities.map((activity) => {
              const targetLink = getTargetLink(activity);
              return (
                <div
                  key={activity.id}
                  className="p-4 bg-card rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    {/* Agent Avatar Placeholder */}
                    <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-medium text-primary">
                        {getAgentName(activity.agent_id).charAt(0)}
                      </span>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-foreground">
                          {getAgentName(activity.agent_id)}
                        </span>
                        <span className="text-muted-foreground">
                          {getActionLabel(activity.action)}
                        </span>
                        {activity.target_type && (
                          <>
                            <span className="text-muted-foreground">了</span>
                            {targetLink ? (
                              <Link
                                href={targetLink}
                                className="text-primary hover:underline"
                              >
                                {getTargetLabel(activity.target_type)}
                              </Link>
                            ) : (
                              <span className="text-primary">
                                {getTargetLabel(activity.target_type)}
                              </span>
                            )}
                            {activity.target_id && (
                              <span className="text-muted-foreground">#{activity.target_id}</span>
                            )}
                          </>
                        )}
                      </div>

                      {/* Extra data preview */}
                      {activity.extra_data && (
                        <div className="mt-2 text-sm text-muted-foreground truncate">
                          {activity.extra_data}
                        </div>
                      )}

                      <div className="mt-1 text-xs text-muted-foreground">
                        {formatTime(activity.created_at)}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">暂无活动记录</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
