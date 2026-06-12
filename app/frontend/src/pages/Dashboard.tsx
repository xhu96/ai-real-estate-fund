import { useEffect, useState } from 'react';
import { recentAnalyses } from '../api/client';
import { VerdictBadge } from '../components/Badge';
import type { CommitteeDecision } from '../types';

const composition: Array<[string, number]> = [
  ['Acquisition', 5], ['Income', 7], ['Expenses', 9], ['Debt', 10],
  ['Physical condition', 11], ['Market', 14], ['Portfolio & returns', 9], ['Governance', 12],
];

export function Dashboard({ onNavigate }: { onNavigate: (page: 'analyze') => void }) {
  const [runs, setRuns] = useState<CommitteeDecision[] | null>(null);
  useEffect(() => { recentAnalyses().then(setRuns).catch(() => setRuns([])); }, []);

  return (
    <>
      <div className="page-head">
        <h1>Overview</h1>
        <p>Deterministic diligence for rental property deals: 77 cited workstreams, policy gates, scenario stress, and an auditable memo.</p>
      </div>
      <div className="two-col">
        <section className="panel">
          <div className="panel-head">
            <h2>Recent verdicts</h2>
            {runs && runs.length > 0 && <span className="hint">latest {Math.min(runs.length, 5)}</span>}
          </div>
          {runs === null ? (
            <div className="skeleton"><div className="line w70" /><div className="line w40" /><div className="line w70" /></div>
          ) : runs.length === 0 ? (
            <div className="empty">
              <h3>No runs yet</h3>
              <p>Run the committee on a sample deal to see how scoring, scenarios, and the risk register come together.</p>
              <div className="btn-row"><button className="primary" onClick={() => onNavigate('analyze')}>Analyze a property</button></div>
            </div>
          ) : (
            <div className="panel-body flush">
              <table className="table">
                <thead><tr><th>Property</th><th className="num">Score</th><th>Verdict</th></tr></thead>
                <tbody>
                  {runs.slice(0, 5).map((run) => (
                    <tr key={run.run_id}>
                      <td className="strong">{run.property.name}</td>
                      <td className="num">{run.overall_score.toFixed(1)}</td>
                      <td><VerdictBadge value={String(run.recommendation)} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
        <section className="panel">
          <div className="panel-head">
            <h2>Committee composition</h2>
            <span className="hint">77 workstreams</span>
          </div>
          <div className="panel-body">
            <dl className="def-rows">
              {composition.map(([name, count]) => (
                <div key={name} className="def-row"><dt>{name}</dt><dd>{count}</dd></div>
              ))}
            </dl>
          </div>
        </section>
      </div>
    </>
  );
}
