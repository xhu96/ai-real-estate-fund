import { useCallback, useEffect, useState, type ReactNode } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, LineChart, History, Network, PieChart, FlaskConical, Wrench, Settings as SettingsIcon, Search } from 'lucide-react';
import { apiBase } from '../api/client';
import { CommandPalette } from './CommandPalette';

type NavItem = { path: string; label: string; icon: typeof LayoutDashboard };
const groups: Array<{ label: string; items: NavItem[] }> = [
  { label: 'Workspace', items: [
    { path: '/', label: 'Overview', icon: LayoutDashboard },
    { path: '/analyze', label: 'Analyze deal', icon: LineChart },
    { path: '/runs', label: 'Runs', icon: History },
    { path: '/committee', label: 'Committee', icon: Network },
  ] },
  { label: 'Fund', items: [
    { path: '/portfolio', label: 'Portfolio', icon: PieChart },
    { path: '/research', label: 'Research lab', icon: FlaskConical },
    { path: '/tools', label: 'Tools', icon: Wrench },
    { path: '/settings', label: 'Settings', icon: SettingsIcon },
  ] },
];

/** Breadcrumb section label for the appbar, derived from the current path's leading segment. */
const sectionLabels: Array<[RegExp, string]> = [
  [/^\/analyze/, 'Analyze'],
  [/^\/runs/, 'Runs'],
  [/^\/committee/, 'Committee'],
  [/^\/portfolio/, 'Portfolio'],
  [/^\/research/, 'Research'],
  [/^\/tools/, 'Tools'],
  [/^\/settings/, 'Settings'],
];
function sectionLabelFor(pathname: string): string {
  for (const [pattern, label] of sectionLabels) if (pattern.test(pathname)) return label;
  return 'Overview';
}

function BrandMark() {
  return (
    <svg className="mark" viewBox="0 0 38 38" fill="none" aria-hidden="true">
      <rect x="1" y="1" width="36" height="36" rx="7" fill="#807dfa" stroke="#16151f" strokeWidth="2" />
      <path d="M10 26V16l9-6 9 6v10" stroke="#16151f" strokeWidth="2.2" strokeLinejoin="round" strokeLinecap="round" />
      <path d="M15 26v-6h8v6" stroke="#16151f" strokeWidth="2.2" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}

function apiHost(): string {
  const base = apiBase();
  if (!base) return 'auto · proxy'; // same-origin: dev proxy forwards to the backend
  try { return new URL(base).host; } catch { return 'local'; }
}

export function Layout({ children }: { children: ReactNode }) {
  const { pathname } = useLocation();
  const [paletteOpen, setPaletteOpen] = useState(false);
  const closePalette = useCallback(() => setPaletteOpen(false), []);

  // Global Cmd/Ctrl+K opens the command palette from anywhere in the app.
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        setPaletteOpen((v) => !v);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  // Close the palette on any route change (selecting a result, or navigating elsewhere).
  useEffect(() => { setPaletteOpen(false); }, [pathname]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <BrandMark />
          <div>
            <div className="name"><b>Real Estate</b> <span>Fund</span></div>
            <div className="sub">Diligence Engine</div>
          </div>
        </div>

        <nav className="nav" aria-label="Main">
          {groups.map((group) => (
            <div className="nav-group" key={group.label}>
              <div className="nav-label">{group.label}</div>
              {group.items.map(({ path, label, icon: Icon }) => (
                // NavLink sets aria-current="page" on the active <a> — the existing nav CSS keys off that.
                <NavLink key={path} to={path} end={path === '/'}>
                  <Icon className="ic" strokeWidth={2} aria-hidden="true" />
                  {label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="side-foot">
          <div className="row"><span className="status-dot" aria-hidden="true" /> Engine ready</div>
          <div className="meta">77 deterministic workstreams · 4 LLM analysts · educational software, not advice</div>
        </div>
      </aside>

      <div className="main">
        <header className="appbar">
          <div className="crumb">Fund <span className="sep">/</span> <b>{sectionLabelFor(pathname)}</b></div>
          <button
            type="button"
            className="appbar-search"
            onClick={() => setPaletteOpen(true)}
            aria-haspopup="dialog"
            aria-keyshortcuts="Meta+K Control+K"
          >
            <Search className="ic" strokeWidth={2} aria-hidden="true" />
            <span className="ph">Search deals, runs, pages…</span>
            <kbd className="kbd">⌘K</kbd>
          </button>
          <span className="env" title="API endpoint">{apiHost()}</span>
        </header>
        <main className="content">{children}</main>
      </div>
      <CommandPalette open={paletteOpen} onClose={closePalette} />
    </div>
  );
}
