import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { History, AlertTriangle } from 'lucide-react';
import { recentAnalyses } from '../api/client';
import { RunRow } from '../components/RunRow';
import { downloadCSV } from '../lib/download';
import type { CommitteeDecision } from '../types';

/** Coerce a possibly-missing backend field to a CSV-safe string. */
function asField(value: unknown): string {
  return value == null ? '' : String(value);
}

/**
 * Flatten the loaded runs into the CSV export rows (one row per run).
 * `engine` and `created_at` are present on persisted runs but omitted from the typed
 * interface, so they're read via a narrowed cast (matching RunDetail's `engine` access).
 */
function runsToCsvRows(runs: CommitteeDecision[]): Record<string, unknown>[] {
  return runs.map((run) => {
    const extra = run as { engine?: unknown; created_at?: unknown };
    return {
      run_id: run.run_id,
      property: run.property.name,
      market: run.property.market,
      overall_score: run.overall_score,
      recommendation: run.recommendation,
      engine: asField(extra.engine),
      created_at: asField(extra.created_at),
    };
  });
}

export function Runs() {
  const [runs, setRuns] = useState<CommitteeDecision[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const load = useCallback(() => {
    setError(null);
    setRuns(null);
    recentAnalyses().then(setRuns).catch((e: unknown) => {
      setError(e instanceof Error ? e.message : 'Failed to load saved runs.');
    });
  }, []);
  useEffect(() => { load(); }, [load]);
  return (
    <>
      <div className="page-head">
        <h1>Runs</h1>
        <p>Every committee run is persisted with its full decision payload — verdict, scores, scenarios, and risk register.</p>
      </div>
      <section className="panel reveal">
        <div className="panel-h">
          <div className="t"><h2>Saved runs</h2></div>
          <div className="btn-row" style={{ marginTop: 0 }}>
            {runs && runs.length > 0 && <span className="hint">{runs.length} total</span>}
            <button
              type="button"
              className="secondary"
              disabled={!runs || runs.length === 0}
              onClick={() => runs && downloadCSV('runs.csv', runsToCsvRows(runs))}
              aria-label="Export saved runs as a CSV file"
            >
              Export CSV
            </button>
          </div>
        </div>
        {error ? (
          <div className="empty">
            <AlertTriangle className="ic" aria-hidden="true" />
            <h3>Couldn't load runs</h3>
            <div className="error-note" role="alert" style={{ marginInline: 'auto', maxWidth: '52ch', textAlign: 'left' }}>{error}</div>
            <div className="btn-row"><button className="primary" onClick={load}>Retry</button></div>
          </div>
        ) : runs === null ? (
          <div className="skeleton"><div className="line w70" /><div className="line w40" /><div className="line w70" /></div>
        ) : runs.length === 0 ? (
          <div className="empty">
            <History className="ic" aria-hidden="true" />
            <h3>No saved runs</h3>
            <p>Runs appear here after you analyze a property. You can also run the CLI:</p>
            <p style={{ marginTop: 'var(--s3)' }}><code>python -m ai_real_estate_fund institutional examples/duplex_sunbelt.json</code></p>
            <div className="btn-row"><Link className="btn btn-primary" to="/analyze">Analyze a deal</Link></div>
          </div>
        ) : (
          <div className="panel-b flush">
            <table className="table">
              <thead><tr><th>Property</th><th>Market</th><th className="num">Score</th><th>Verdict</th><th>Run</th></tr></thead>
              <tbody>
                {runs.map((run) => (
                  <RunRow key={run.run_id} run={run} showRunId />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
