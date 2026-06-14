import { useEffect, useState } from 'react';
import { DEFAULT_API_BASE, isApiBaseValid, listModels, llmStatus, testLlm, type LlmStatus } from '../api/client';
import { DEFAULT_MODELS, PROVIDERS, loadRunSettings, saveRunSettings } from '../components/SettingsStore';

type Msg = { kind: 'ok' | 'err'; text: string } | null;

export function Settings() {
  const [base, setBase] = useState(localStorage.getItem('aref.apiBase') ?? '');
  const [run, setRun] = useState(loadRunSettings());
  const [saved, setSaved] = useState(false);
  const [baseErr, setBaseErr] = useState('');

  const [status, setStatus] = useState<LlmStatus | null>(null);
  const [models, setModels] = useState<string[]>([]);
  const [busy, setBusy] = useState<'' | 'models' | 'test'>('');
  const [msg, setMsg] = useState<Msg>(null);

  useEffect(() => { llmStatus(run.llmProvider).then(setStatus).catch(() => setStatus(null)); }, [run.llmProvider]);

  function save() {
    const trimmed = base.trim();
    if (trimmed && !isApiBaseValid(trimmed)) { setBaseErr('Enter a full backend URL like http://localhost:8000 — a URL, not an API key.'); return; }
    setBaseErr('');
    if (trimmed) localStorage.setItem('aref.apiBase', trimmed); else localStorage.removeItem('aref.apiBase');
    saveRunSettings(run);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  async function fetchModels() {
    setBusy('models'); setMsg(null);
    try {
      const r = await listModels({ provider: run.llmProvider, apiKey: run.llmApiKey || undefined, baseUrl: run.llmBaseUrl || undefined });
      setModels(r.models);
      setMsg({ kind: 'ok', text: `${r.count} models available for ${r.provider}.` });
    } catch (e) {
      setMsg({ kind: 'err', text: e instanceof Error ? e.message : 'Could not list models.' });
    } finally { setBusy(''); }
  }

  async function testConn() {
    setBusy('test'); setMsg(null);
    try {
      const r = await testLlm({ provider: run.llmProvider, model: run.llmModel || undefined, apiKey: run.llmApiKey || undefined, baseUrl: run.llmBaseUrl || undefined });
      setMsg({ kind: 'ok', text: `Connection OK · ${r.model} · ${r.latency_ms} ms` });
    } catch (e) {
      setMsg({ kind: 'err', text: e instanceof Error ? e.message : 'Test failed.' });
    } finally { setBusy(''); }
  }

  return (
    <>
      <div className="page-head">
        <h1>Settings</h1>
        <p>Saved in this browser. Provider keys default to the server <code>.env</code>; you can override them here per the option you chose.</p>
      </div>

      <section className="panel reveal">
        <div className="panel-h"><div className="t"><h2>Connection</h2></div></div>
        <div className="panel-b">
          <div className="form-grid">
            <label className="field">
              <span>API base URL <span className="field-tag">override, optional</span></span>
              <input placeholder="auto-connect — leave blank" value={base} onChange={(e) => setBase(e.target.value)} />
            </label>
          </div>
          <p className="prose" style={{ marginTop: 'var(--s3)', color: 'var(--muted)', fontSize: 'var(--text-xs)' }}>
            Leave blank to <b>auto-connect</b>: the dev server proxies API calls to the backend (run both with <code>./dev.sh</code>), so there's no URL to copy. Set a full URL (e.g. <code>{DEFAULT_API_BASE}</code>) only to point at a different or remote backend. This is a URL, not an API key.
          </p>
          {baseErr && <div className="error-note" role="alert">{baseErr}</div>}
        </div>
      </section>

      <section className="panel reveal">
        <div className="panel-h">
          <div className="t"><h2>AI provider (LLM analysts)</h2></div>
          <span className="hint">
            {status ? `server key: ${status.key_present ? 'configured ✓' : 'not set ✗'}` : 'checking…'}
          </span>
        </div>
        <div className="panel-b">
          <div className="run-options">
            <label className="field">
              <span>Provider</span>
              <select value={run.llmProvider} onChange={(e) => { setRun({ ...run, llmProvider: e.target.value, llmModel: '' }); setModels([]); setMsg(null); }}>
                {(status?.providers ?? PROVIDERS).map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </label>
            <label className="field">
              <span>Model</span>
              <input
                list="llm-models"
                placeholder={DEFAULT_MODELS[run.llmProvider] || 'model id'}
                value={run.llmModel}
                onChange={(e) => setRun({ ...run, llmModel: e.target.value })}
              />
              <datalist id="llm-models">
                {models.map((m) => <option key={m} value={m} />)}
              </datalist>
            </label>
            <label className="field">
              <span>API key — override (optional)</span>
              <input
                type="password"
                placeholder={status?.key_present ? 'using server .env — leave blank' : 'paste a key, or set it in server .env'}
                value={run.llmApiKey}
                onChange={(e) => setRun({ ...run, llmApiKey: e.target.value })}
              />
            </label>
            <label className="field">
              <span>Base URL — override (optional)</span>
              <input
                placeholder={status?.base_url || 'provider default'}
                value={run.llmBaseUrl}
                onChange={(e) => setRun({ ...run, llmBaseUrl: e.target.value })}
              />
            </label>
            <label className="field checkbox">
              <span>LLM debate on by default</span>
              <span className="check-row">
                <input type="checkbox" checked={run.llmEnabled} onChange={(e) => setRun({ ...run, llmEnabled: e.target.checked })} />
                <em>bull / bear / risk / chair</em>
              </span>
            </label>
            <label className="field">
              <span>Committee</span>
              <select value={run.engine} onChange={(e) => setRun({ ...run, engine: e.target.value as typeof run.engine })}>
                <option value="institutional">Institutional (77 workstreams)</option>
                <option value="screening">Screening (29 agents)</option>
              </select>
            </label>
          </div>

          <div className="btn-row">
            <button className="secondary" type="button" disabled={busy !== ''} onClick={fetchModels}>
              {busy === 'models' ? 'Listing…' : 'List models'}
            </button>
            <button className="secondary" type="button" disabled={busy !== ''} onClick={testConn}>
              {busy === 'test' ? 'Testing…' : 'Test connection'}
            </button>
            <button className="primary" type="button" onClick={save}>Save settings</button>
            {saved && <span className="hint" role="status">Saved.</span>}
            {msg && msg.kind === 'ok' && <span className="hint" role="status" style={{ color: 'var(--positive)' }}>{msg.text}</span>}
          </div>
          {msg && msg.kind === 'err' && <div className="error-note" role="alert">{msg.text}</div>}

          <p className="prose" style={{ marginTop: 'var(--s4)', color: 'var(--muted)', fontSize: 'var(--text-xs)' }}>
            “List models” reads the provider catalog (e.g. NVIDIA’s ~120 models) — pick one from the dropdown or type any id manually.
            Leave the key blank to use the server <code>.env</code>. A key entered here is stored in this browser and sent with each run.
            First run of a fresh model can take a minute (cold start), then it’s fast.
          </p>
        </div>
      </section>
    </>
  );
}
