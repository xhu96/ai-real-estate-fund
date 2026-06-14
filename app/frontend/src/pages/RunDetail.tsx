import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { History, AlertTriangle, ArrowLeft } from 'lucide-react';
import { downloadInstitutionalReportPdf, downloadScreeningReportPdf, getRun } from '../api/client';
import { DecisionResult } from '../components/DecisionResult';
import { downloadBlob, downloadJSON } from '../lib/download';
import type { CommitteeDecision, InstitutionalDecision } from '../types';

/** Turn a property name into a safe filename stem (mirrors AnalyzeProperty's helper). */
function safeName(name: string): string {
  const stem = name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  return stem || 'run';
}

type Decision = CommitteeDecision | InstitutionalDecision;

/**
 * Detect which committee produced a decision. Prefer the explicit `engine` field
 * (backend contract: "institutional" | "screening"); fall back to structural inference —
 * institutional runs carry a non-empty `scorecards[]`.
 */
function decisionKind(decision: Decision): 'institutional' | 'screening' {
  const engine = (decision as { engine?: unknown }).engine;
  if (engine === 'institutional') return 'institutional';
  if (engine === 'screening') return 'screening';
  const scorecards = (decision as { scorecards?: unknown }).scorecards;
  return Array.isArray(scorecards) && scorecards.length > 0 ? 'institutional' : 'screening';
}

export function RunDetail() {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const [decision, setDecision] = useState<Decision | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!runId) return;
    setError(null);
    setNotFound(false);
    setDecision(null);
    getRun(runId)
      .then(setDecision)
      .catch((e: unknown) => {
        const message = e instanceof Error ? e.message : 'Failed to load this run.';
        // request() formats 404s with a "(404)" marker — surface those as a clear empty state.
        if (message.includes('404')) setNotFound(true);
        else setError(message);
      });
  }, [runId]);
  useEffect(() => { load(); }, [load]);

  const exportJson = () => {
    if (!decision) return;
    setExportError(null);
    downloadJSON(`run-${safeName(decision.property.name)}.json`, decision);
  };

  const exportPdf = async () => {
    if (!decision) return;
    setExportError(null);
    setExportingPdf(true);
    try {
      const blob = decisionKind(decision) === 'institutional'
        ? await downloadInstitutionalReportPdf(decision.property, { enabled: false })
        : await downloadScreeningReportPdf(decision.property);
      downloadBlob(`report-${safeName(decision.property.name)}.pdf`, blob, 'application/pdf');
    } catch (err) {
      setExportError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setExportingPdf(false);
    }
  };

  return (
    <>
      <div className="page-head" style={{ flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between', gap: 'var(--s4)', flexWrap: 'wrap' }}>
        <div>
          <h1>Run detail</h1>
          <p>The full committee decision for this run — verdict, scores, scenarios, and risk register. {runId && <code style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)' }}>{runId.slice(0, 8)}</code>}</p>
        </div>
        <div className="btn-row" style={{ marginTop: 0 }}>
          <button className="btn btn-primary" onClick={() => navigate('/runs')}><ArrowLeft className="ic" strokeWidth={2.2} aria-hidden="true" /> Back to runs</button>
          <button type="button" className="secondary" disabled={!decision} onClick={exportJson} aria-label="Export this run's decision as a JSON file">Export JSON</button>
          <button type="button" className="secondary" disabled={!decision || exportingPdf} onClick={exportPdf} aria-label="Download this run's report as a PDF file">
            {exportingPdf ? 'Preparing PDF…' : 'Download PDF'}
          </button>
        </div>
      </div>

      {exportError && <div className="error-note" role="alert">{exportError}</div>}

      {notFound ? (
        <section className="panel reveal">
          <div className="empty">
            <History className="ic" aria-hidden="true" />
            <h3>Run not found</h3>
            <p>No saved run matches{runId ? <> <code>{runId}</code></> : ' this id'}. It may have been removed, or the id is incorrect.</p>
            <div className="btn-row"><Link className="btn btn-primary" to="/runs">Back to all runs</Link></div>
          </div>
        </section>
      ) : error ? (
        <section className="panel reveal">
          <div className="empty">
            <AlertTriangle className="ic" aria-hidden="true" />
            <h3>Couldn't load this run</h3>
            <div className="error-note" role="alert" style={{ marginInline: 'auto', maxWidth: '52ch', textAlign: 'left' }}>{error}</div>
            <div className="btn-row">
              <button className="primary" onClick={load}>Retry</button>
              <Link className="btn btn-ghost" to="/runs">Back to runs</Link>
            </div>
          </div>
        </section>
      ) : decision === null ? (
        <section className="panel" aria-busy="true">
          <div className="skeleton">
            <div className="line w40" /><div className="line w70" /><div className="line" /><div className="line w70" />
          </div>
        </section>
      ) : decisionKind(decision) === 'institutional' ? (
        <DecisionResult kind="institutional" decision={decision as InstitutionalDecision} />
      ) : (
        <DecisionResult kind="screening" decision={decision as CommitteeDecision} />
      )}
    </>
  );
}
