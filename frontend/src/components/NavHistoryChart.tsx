'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface NavHistoryChartProps {
  data: { date: string; nav: number }[];
  agentName: string;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatUsd(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

export default function NavHistoryChart({ data, agentName }: NavHistoryChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-muted-foreground">
        No NAV history available yet.
      </div>
    );
  }

  // Calculate min/max for better axis scaling
  const navs = data.map((d) => d.nav);
  const minNav = Math.min(...navs);
  const maxNav = Math.max(...navs);
  const padding = (maxNav - minNav) * 0.1;

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            stroke="#9ca3af"
            fontSize={12}
            tickMargin={8}
          />
          <YAxis
            domain={[minNav - padding, maxNav + padding]}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            stroke="#9ca3af"
            fontSize={12}
            tickMargin={8}
            width={60}
          />
          <Tooltip
            formatter={(value: number) => [formatUsd(value), 'NAV']}
            labelFormatter={(label) => formatDate(label)}
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e5e7eb',
              borderRadius: '0.75rem',
              padding: '0.75rem',
            }}
          />
          <Line
            type="monotone"
            dataKey="nav"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#10b981' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
