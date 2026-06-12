import { useEffect, useState } from 'react';
import { recentAnalyses } from '../api/client';
import { VerdictBadge } from '../components/Badge';
import type { CommitteeDecision } from '../types';

export function Runs() {
  const [runs, setRuns] = useState<CommitteeDecision[] | null>(null);
  useEffect(() => { recentAnalyses().then(setRuns).catch(() => setRuns([])); }, []);
  return (
    <>
      <div className="page-head">
        <h1>Runs</h1>
        <p>Every committee run is persisted with its full decision payload.</p>
      </div>
      <section className="panel">
        {runs === null ? (
          <div className="skeleton"><div className="line w70" /><div className="line w40" /><div className="line w70" /></div>
        ) : runs.length === 0 ? (
          <div className="empty">
            <h3>No saved runs</h3>
            <p>Runs appear here after you analyze a property. You can also run the CLI: <code>python -m ai_real_estate_fund institutional examples/duplex_sunbelt.json</code></p>
          </div>
        ) : (
          <div className="panel-body flush">
            <table className="table">
              <thead><tr><th>Property</th><th>Market</th><th className="num">Score</th><th>Verdict</th><th>Run</th></tr></thead>
              <tbody>
                {runs.map((run) => (
                  <tr key={run.run_id}>
                    <td className="strong">{run.property.name}</td>
                    <td>{run.property.market}</td>
                    <td className="num">{run.overall_score.toFixed(1)}</td>
                    <td><VerdictBadge value={String(run.recommendation)} /></td>
                    <td><code style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)' }}>{run.run_id.slice(0, 8)}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
