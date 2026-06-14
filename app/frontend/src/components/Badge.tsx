const classFor: Record<string, string> = { BUY: 'buy', NEGOTIATE: 'negotiate', WATCHLIST: 'watchlist', PASS: 'pass' };

export function VerdictBadge({ value, large }: { value: string; large?: boolean }) {
  return <span className={`badge ${classFor[value] ?? ''}${large ? ' lg' : ''}`}>{value}</span>;
}
