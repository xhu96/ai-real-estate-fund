# Product

## Register

product

## Users

Real-estate investors, analysts, and engineering reviewers evaluating the project as a portfolio piece. They arrive mid-workflow: load a deal, run the committee, read the verdict, drill into the workstreams that drove it. Secondary audience is hiring managers skimming screenshots — the first screen has to communicate "credible financial tool" in five seconds.

## Product Purpose

A deterministic institutional diligence engine with a dashboard surface: run a 77-workstream investment committee on a rental property, inspect scores, scenarios, risks, and the memo, and review past runs. The UI's job is to make dense quantitative output legible and trustworthy, with a bold, confident surface that still keeps the data the hero.

## Brand Personality

Neobrutalist and numerate. High-contrast, bold, and structural. Saturated pastel fields (a cyan content area, a yellow sidebar) ground white data cards framed in 2px near-black borders and hard offset shadows (no blur). Every "window" gets a color anchor: a tinted panel header and vivid hero tiles, with verdict states shown as flat saturated fills. Space Grotesk carries the display type; figures stay tabular. Confidence comes from committed color and chunky structure, not restraint, but the number is always first-class and the data bodies stay on white for legibility.

## Anti-references

- Soft/blurred shadows or glassmorphism: shadows are hard offset (`4px 4px 0`), surfaces are flat, no `backdrop-filter`.
- Gradients of any kind: flat color only. No gradient text, no gradient fills.
- All-white monotony: cards are not a sea of identical white rectangles; fields, headers, and hero tiles carry color.
- Thin hairline-only cards and timid one-accent restraint: borders are a committed 2px near-black, color is part of the system.
- Generic SaaS-admin blandness and AI tells: no bootstrap-blue-on-white, no side-stripe accent borders, no purple-blue gradient logos.

## Design Principles

1. **The number is the interface.** Scores, ratios, and dollar figures carry the page; bold tabular figures do the explaining before any chrome does.
2. **Verdicts read at a glance.** Recommendation states (BUY / NEGOTIATE / WATCHLIST / PASS) have one consistent, bold visual encoding (a colored fill + the label) everywhere they appear, never color alone.
3. **Structure is the decoration.** 2px near-black borders and hard offset shadows frame everything; the press of a button and the lift of a card are the motion. Flat fills, no gradients, no glow.
4. **Color grounds the data.** Saturated fields and tinted headers anchor white cards; color carries meaning and hierarchy (verdicts, hero stats), and dark text sits on every colored fill. Data tables stay on white for maximum legibility.
5. **Every state is designed.** Loading, empty, and error states get the same care as the happy path.

## Accessibility & Inclusion

WCAG 2.1 AA: body text ≥4.5:1, large text ≥3:1, visible focus states, full keyboard navigation, `prefers-reduced-motion` honored. Recommendation states never rely on color alone (always paired with the label text).
