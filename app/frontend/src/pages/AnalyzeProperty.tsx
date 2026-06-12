import { useState } from 'react';
import { analyzeInstitutional, analyzeScreening } from '../api/client';
import { Findings } from '../components/Findings';
import { AnalystCommentary, PolicyGates, Scorecards, VerdictHeader } from '../components/InstitutionalResults';
import { MemoViewer } from '../components/MemoViewer';
import { PropertyForm } from '../components/PropertyForm';
import { RiskRegister } from '../components/RiskRegister';
import { ScenarioTable } from '../components/ScenarioTable';
import type { RunSettings } from '../components/SettingsStore';
import type { CommitteeDecision, InstitutionalDecision, PropertyInput } from '../types';

type Result = { kind: 'screening'; decision: CommitteeDecision } | { kind: 'institutional'; decision: InstitutionalDecision };

export function AnalyzeProperty() {
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function submit(payload: PropertyInput, settings: RunSettings) {
    setError('');
    setBusy(true);
    setResult(null);
    try {
      if (settings.engine === 'screening') {
        setResult({ kind: 'screening', decision: await analyzeScreening(payload) });
      } else {
        setResult({
          kind: 'institutional',
          decision: await analyzeInstitutional(payload, { enabled: settings.llmEnabled, provider: settings.llmProvider, model: settings.llmModel || undefined }),
        });
      }
    } catch (err) {
      setError(err instanceof Error ? `The committee run failed (${err.message}). Check that the API is running on port 8000.` : 'Unknown error');
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>Analyze</h1>
        <p>Configure the deal, choose a committee, and optionally add the LLM analyst debate. Every assumption below feeds the deterministic engine.</p>
      </div>
      <PropertyForm onSubmit={submit} busy={busy} />
      {error && <div className="error-note" role="alert">{error}</div>}
      {busy && (
        <section className="panel" aria-busy="true" style={{ marginTop: 'var(--s4)' }}>
          <div className="skeleton">
            <div className="line w40" /><div className="line w70" /><div className="line" /><div className="line w70" />
          </div>
          <p className="hint" style={{ padding: '0 var(--s5) var(--s4)' }}>Deterministic scoring is instant; the LLM analyst debate adds four model calls and can take up to a minute on some providers.</p>
        </section>
      )}
      {result?.kind === 'institutional' && (
        <>
          <div style={{ marginTop: 'var(--s4)' }} />
          <VerdictHeader decision={result.decision} />
          <PolicyGates decision={result.decision} />
          <Scorecards decision={result.decision} />
          <AnalystCommentary decision={result.decision} />
          <ScenarioTable scenarios={result.decision.scenarios} />
          <RiskRegister risks={result.decision.risk_register} />
          <Findings findings={result.decision.findings} />
        </>
      )}
      {result?.kind === 'screening' && (
        <>
          <div style={{ marginTop: 'var(--s4)' }} />
          <MemoViewer decision={result.decision} />
          <ScenarioTable scenarios={result.decision.scenarios} />
          <RiskRegister risks={result.decision.risk_register} />
          <Findings findings={result.decision.findings} />
        </>
      )}
    </>
  );
}
