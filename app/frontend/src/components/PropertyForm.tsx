import { useRef, useState, type ChangeEvent, type FormEvent } from 'react';
import type { PropertyInput } from '../types';
import { DEFAULT_MODELS, PROVIDERS, loadRunSettings, saveRunSettings, type RunSettings } from './SettingsStore';

const fullExample = { name: 'Sunbelt Duplex', address: '123 Main St', market: 'San Antonio, TX', property_type: 'duplex', purchase_price: 285000, estimated_arv: 330000, monthly_rent: 3700, other_monthly_income: 0, vacancy_rate: 0.06, property_taxes_annual: 5200, insurance_annual: 2100, repairs_annual: 2500, utilities_annual: 600, hoa_annual: 0, capex_annual: 2500, management_rate: 0.08, acquisition_costs: 6500, rehab_budget: 18000, loan_amount: 210000, annual_interest_rate: 0.0725, loan_term_years: 30, holding_period_years: 5, expected_annual_rent_growth: 0.03, expected_annual_expense_growth: 0.03, expected_annual_appreciation: 0.035, selling_cost_rate: 0.06, neighborhood_score: 7, school_score: 6, liquidity_score: 7, crime_risk_score: 4, landlord_friendliness_score: 7, unit_count: 2, square_feet: 1850, bedrooms: 4, bathrooms: 2, year_built: 1948 } as unknown as PropertyInput;

/** The four fields the backend cannot default. Everything else has a model default. */
const REQUIRED_KEYS = ['name', 'address', 'market', 'purchase_price'] as const;

type FieldSpec = {
  key: string;
  label: string;
  numeric?: boolean;
  required?: boolean;
  recommended?: boolean;
  /** Model default, shown as the optional field's grey placeholder. Omitted = truly required. */
  placeholder?: string;
};

const groups: Array<{ title: string; fields: FieldSpec[]; advanced?: boolean }> = [
  { title: 'Property', fields: [
    { key: 'name', label: 'Property name', required: true },
    { key: 'address', label: 'Address', required: true },
    { key: 'market', label: 'Market', required: true },
    { key: 'property_type', label: 'Type (e.g. duplex)', placeholder: 'single_family default' },
    { key: 'unit_count', label: 'Units', numeric: true, placeholder: '1 default' },
    { key: 'square_feet', label: 'Square feet', numeric: true, placeholder: '0 default' },
    { key: 'bedrooms', label: 'Bedrooms', numeric: true, placeholder: '0 default' },
    { key: 'bathrooms', label: 'Bathrooms', numeric: true, placeholder: '0 default' },
    { key: 'year_built', label: 'Year built', numeric: true, placeholder: 'optional' },
  ]},
  { title: 'Income', fields: [
    { key: 'monthly_rent', label: 'Monthly rent ($)', numeric: true, recommended: true, placeholder: '0 default — drives returns' },
    { key: 'other_monthly_income', label: 'Other income ($/mo)', numeric: true, placeholder: '0 default' },
    { key: 'vacancy_rate', label: 'Vacancy rate (0–1)', numeric: true, placeholder: '0.05 default' },
  ]},
  { title: 'Financing', fields: [
    { key: 'purchase_price', label: 'Purchase price ($)', numeric: true, required: true },
    { key: 'loan_amount', label: 'Loan amount ($)', numeric: true, placeholder: '0 default' },
    { key: 'annual_interest_rate', label: 'Interest rate (decimal)', numeric: true, placeholder: '0.07 default' },
    { key: 'loan_term_years', label: 'Loan term (years)', numeric: true, placeholder: '30 default' },
    { key: 'acquisition_costs', label: 'Closing costs ($)', numeric: true, placeholder: '0 default' },
    { key: 'rehab_budget', label: 'Rehab budget ($)', numeric: true, placeholder: '0 default' },
  ]},
  { title: 'Operating expenses (annual) · all optional', advanced: true, fields: [
    { key: 'property_taxes_annual', label: 'Property taxes ($)', numeric: true, placeholder: '0 default' },
    { key: 'insurance_annual', label: 'Insurance ($)', numeric: true, placeholder: '0 default' },
    { key: 'repairs_annual', label: 'Repairs ($)', numeric: true, placeholder: '0 default' },
    { key: 'utilities_annual', label: 'Utilities ($)', numeric: true, placeholder: '0 default' },
    { key: 'hoa_annual', label: 'HOA ($)', numeric: true, placeholder: '0 default' },
    { key: 'capex_annual', label: 'Capex reserve ($)', numeric: true, placeholder: '0 default' },
    { key: 'management_rate', label: 'Management rate (0–1)', numeric: true, placeholder: '0.08 default' },
  ]},
  { title: 'Growth & exit · all optional', advanced: true, fields: [
    { key: 'holding_period_years', label: 'Hold (years)', numeric: true, placeholder: '5 default' },
    { key: 'expected_annual_rent_growth', label: 'Rent growth (0–1)', numeric: true, placeholder: '0.03 default' },
    { key: 'expected_annual_expense_growth', label: 'Expense growth (0–1)', numeric: true, placeholder: '0.03 default' },
    { key: 'expected_annual_appreciation', label: 'Appreciation (0–1)', numeric: true, placeholder: '0.03 default' },
    { key: 'selling_cost_rate', label: 'Selling costs (0–1)', numeric: true, placeholder: '0.06 default' },
    { key: 'estimated_arv', label: 'After-repair value ($)', numeric: true, placeholder: '0 default' },
  ]},
  { title: 'Market scores (1–10) · all optional', advanced: true, fields: [
    { key: 'neighborhood_score', label: 'Neighborhood', numeric: true, placeholder: '6 default' },
    { key: 'school_score', label: 'Schools', numeric: true, placeholder: '6 default' },
    { key: 'liquidity_score', label: 'Liquidity', numeric: true, placeholder: '6 default' },
    { key: 'crime_risk_score', label: 'Crime risk', numeric: true, placeholder: '4 default' },
    { key: 'landlord_friendliness_score', label: 'Landlord friendliness', numeric: true, placeholder: '6 default' },
  ]},
];

const ALL_SPECS: FieldSpec[] = groups.flatMap((g) => g.fields);

/** The field keys the form knows how to render — used to drop unknown keys on import (so a run won't 422). */
const KNOWN_KEYS = new Set<string>(ALL_SPECS.map((s) => s.key));

/**
 * Coerce an imported JSON object into the form's string-keyed shape, keeping ONLY known
 * field keys and dropping null/undefined values. Numbers/strings/bools become their string
 * form; nested objects/arrays are skipped (the form has no field for them).
 */
function importedToStrings(parsed: Record<string, unknown>): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(parsed)) {
    if (!KNOWN_KEYS.has(key) || value == null) continue;
    if (typeof value === 'object') continue;
    out[key] = String(value);
  }
  return out;
}

/** True when a raw form entry should be treated as blank ("use default" / "missing"). */
function isBlank(value: unknown): boolean {
  return value == null || (typeof value === 'string' && value.trim() === '');
}

/**
 * Build the submitted payload from the raw form: include ONLY non-blank fields so
 * the backend default applies to anything left blank. Numeric fields are coerced to
 * Number; a blank or unparseable numeric is omitted (never sent as NaN or "").
 */
function buildPayload(form: Record<string, string>): Record<string, unknown> {
  const payload: Record<string, unknown> = {};
  for (const spec of ALL_SPECS) {
    const raw = form[spec.key];
    if (isBlank(raw)) continue;
    if (spec.numeric) {
      const n = Number(raw);
      if (Number.isFinite(n)) payload[spec.key] = n;
    } else {
      payload[spec.key] = raw.trim();
    }
  }
  return payload;
}

/** Per-field required validation. Returns a map of key -> message for offending fields. */
function validate(form: Record<string, string>): Record<string, string> {
  const errors: Record<string, string> = {};
  for (const key of REQUIRED_KEYS) {
    if (isBlank(form[key])) {
      errors[key] = key === 'purchase_price' ? 'Enter a purchase price.' : 'Required.';
    }
  }
  if (!errors.purchase_price && !isBlank(form.purchase_price)) {
    const price = Number(form.purchase_price);
    if (!Number.isFinite(price) || price <= 0) errors.purchase_price = 'Must be greater than 0.';
  }
  return errors;
}

/** Convert the example object into the form's string-keyed shape. */
function exampleAsStrings(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(fullExample as unknown as Record<string, unknown>)) {
    if (value != null) out[key] = String(value);
  }
  return out;
}

export function PropertyForm({ onSubmit, busy }: { onSubmit: (payload: PropertyInput, settings: RunSettings) => void; busy: boolean }) {
  // Clean start: required fields empty, optional fields empty showing default placeholders.
  const [form, setForm] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [importError, setImportError] = useState('');
  const [settings, setSettings] = useState<RunSettings>(loadRunSettings());
  const fileInputRef = useRef<HTMLInputElement>(null);

  const updateSettings = (patch: Partial<RunSettings>) => {
    const next = { ...settings, ...patch };
    setSettings(next);
    saveRunSettings(next);
  };

  const update = (spec: FieldSpec, value: string) => {
    setForm((prev) => ({ ...prev, [spec.key]: value }));
    // Clear this field's error as soon as the user edits it.
    if (errors[spec.key]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[spec.key];
        return next;
      });
    }
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const found = validate(form);
    if (Object.keys(found).length > 0) {
      setErrors(found);
      return;
    }
    setErrors({});
    // Signature unchanged: AnalyzeProperty still receives (payload, settings).
    onSubmit(buildPayload(form) as unknown as PropertyInput, settings);
  };

  const handleImportFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    // Reset the input so re-selecting the same file fires onChange again.
    event.target.value = '';
    if (!file) return;
    try {
      const text = await file.text();
      const parsed: unknown = JSON.parse(text);
      if (parsed == null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Expected a JSON object of property fields.');
      }
      const next = importedToStrings(parsed as Record<string, unknown>);
      if (Object.keys(next).length === 0) {
        throw new Error('No recognized property fields found in that file.');
      }
      // Merge over blanks: imported values replace the form, unknown keys already dropped.
      setForm(next);
      setErrors({});
      setImportError('');
    } catch (err) {
      setImportError(`Couldn't import that file — ${err instanceof Error ? err.message : 'invalid JSON'}.`);
    }
  };

  const hasErrors = Object.keys(errors).length > 0;
  const requiredCount = REQUIRED_KEYS.length;

  const renderFields = (specs: FieldSpec[]) => (
    <div className="form-grid">
      {specs.map((spec) => {
        const fieldError = errors[spec.key];
        const errId = fieldError ? `err-${spec.key}` : undefined;
        return (
          <label key={spec.key} className={`field${fieldError ? ' field-invalid' : ''}`}>
            <span>
              {spec.label}
              {spec.required && <i className="req" aria-hidden="true"> *</i>}
              {spec.recommended && <em className="field-tag"> recommended</em>}
            </span>
            <input
              value={form[spec.key] ?? ''}
              placeholder={spec.placeholder}
              inputMode={spec.numeric ? 'decimal' : undefined}
              aria-required={spec.required || undefined}
              aria-invalid={fieldError ? true : undefined}
              aria-describedby={errId}
              onChange={(event) => update(spec, event.target.value)}
            />
            {fieldError && <span id={errId} className="field-error">{fieldError}</span>}
          </label>
        );
      })}
    </div>
  );

  const basics = groups.filter((g) => !g.advanced);
  const advanced = groups.filter((g) => g.advanced);

  return (
    <form className="panel" onSubmit={handleSubmit} noValidate>
      <div className="panel-head">
        <h2>Analyze a property</h2>
        <span className="hint">{settings.engine === 'institutional' ? 'Institutional committee · 77 workstreams' : 'Screening committee · 29 agents'}</span>
      </div>
      <div className="panel-body">
        <p className="hint" style={{ margin: '0 0 var(--s4)', lineHeight: 1.6 }}>
          Only name, address, market, and purchase price are required. Leave anything you don&apos;t have blank and the engine uses sensible defaults (shown in grey).
        </p>

        {hasErrors && (
          <div className="error-note" role="alert">
            {Object.keys(errors).length} field{Object.keys(errors).length === 1 ? '' : 's'} need attention — all {requiredCount} required fields (name, address, market, purchase price) must be filled, and purchase price must be greater than 0.
          </div>
        )}

        {basics.map((group, index) => (
          <div key={group.title}>
            <div className="fieldset-label" style={index === 0 ? { marginTop: 0 } : undefined}>{group.title}</div>
            {renderFields(group.fields)}
          </div>
        ))}
        <details className="advanced">
          <summary>More assumptions <span className="hint">expenses, growth, market scores — all optional</span></summary>
          {advanced.map((group) => (
            <div key={group.title}>
              <div className="fieldset-label">{group.title}</div>
              {renderFields(group.fields)}
            </div>
          ))}
        </details>

        <div className="fieldset-label">Run options</div>
        <div className="run-options">
          <label className="field">
            <span>Committee</span>
            <select value={settings.engine} onChange={(e) => updateSettings({ engine: e.target.value as RunSettings['engine'] })}>
              <option value="institutional">Institutional (77 workstreams)</option>
              <option value="screening">Screening (29 agents, persisted)</option>
            </select>
          </label>
          {settings.engine === 'institutional' && (
            <>
              <label className="field checkbox">
                <span>LLM analyst debate</span>
                <span className="check-row">
                  <input type="checkbox" checked={settings.llmEnabled} onChange={(e) => updateSettings({ llmEnabled: e.target.checked })} />
                  <em>bull / bear / risk / chair</em>
                </span>
              </label>
              {settings.llmEnabled && (
                <>
                  <label className="field">
                    <span>Provider</span>
                    <select value={settings.llmProvider} onChange={(e) => updateSettings({ llmProvider: e.target.value, llmModel: '' })}>
                      {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </label>
                  <label className="field">
                    <span>Model</span>
                    <input placeholder={DEFAULT_MODELS[settings.llmProvider]} value={settings.llmModel} onChange={(e) => updateSettings({ llmModel: e.target.value })} />
                  </label>
                </>
              )}
            </>
          )}
        </div>

        {importError && <div className="error-note" role="alert">{importError}</div>}

        <div className="btn-row">
          <button className="primary" disabled={busy}>{busy ? 'Running committee…' : 'Run committee'}</button>
          <button type="button" className="secondary" disabled={busy} onClick={() => { setForm(exampleAsStrings()); setErrors({}); setImportError(''); }}>Reset to example</button>
          <button type="button" className="secondary" disabled={busy} onClick={() => fileInputRef.current?.click()} aria-label="Import property fields from a JSON file">Import JSON</button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,application/json"
            onChange={handleImportFile}
            hidden
            aria-hidden="true"
            tabIndex={-1}
          />
        </div>
      </div>
    </form>
  );
}
