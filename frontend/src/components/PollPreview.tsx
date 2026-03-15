interface PollOption {
  id: number;
  option_text: string;
  vote_count: number;
}

interface PollPreviewProps {
  options: PollOption[];
  maxOptions?: number;
}

export default function PollPreview({ options, maxOptions = 3 }: PollPreviewProps) {
  const totalVotes = options.reduce((sum, opt) => sum + opt.vote_count, 0);
  const displayOptions = options.slice(0, maxOptions);

  return (
    <div className="space-y-2">
      {displayOptions.map((option) => {
        const percentage = totalVotes > 0 ? (option.vote_count / totalVotes) * 100 : 0;
        return (
          <div key={option.id} className="relative">
            <div
              className="absolute inset-0 bg-primary/20 rounded"
              style={{ width: `${percentage}%` }}
            />
            <div className="relative flex justify-between items-center p-2 text-sm">
              <span className="truncate">{option.option_text}</span>
              <span className="text-muted-foreground text-xs">
                {option.vote_count} 票 ({percentage.toFixed(0)}%)
              </span>
            </div>
          </div>
        );
      })}
      {options.length > maxOptions && (
        <p className="text-xs text-muted-foreground">
          + {options.length - maxOptions} 更多选项
        </p>
      )}
    </div>
  );
}