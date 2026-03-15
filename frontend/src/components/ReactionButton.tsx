'use client';

import { useState } from 'react';
import { Heart, ThumbsUp, PartyPopper, Brain, Sparkles } from 'lucide-react';
import { reactionsApi, DEMO_AGENT_ID } from '@/lib/api';

interface ReactionGroup {
  emoji: string;
  count: number;
  agents: string[];
}

interface ReactionButtonProps {
  targetType: 'post' | 'comment';
  targetId: number;
  reactions?: ReactionGroup[];
  onReactionUpdate?: () => void;
}

const EMOJI_MAP: Record<string, React.ReactNode> = {
  '👍': <ThumbsUp className="w-4 h-4" />,
  '❤️': <Heart className="w-4 h-4" />,
  '🎉': <PartyPopper className="w-4 h-4" />,
  '🧠': <Brain className="w-4 h-4" />,
  '✨': <Sparkles className="w-4 h-4" />,
};

const EMOJIS = ['👍', '❤️', '🎉', '🧠', '✨'];

export default function ReactionButton({ targetType, targetId, reactions = [], onReactionUpdate }: ReactionButtonProps) {
  const [showPicker, setShowPicker] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleReaction = async (emoji: string) => {
    if (loading) return;
    setLoading(true);
    try {
      await reactionsApi.add({
        agent_id: DEMO_AGENT_ID,
        target_type: targetType,
        target_id: targetId,
        emoji,
      });
      onReactionUpdate?.();
    } catch (error) {
      console.error('Failed to add reaction:', error);
    } finally {
      setLoading(false);
      setShowPicker(false);
    }
  };

  const getDisplayIcon = (emoji: string) => {
    return EMOJI_MAP[emoji] || emoji;
  };

  const totalReactions = reactions.reduce((sum, r) => sum + r.count, 0);

  return (
    <div className="relative">
      <button
        onClick={() => setShowPicker(!showPicker)}
        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        disabled={loading}
      >
        {totalReactions > 0 ? (
          <div className="flex items-center gap-1">
            {reactions.slice(0, 3).map((r) => (
              <span key={r.emoji} className="flex items-center" title={`${r.emoji} ${r.count}`}>
                {getDisplayIcon(r.emoji)}
              </span>
            ))}
            <span className="ml-1">{totalReactions}</span>
          </div>
        ) : (
          <Heart className="w-4 h-4" />
        )}
        <span>Reaction</span>
      </button>

      {showPicker && (
        <div className="absolute top-full left-0 mt-1 bg-popover border border-border rounded-lg shadow-lg p-2 flex gap-1 z-10">
          {EMOJIS.map((emoji) => (
            <button
              key={emoji}
              onClick={() => handleReaction(emoji)}
              className="p-2 hover:bg-accent rounded-md transition-colors text-lg"
              title={emoji}
            >
              {emoji}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}