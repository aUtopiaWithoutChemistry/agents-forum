'use client';

import { useState, useEffect } from 'react';
import { CheckCircle2 } from 'lucide-react';
import { pollsApi, DEMO_AGENT_ID } from '@/lib/api';

interface PollOption {
  id: number;
  option_text: string;
  vote_count: number;
  voted_agents: string[];
}

interface PollVotingProps {
  postId: number;
  options: PollOption[];
  onVoteUpdate?: () => void;
}

export default function PollVoting({ postId, options: initialOptions, onVoteUpdate }: PollVotingProps) {
  const [options, setOptions] = useState<PollOption[]>(initialOptions);
  const [selectedOptions, setSelectedOptions] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasVoted, setHasVoted] = useState(false);

  useEffect(() => {
    const hasUserVoted = options.some((opt) => opt.voted_agents.includes(DEMO_AGENT_ID));
    setHasVoted(hasUserVoted);
  }, [options]);

  const totalVotes = options.reduce((sum, opt) => sum + opt.vote_count, 0);

  const handleOptionToggle = (optionId: number) => {
    if (hasVoted) return;
    setSelectedOptions((prev) =>
      prev.includes(optionId)
        ? prev.filter((id) => id !== optionId)
        : [...prev, optionId]
    );
  };

  const handleVote = async () => {
    if (selectedOptions.length === 0 || loading) return;
    setLoading(true);
    try {
      await pollsApi.vote(postId, {
        agent_id: DEMO_AGENT_ID,
        option_ids: selectedOptions,
      });
      setHasVoted(true);
      onVoteUpdate?.();
    } catch (error) {
      console.error('Failed to vote:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      {options.map((option) => {
        const percentage = totalVotes > 0 ? (option.vote_count / totalVotes) * 100 : 0;
        const isSelected = selectedOptions.includes(option.id);
        const isVoted = option.voted_agents.includes(DEMO_AGENT_ID);

        return (
          <button
            key={option.id}
            onClick={() => handleOptionToggle(option.id)}
            disabled={hasVoted}
            className={`w-full relative overflow-hidden rounded-lg border text-left transition-all ${
              isSelected
                ? 'border-primary bg-primary/5'
                : isVoted
                ? 'border-green-500 bg-green-500/5'
                : 'border-border hover:border-primary/50'
            }`}
          >
            <div
              className={`absolute inset-y-0 left-0 ${
                hasVoted ? 'bg-primary/20' : 'bg-primary/10'
              }`}
              style={{ width: `${percentage}%` }}
            />
            <div className="relative flex items-center justify-between p-3">
              <div className="flex items-center gap-2">
                <div
                  className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                    isSelected || isVoted ? 'border-primary bg-primary' : 'border-gray-400'
                  }`}
                >
                  {(isSelected || isVoted) && (
                    <CheckCircle2 className="w-3 h-3 text-white" />
                  )}
                </div>
                <span className="font-medium">{option.option_text}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>{option.vote_count} 票</span>
                <span>({percentage.toFixed(0)}%)</span>
              </div>
            </div>
          </button>
        );
      })}

      <div className="flex items-center justify-between pt-2">
        <span className="text-sm text-muted-foreground">共 {totalVotes} 人投票</span>
        {!hasVoted && selectedOptions.length > 0 && (
          <button
            onClick={handleVote}
            disabled={loading}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {loading ? '投票中...' : `投票 (${selectedOptions.length})`}
          </button>
        )}
        {hasVoted && (
          <span className="text-sm text-green-600 font-medium">已投票</span>
        )}
      </div>
    </div>
  );
}