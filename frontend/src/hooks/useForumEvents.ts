'use client';

import { useEffect, useRef, useCallback } from 'react';

export interface ForumEvent {
  type: 'new_post' | 'new_comment' | 'new_reaction' | 'post_deleted' | 'ping';
  data?: {
    post_id?: number;
    comment_id?: number;
    reaction_id?: number;
    [key: string]: unknown;
  };
}

interface UseForumEventsOptions {
  onNewPost?: (data: ForumEvent['data']) => void;
  onNewComment?: (data: ForumEvent['data']) => void;
  onNewReaction?: (data: ForumEvent['data']) => void;
  onPostDeleted?: (data: ForumEvent['data']) => void;
  enabled?: boolean;
}

export function useForumEvents({
  onNewPost,
  onNewComment,
  onNewReaction,
  onPostDeleted,
  enabled = true,
}: UseForumEventsOptions = {}) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const eventSource = new EventSource(`${apiUrl}/api/events/forum`);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const parsed: ForumEvent = JSON.parse(event.data);

        switch (parsed.type) {
          case 'new_post':
            onNewPost?.(parsed.data);
            break;
          case 'new_comment':
            onNewComment?.(parsed.data);
            break;
          case 'new_reaction':
            onNewReaction?.(parsed.data);
            break;
          case 'post_deleted':
            onPostDeleted?.(parsed.data);
            break;
          case 'ping':
            // Keepalive - no action needed
            break;
        }
      } catch (err) {
        console.error('Failed to parse forum event:', err);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      eventSourceRef.current = null;

      // Reconnect after 5 seconds
      if (enabled) {
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 5000);
      }
    };
  }, [enabled, onNewPost, onNewComment, onNewReaction, onPostDeleted]);

  useEffect(() => {
    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [connect]);
}
