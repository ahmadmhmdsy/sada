# Echo 4.0 preview — review guide

**Status: non-shipping preview, prepared 2026-11-23 on branch `design/echo-4.0-preview`.
Nothing here is approved, merged or released.** The direction itself is
[echo-identity-4.0.md](../echo-identity-4.0.md); this branch lets the owner see the first migration
step from brief §8, not the finished identity.

## What the branch changes (product code: 2 files)

| File | Change |
| --- | --- |
| `desktop/src/globals.css` | Paper-and-ink token layer scoped to `html[data-echo-preview]`: the brief's §3 ramp and a remap of every existing semantic token (background, primary, borders, sidebar, shadows, selection, scrollbar). No layout, spacing, radius, copy or component change. |
| `desktop/src/bootstrap.tsx` | Sets `data-echo-preview` on `<html>` when the build is started with `VITE_ECHO_PREVIEW=true`. Default builds never set it, so the shipped look is untouched. |
| `docs/design/ui-decisions/ECHO-PREVIEW.md`, `echo-preview.html` | This guide and the static review board (palette, contrast, motif, type scale, mini composition). |

**Deliberately not in this branch:** rail move to the reading start, ink window chrome, wordmark,
in-app rings/waveform, settings restyle, icons, installer/OG artwork, dark theme. Those are later
steps and each needs its own review.

## How to view the app with the flag

```powershell
cd desktop
$env:VITE_ECHO_PREVIEW = 'true'
pnpm dev                 # browser dev
# or: pnpm exec tauri dev  # real window
```

Remove the variable (or set it to `false`) and restart to get the current palette back. The flag is
build-time, not a user preference; it is never exposed in Settings and a shipped installer cannot
turn it on.

Keep the OS in **light mode** while previewing — dark theme is out of scope for this pass, as the
brief says (no half-migrated dark ramp).

## Static board

Open [echo-preview.html](echo-preview.html) in any browser for the same tokens, the contrast pairs,
the concentric-arc motif and a CSS-only mini composition. It needs no server and no build.

## What to judge (and report back)

1. **Temperature.** Does the paper canvas read calmer and less "chat app" than the current neutral
   grey? Is it too warm for an Arabic-first tool?
2. **Signal discipline.** Terracotta appears on at most one primary action per screen plus the motif.
   Does it work as a signal without reading as a theme?
3. **Ink rail.** The token layer already paints the sidebar ink; the rail is still on the old side.
   Is the ink direction right to design the rail restyle around, or too heavy next to paper?
4. **Arabic reading.** Body 14–15 px at 1.7 line-height on `#FBF8F2`; timestamps tabular and 11–12 px.
   Is the transcript comfortable at arm's length?
5. **Motif.** Concentric arcs that decay from a solid centre + a 10-bar footline. Is this a
   recognisable direction worth building the shell around?
6. **Trust.** Does any of it weaken the literal privacy line? It must not be restyled into a badge.

Report the exact screen and what is wrong (e.g. "Settings → Models, disabled button invisible on
paper"). Components the brief did not audit can have weak pairs in this token-only pass; that is
expected and exactly what review is for.

## Contrast pairs worth knowing while reviewing

| Pair | Ratio | Rule |
| --- | --- | --- |
| `#17140F` ink-900 on `#FBF8F2` paper | 17.1:1 | primary text ✓ |
| `#7A7164` ink-500 on paper | 4.6:1 | secondary text, ≥14 px only ✓ |
| `#A94E2F` signal-600 on paper | 5.2:1 | links, primary CTA, focus ✓ |
| `#C2603F` signal-500 on paper | 3.9:1 | decorative and ≥24 px text only — never small text |
| `#3F7D5F` verify-700 on paper | 4.6:1 | trust check icon + its line ✓ |
| paper-0 on signal-600 | 5.5:1 | button label ✓ |

## What "approve" means

- **Approve in principle** → keep the branch as the base for the 4.0 token/shell work after the
  five-user gate; still nothing ships and the flag stays off in releases.
- **Reject** → close the PR without merging; the product change is one CSS block + one `if` and is
  reverted by deleting the branch.
- **Iterate** → leave line notes on the PR; palette values are proposals, not final (brief §3).
