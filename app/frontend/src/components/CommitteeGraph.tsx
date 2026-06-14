import { useEffect, useMemo, useRef, useState } from 'react';
import type { MouseEvent as ReactMouseEvent } from 'react';
import type { AgentFinding } from '../types';

const VERDICT: Record<string, { key: string; color: string; label: string }> = {
  BUY: { key: 'buy', color: 'var(--buy)', label: 'Buy' },
  NEGOTIATE: { key: 'negotiate', color: 'var(--neg)', label: 'Negotiate' },
  WATCHLIST: { key: 'watchlist', color: 'var(--watch)', label: 'Watchlist' },
  PASS: { key: 'pass', color: 'var(--pass)', label: 'Pass' },
};
const fallbackVerdict = { key: 'watchlist', color: 'var(--muted)', label: '—' };

const DOMAIN_ORDER = ['Acquisition', 'Income', 'Expenses', 'Debt', 'Condition', 'Market', 'Portfolio', 'Governance', 'Other'] as const;
const DOMAIN_RULES: Array<[string, string[]]> = [
  ['Acquisition', ['pric', 'sale comp', 'valu', 'acquisition', 'bid', 'basis']],
  ['Income', ['rent', 'tenant', 'lease', 'cash flow', 'cash-flow', 'income', 'occupanc', 'demand']],
  ['Expenses', ['expense', 'tax', 'insur', 'reserve', 'capex', 'operat', 'utilit']],
  ['Debt', ['debt', 'dscr', 'financ', 'refinanc', 'liquidit', 'coverage', 'loan']],
  ['Condition', ['condition', 'renovat', 'rehab', 'environment', 'title', 'legal', 'physical', 'inspect']],
  ['Market', ['market', 'neighbor', 'zoning', 'regulat', 'appreciat', 'submarket', 'demograph']],
  ['Portfolio', ['portfolio', 'exit', 'sponsor', 'allocation', 'concentrat']],
  ['Governance', ['data quality', 'data-quality', 'risk', 'bull', 'bear', 'stress', 'governance']],
];

function domainOf(name: string, role: string): string {
  const h = `${name} ${role}`.toLowerCase();
  for (const [domain, keys] of DOMAIN_RULES) if (keys.some((k) => h.includes(k))) return domain;
  return 'Other';
}

type Node = { x: number; y: number; r: number; color: string; colorKey: string; vlabel: string; name: string; conf: number; score: number; blurb: string };

const W = 900, H = 520, CX = 450, CY = 258, R = 196;

export function CommitteeGraph({ findings, overallScore, recommendation }: { findings: AgentFinding[]; overallScore: number; recommendation: string }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const reduced = useMemo(() => typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches, []);
  const [shown, setShown] = useState(reduced);
  const [tip, setTip] = useState<{ i: number; left: number; top: number } | null>(null);

  useEffect(() => {
    if (shown) return;
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setShown(true)));
    return () => cancelAnimationFrame(id);
  }, [shown]);

  const { nodes, sectors } = useMemo(() => {
    const chairIsCenter = (f: AgentFinding) => /chair|committee/i.test(f.agent_name);
    const ring = findings.filter((f) => !chairIsCenter(f));
    const byDomain = new Map<string, AgentFinding[]>();
    for (const f of ring) {
      const d = domainOf(f.agent_name, f.role ?? '');
      if (!byDomain.has(d)) byDomain.set(d, []);
      byDomain.get(d)!.push(f);
    }
    const domains = DOMAIN_ORDER.filter((d) => byDomain.has(d)).map((d) => ({ key: d, members: byDomain.get(d)!.sort((a, b) => a.score - b.score) }));
    const total = ring.length || 1;
    const gap = 0.05;
    const nodes: Node[] = [];
    const sectors: Array<{ key: string; lx: number; ly: number; anchor: string }> = [];
    let idx = 0;
    for (const dom of domains) {
      const span = (dom.members.length / total) * Math.PI * 2;
      const start = (idx / total) * Math.PI * 2 - Math.PI / 2 + gap / 2;
      const end = start + span - gap;
      const mid = (start + end) / 2;
      const lr = R + 30;
      sectors.push({
        key: dom.key,
        lx: CX + Math.cos(mid) * lr,
        ly: CY + Math.sin(mid) * lr,
        anchor: Math.cos(mid) < -0.3 ? 'end' : Math.cos(mid) > 0.3 ? 'start' : 'middle',
      });
      dom.members.forEach((f, j) => {
        const t = dom.members.length === 1 ? 0.5 : j / (dom.members.length - 1);
        const ang = start + (end - start) * t;
        const rad = R * (0.82 + (j % 2) * 0.14);
        const v = VERDICT[String(f.recommendation).toUpperCase()] ?? fallbackVerdict;
        const conf = Math.max(0, Math.min(1, Number(f.confidence) || 0.5));
        nodes.push({
          x: CX + Math.cos(ang) * rad,
          y: CY + Math.sin(ang) * rad,
          r: 6 + conf * 9,
          color: v.color,
          colorKey: v.key,
          vlabel: v.label,
          name: f.agent_name,
          conf,
          score: f.score,
          blurb: f.concerns?.[0] || f.thesis || f.positives?.[0] || '',
        });
      });
      idx += dom.members.length;
    }
    return { nodes, sectors };
  }, [findings]);

  function onEnter(i: number, e: ReactMouseEvent) {
    const wrap = wrapRef.current?.getBoundingClientRect();
    const nb = (e.currentTarget as SVGGElement).getBoundingClientRect();
    if (!wrap) return;
    const cxp = nb.left + nb.width / 2 - wrap.left;
    const cyp = nb.top + nb.height / 2 - wrap.top;
    let left = cxp + 16; if (left > wrap.width - 248) left = cxp - 240; if (left < 6) left = 6;
    let top = cyp - 12; if (top < 6) top = 6; if (top > wrap.height - 124) top = wrap.height - 124;
    setTip({ i, left, top });
  }

  const chair = VERDICT[String(recommendation).toUpperCase()] ?? fallbackVerdict;

  return (
    <div className="cst-wrap" ref={wrapRef}>
      <svg className="cst" viewBox={`0 0 ${W} ${H}`} role="img"
        aria-label={`Radial graph of ${nodes.length} investment-committee workstreams grouped by domain, each colored by its recommendation and sized by confidence, connected to the IC chair at the center.`}>
        {!reduced && (
          <line x1={CX} y1={CY} x2={CX} y2={CY - R - 14} stroke="var(--accent-line)" strokeWidth={1.5} opacity={0.16}
            style={{ transformOrigin: `${CX}px ${CY}px`, animation: 'sweepRot 16s linear infinite' }} />
        )}
        {[0.5, 0.78, 1].map((f) => (
          <circle key={f} cx={CX} cy={CY} r={R * f} fill="none" stroke="var(--border)" strokeWidth={1} opacity={0.5} />
        ))}

        {nodes.map((n, i) => (
          <line key={`e${i}`} className="edge" x1={CX} y1={CY} x2={n.x} y2={n.y}
            style={{ opacity: shown ? 0.16 : 0, transition: reduced ? 'none' : `opacity .5s ease ${i * 20}ms` }} />
        ))}

        {sectors.map((s) => (
          <text key={s.key} className="arc-label" x={s.lx} y={s.ly} textAnchor={s.anchor as 'start' | 'middle' | 'end'} dominantBaseline="middle">{s.key}</text>
        ))}

        {nodes.map((n, i) => (
          <g key={`n${i}`} className="node"
            style={{ opacity: shown ? 1 : 0, transform: shown ? 'none' : 'translateY(6px)', transition: reduced ? 'none' : `opacity .45s var(--ease) ${120 + i * 24}ms, transform .45s var(--ease) ${120 + i * 24}ms` }}
            onMouseEnter={(e) => onEnter(i, e)} onMouseLeave={() => setTip((t) => (t?.i === i ? null : t))}
            tabIndex={0} onFocus={(e) => onEnter(i, e as unknown as ReactMouseEvent)} onBlur={() => setTip(null)}>
            <g className="body">
              <circle cx={n.x} cy={n.y} r={n.r + 4} style={{ fill: n.color }} opacity={0.13} />
              <circle className="hit" cx={n.x} cy={n.y} r={n.r} style={{ fill: n.color }} stroke="var(--bg)" strokeWidth={2} />
            </g>
          </g>
        ))}

        <circle cx={CX} cy={CY} r={34} style={{ fill: chair.color, animation: reduced ? undefined : 'pulse 3.4s ease-in-out infinite' }} opacity={0.16} />
        <circle cx={CX} cy={CY} r={26} fill="var(--accent-tint)" style={{ stroke: chair.color }} strokeWidth={1.5} />
        <text x={CX} y={CY - 2} textAnchor="middle" fill="var(--ink)" fontSize={16} fontWeight={700} fontFamily="var(--font)" style={{ fontVariantNumeric: 'tabular-nums' }}>{overallScore.toFixed(1)}</text>
        <text x={CX} y={CY + 13} textAnchor="middle" className="chair-label" fontSize={9}>IC CHAIR</text>
      </svg>

      {tip && (
        <div className="cst-tooltip on" style={{ left: tip.left, top: tip.top }}>
          <div className="tn">{nodes[tip.i].name}<span className="vk" style={{ color: nodes[tip.i].color }}>{nodes[tip.i].vlabel}</span></div>
          <div className="tr">score {nodes[tip.i].score.toFixed(1)} · confidence {Math.round(nodes[tip.i].conf * 100)}%</div>
          {nodes[tip.i].blurb && <div className="tt">{nodes[tip.i].blurb}</div>}
        </div>
      )}
    </div>
  );
}

const LEGEND: Array<[string, string]> = [['Buy', 'var(--buy)'], ['Negotiate', 'var(--neg)'], ['Watchlist', 'var(--watch)'], ['Pass', 'var(--pass)']];

export function CommitteePanel({ findings, overallScore, recommendation }: { findings: AgentFinding[]; overallScore: number; recommendation: string }) {
  if (!findings || findings.length === 0) return null;
  return (
    <section className="panel constellation reveal">
      <div className="panel-h">
        <div className="t"><h2>Investment committee</h2><span className="hint">{findings.length} workstreams · IC chair synthesis</span></div>
        <div className="legend">
          {LEGEND.map(([label, color]) => (
            <span className="lg" key={label}><i style={{ background: color }} />{label}</span>
          ))}
          <span className="lg" style={{ color: 'var(--faint)' }}>node size = confidence</span>
        </div>
      </div>
      <CommitteeGraph findings={findings} overallScore={overallScore} recommendation={recommendation} />
    </section>
  );
}
