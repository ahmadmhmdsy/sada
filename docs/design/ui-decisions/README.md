# Sada UI decision boards

Visual prototypes for the four decisions left open by the [v3.9.0 UI/UX critique](../../UI-UX-REVIEW.md) and the Qiyas council. The point is to make each decision judgeable by looking, not by reading another report: every board shows the before/after fragment, user impact, honest build effort, risk, and what the choice unlocks later.

Open [index.html](index.html) in a browser, or read the PNGs in [shots/](shots/).

## The recommended bundle

| # | Question | Recommended | Effort | Risk | Why |
|---|----------|-------------|--------|------|-----|
| Q1 | Which repair family leads? | **Trust & failure recovery first** (then the finish line) | ~2 days lead, ~6 days for all four | Low | Every later screen inherits the failure language; the privacy line lands where the decision happens |
| Q2 | How much now? | **Wave 1 only**, then a five-user gate | 7–8 focused days | Low | Keeps the test clean and the re-critique interpretable; Wave 2 waits for the numbers |
| Q3 | How far from the clone? | **Restrained echo layer now**, full identity briefed for 4.0 | 2–3 days incremental | Low–medium | Fixes the RTL shell without a rebrand; token-level and reversible |
| Q4 | Which trust sentence? | **Scoped two-sentence copy** | 0.5–1 day | Low | The only version that stays true on the first-run download screen and after it |

Total for 3.10 (Wave 1 + echo layer): **7–8 focused days**. Wave 2 (3.11): **3–4 more**. The 4.0 identity is briefed after the measurement gate, not before.

## Boards

- `00-overview.html` — all four answers, the sequence 3.10 -> gate -> 3.11 -> 4.0, long-run rationale
- `01-q1-priority.html` — trust & recovery, finish line, settings/a11y, Arabic typography, each with a before/after fragment
- `02-q2-scope.html` — Wave 1 only vs. three fixes vs. two waves back to back, with timelines and deferred scope
- `03-q3-identity.html` — today’s borrowed shell, the restrained echo layer (recommended for 3.10), and the 4.0 concept
- `04-q4-trust.html` — hidden vs. absolute vs. scoped wording, shown at the drop point and on first run, with a claim audit and approved Arabic copy

Screenshots are rendered at 1440px width with headless Chrome, using the app’s bundled IBM Plex Sans Arabic and the 3.9.0 design tokens. Windows in Q3 are simplified to ~620px logical width for legibility; layout, colour, type and affordances are faithful.

## What these are and are not

These are **decision aids**, not implementation specs. They approximate the shipped UI closely enough to judge direction, density and copy, but they are static HTML with hand-built fragments. Any chosen direction still goes through the real components, tokens and i18n pipeline; estimates are focused build time (±30%), excluding review and release overhead.

## If the recommendation is approved

1. Q4 copy lands with Q1’s trust/recovery work (one pass, not two).
2. Q3’s echo layer is implemented as token and layout changes inside the existing shell, not as a new design system.
3. 3.10 stops at the five-user test; do not start Wave 2 before the numbers.
4. The 4.0 identity brief is written after positioning, using the echo motif already introduced.
