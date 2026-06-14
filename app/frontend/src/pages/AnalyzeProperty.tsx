import { useState } from 'react';
import { analyzeInstitutional, analyzeScreening, downloadInstitutionalReportPdf, downloadScreeningReportPdf, exportInstitutionalMemo, exportScreeningMemo } from '../api/client';
import { DecisionResult } from '../components/DecisionResult';
import { PropertyForm } from '../components/PropertyForm';
import type { RunSettings } from '../components/SettingsStore';
import { downloadBlob } from '../lib/download';
import type { CommitteeDecision, InstitutionalDecision, PropertyInput } from '../types';

type Result = { kind: 'screening'; decision: CommitteeDecision } | { kind: 'institutional'; decision: InstitutionalDecision };

type LastRun = { payload: PropertyInput; settings: RunSettings };

/** Turn a property name into a safe .md filename stem. */
function safeName(name: string): string {
  const stem = name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  return stem || 'deal';
}

export function AnalyzeProperty() {
  const [result, setResult] = useState<Result | null>(null);
  const [lastRun, setLastRun] = useState<LastRun | null>(null);
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [error, setError] = useState('');

  async function submit(payload: PropertyInput, settings: RunSettings) {
    setError('');
    setBusy(true);
    setResult(null);
    setLastRun(null);
    try {
      if (settings.engine === 'screening') {
        setResult({ kind: 'screening', decision: await analyzeScreening(payload) });
      } else {
        setResult({
          kind: 'institutional',
          decision: await analyzeInstitutional(payload, { enabled: settings.llmEnabled, provider: settings.llmProvider, model: settings.llmModel || undefined, apiKey: settings.llmApiKey || undefined, baseUrl: settings.llmBaseUrl || undefined }),
        });
      }
      setLastRun({ payload, settings });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setBusy(false);
    }
  }

  async function exportMemo() {
    if (!result || !lastRun) return;
    setError('');
    setExporting(true);
    try {
      const { payload, settings } = lastRun;
      const markdown = result.kind === 'institutional'
        ? await exportInstitutionalMemo(payload, { enabled: settings.llmEnabled, provider: settings.llmProvider, model: settings.llmModel || undefined, apiKey: settings.llmApiKey || undefined, baseUrl: settings.llmBaseUrl || undefined })
        : await exportScreeningMemo(payload);
      const url = URL.createObjectURL(new Blob([markdown], { type: 'text/markdown' }));
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `memo-${safeName(payload.name)}.md`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setExporting(false);
    }
  }

  async function exportPdf() {
    if (!result || !lastRun) return;
    setError('');
    setExportingPdf(true);
    try {
      const { payload, settings } = lastRun;
      const blob = result.kind === 'institutional'
        ? await downloadInstitutionalReportPdf(payload, { enabled: settings.llmEnabled, provider: settings.llmProvider, model: settings.llmModel || undefined, apiKey: settings.llmApiKey || undefined, baseUrl: settings.llmBaseUrl || undefined })
        : await downloadScreeningReportPdf(payload);
      downloadBlob(`report-${safeName(payload.name)}.pdf`, blob, 'application/pdf');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setExportingPdf(false);
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>Analyze deal</h1>
        <p>Set the assumptions, pick a committee, and optionally add the analyst debate. The engine is deterministic — every score traces to a rule, never to a model.</p>
      </div>

      <PropertyForm onSubmit={submit} busy={busy} />
      {error && <div className="error-note" role="alert">{error}</div>}

      {busy && (
        <section className="panel" aria-busy="true" style={{ marginTop: 'var(--s5)' }}>
          <div className="skeleton">
            <div className="line w40" /><div className="line w70" /><div className="line" /><div className="line w70" />
          </div>
          <p className="hint" style={{ padding: '0 var(--s5) var(--s5)' }}>Scoring is instant. With the analyst debate on, four model calls run in sequence — the first can take a minute on a cold model.</p>
        </section>
      )}

      {result && (
        <div className="btn-row" style={{ justifyContent: 'flex-end', marginTop: 'var(--s5)' }}>
          <button type="button" className="secondary" onClick={exportMemo} disabled={exporting} aria-label="Download memo as Markdown file">
            {exporting ? 'Preparing memo…' : 'Download memo (.md)'}
          </button>
          <button type="button" className="secondary" onClick={exportPdf} disabled={exportingPdf} aria-label="Download report as PDF file">
            {exportingPdf ? 'Preparing PDF…' : 'Download PDF'}
          </button>
        </div>
      )}

      {result && (
        <div style={{ marginTop: 'var(--s5)' }}>
          {result.kind === 'institutional'
            ? <DecisionResult kind="institutional" decision={result.decision} />
            : <DecisionResult kind="screening" decision={result.decision} />}
        </div>
      )}
    </>
  );
}
