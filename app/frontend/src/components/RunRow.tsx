import type { KeyboardEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { VerdictBadge } from './Badge';
import type { CommitteeDecision } from '../types';

/**
 * A clickable, keyboard-accessible table row for a saved run. The whole row navigates to
 * `/runs/{run_id}`. Cells stay <td> so the existing `.table` styling is untouched; the row
 * is given role="button" + Enter/Space handling for keyboard users. `showRunId` adds the
 * short-id column used on the Runs page (the Dashboard table omits it).
 */
export function RunRow({ run, showRunId = false }: { run: CommitteeDecision; showRunId?: boolean }) {
  const navigate = useNavigate();
  const go = () => navigate(`/runs/${encodeURIComponent(run.run_id)}`);
  const onKeyDown = (e: KeyboardEvent<HTMLTableRowElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      go();
    }
  };
  return (
    <tr
      role="button"
      tabIndex={0}
      onClick={go}
      onKeyDown={onKeyDown}
      aria-label={`Open run for ${run.property.name}`}
      style={{ cursor: 'pointer' }}
    >
      <td className="strong">{run.property.name}</td>
      <td>{run.property.market}</td>
      <td className="num">{run.overall_score.toFixed(1)}</td>
      <td><VerdictBadge value={String(run.recommendation)} /></td>
      {showRunId && <td><code style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)' }}>{run.run_id.slice(0, 8)}</code></td>}
    </tr>
  );
}
