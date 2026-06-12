import type { ReactNode } from 'react';
import type { Page } from '../App';

const nav: Array<[Page, string]> = [
  ['dashboard', 'Overview'],
  ['analyze', 'Analyze'],
  ['runs', 'Runs'],
  ['portfolio', 'Portfolio'],
  ['research', 'Research'],
  ['settings', 'Settings'],
];

export function Layout({ page, onPageChange, children }: { page: Page; onPageChange: (page: Page) => void; children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-name">AI Real Estate Fund</div>
          <div className="brand-sub">Institutional diligence</div>
        </div>
        <nav className="nav" aria-label="Main">
          {nav.map(([key, label]) => (
            <button key={key} aria-current={page === key ? 'page' : undefined} onClick={() => onPageChange(key)}>
              {label}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">77 deterministic workstreams · educational software, not advice</div>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
