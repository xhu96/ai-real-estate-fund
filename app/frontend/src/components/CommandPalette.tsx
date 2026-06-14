import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, LineChart, History, Network, PieChart, FlaskConical,
  Wrench, Settings as SettingsIcon, Search, CornerDownLeft,
} from 'lucide-react';
import { recentAnalyses } from '../api/client';
import { VerdictBadge } from './Badge';
import type { CommitteeDecision } from '../types';

type IconType = typeof LayoutDashboard;

/** A navigable page/tool target. Mirrors the sidebar nav in Layout. */
interface PageItem { kind: 'page'; path: string; label: string; icon: IconType; hint: string }
/** A persisted run; selecting it opens `/runs/{run_id}`. */
interface RunItem { kind: 'run'; run: CommitteeDecision }
type Item = PageItem | RunItem;

const PAGES: PageItem[] = [
  { kind: 'page', path: '/', label: 'Overview', icon: LayoutDashboard, hint: 'Dashboard' },
  { kind: 'page', path: '/analyze', label: 'Analyze deal', icon: LineChart, hint: 'Run analysis' },
  { kind: 'page', path: '/runs', label: 'Runs', icon: History, hint: 'Saved runs' },
  { kind: 'page', path: '/committee', label: 'Committee', icon: Network, hint: 'Roster' },
  { kind: 'page', path: '/portfolio', label: 'Portfolio', icon: PieChart, hint: 'Optimizer' },
  { kind: 'page', path: '/research', label: 'Research lab', icon: FlaskConical, hint: 'Backtest' },
  { kind: 'page', path: '/tools', label: 'Tools', icon: Wrench, hint: 'Comps & validation' },
  { kind: 'page', path: '/settings', label: 'Settings', icon: SettingsIcon, hint: 'API & LLM' },
];

/** Stable id for keyboard highlight + aria wiring. */
function itemId(item: Item): string {
  return item.kind === 'page' ? `page:${item.path}` : `run:${item.run.run_id}`;
}

/** Case-insensitive substring match across the searchable text of an item. */
function matches(item: Item, q: string): boolean {
  if (!q) return true;
  const needle = q.toLowerCase();
  if (item.kind === 'page') {
    return `${item.label} ${item.hint} ${item.path}`.toLowerCase().includes(needle);
  }
  const p = item.run.property;
  return `${p.name} ${p.market} ${item.run.recommendation}`.toLowerCase().includes(needle);
}

export function CommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  const navigate = useNavigate();
  const dialogRef = useRef<HTMLDialogElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const listRef = useRef<HTMLUListElement | null>(null);
  const [query, setQuery] = useState('');
  const [runs, setRuns] = useState<CommitteeDecision[]>([]);
  const [runsError, setRunsError] = useState<string | null>(null);
  const [active, setActive] = useState(0);

  // Sync the native <dialog> open state with the `open` prop. showModal() gives us
  // the focus-trap + ::backdrop + Escape-to-close for free.
  useEffect(() => {
    const dlg = dialogRef.current;
    if (!dlg) return;
    if (open && !dlg.open) {
      dlg.showModal();
      setQuery('');
      setActive(0);
      // Autofocus the input after the dialog opens.
      requestAnimationFrame(() => inputRef.current?.focus());
    } else if (!open && dlg.open) {
      dlg.close();
    }
  }, [open]);

  // Fetch recent runs once each time the palette opens.
  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setRunsError(null);
    recentAnalyses()
      .then((data) => { if (!cancelled) setRuns(data); })
      .catch((e: unknown) => {
        if (!cancelled) setRunsError(e instanceof Error ? e.message : 'Failed to load recent runs.');
      });
    return () => { cancelled = true; };
  }, [open]);

  const pageResults = useMemo(() => PAGES.filter((p) => matches(p, query)), [query]);
  const runResults = useMemo<RunItem[]>(
    () => runs.map((run): RunItem => ({ kind: 'run', run })).filter((r) => matches(r, query)),
    [runs, query],
  );
  // Flat, ordered list the keyboard cursor walks (pages first, then runs).
  const flat = useMemo<Item[]>(() => [...pageResults, ...runResults], [pageResults, runResults]);

  // Keep the active index in range as results change.
  useEffect(() => {
    setActive((i) => (flat.length === 0 ? 0 : Math.min(i, flat.length - 1)));
  }, [flat.length]);

  const activate = useCallback((item: Item) => {
    onClose();
    if (item.kind === 'page') navigate(item.path);
    else navigate(`/runs/${encodeURIComponent(item.run.run_id)}`);
  }, [navigate, onClose]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive((i) => (flat.length === 0 ? 0 : (i + 1) % flat.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((i) => (flat.length === 0 ? 0 : (i - 1 + flat.length) % flat.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const item = flat[active];
      if (item) activate(item);
    }
    // Escape is handled by the native dialog's cancel event below.
  };

  // Scroll the highlighted row into view as the cursor moves.
  useEffect(() => {
    if (!open) return;
    const el = listRef.current?.querySelector<HTMLElement>('[aria-selected="true"]');
    el?.scrollIntoView({ block: 'nearest' });
  }, [active, open]);

  // The dialog fires `cancel` on Escape and `close` on backdrop dismissal in
  // supporting browsers — route both back through onClose so React stays in sync.
  const handleCancel = (e: React.SyntheticEvent<HTMLDialogElement>) => {
    e.preventDefault();
    onClose();
  };

  const activeId = flat[active] ? itemId(flat[active]) : undefined;

  return (
    <dialog
      ref={dialogRef}
      className="cmdk"
      aria-label="Command palette"
      onCancel={handleCancel}
      onClose={() => { if (open) onClose(); }}
      // Click on the backdrop (outside the inner box) closes.
      onClick={(e) => { if (e.target === dialogRef.current) onClose(); }}
    >
      <div className="cmdk-box" onKeyDown={onKeyDown}>
        <div className="cmdk-input-row">
          <Search className="ic" strokeWidth={2} aria-hidden="true" />
          <input
            ref={inputRef}
            className="cmdk-input"
            type="text"
            value={query}
            onChange={(e) => { setQuery(e.target.value); setActive(0); }}
            placeholder="Search deals, runs, pages…"
            aria-label="Search deals, runs, pages"
            role="combobox"
            aria-expanded="true"
            aria-controls="cmdk-list"
            aria-activedescendant={activeId}
            autoComplete="off"
            spellCheck={false}
          />
          <kbd className="kbd">Esc</kbd>
        </div>

        <ul className="cmdk-list" id="cmdk-list" role="listbox" aria-label="Results" ref={listRef}>
          {flat.length === 0 ? (
            <li className="cmdk-empty" role="presentation">
              {runsError ? runsError : 'No matches'}
            </li>
          ) : (
            <>
              {pageResults.length > 0 && (
                <li className="cmdk-group" role="presentation">Pages</li>
              )}
              {pageResults.map((p) => {
                const id = itemId(p);
                const selected = id === activeId;
                const Icon = p.icon;
                return (
                  <li
                    key={id}
                    id={id}
                    role="option"
                    aria-selected={selected}
                    className="cmdk-row"
                    onClick={() => activate(p)}
                    onMouseMove={() => setActive(flat.findIndex((f) => itemId(f) === id))}
                  >
                    <Icon className="ic" strokeWidth={2} aria-hidden="true" />
                    <span className="cmdk-label">{p.label}</span>
                    <span className="cmdk-meta">{p.hint}</span>
                    <CornerDownLeft className="enter" strokeWidth={2} aria-hidden="true" />
                  </li>
                );
              })}

              {runResults.length > 0 && (
                <li className="cmdk-group" role="presentation">Recent runs</li>
              )}
              {runResults.map((r) => {
                const id = itemId(r);
                const selected = id === activeId;
                const p = r.run.property;
                return (
                  <li
                    key={id}
                    id={id}
                    role="option"
                    aria-selected={selected}
                    className="cmdk-row"
                    onClick={() => activate(r)}
                    onMouseMove={() => setActive(flat.findIndex((f) => itemId(f) === id))}
                  >
                    <History className="ic" strokeWidth={2} aria-hidden="true" />
                    <span className="cmdk-label">{p.name}</span>
                    <span className="cmdk-meta">{p.market}</span>
                    <VerdictBadge value={String(r.run.recommendation)} />
                    <CornerDownLeft className="enter" strokeWidth={2} aria-hidden="true" />
                  </li>
                );
              })}
            </>
          )}
        </ul>

        <div className="cmdk-foot">
          <span><kbd className="kbd">↑</kbd><kbd className="kbd">↓</kbd> to navigate</span>
          <span><kbd className="kbd">↵</kbd> to open</span>
          <span><kbd className="kbd">Esc</kbd> to close</span>
        </div>
      </div>
    </dialog>
  );
}
