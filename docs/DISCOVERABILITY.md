# Discoverability and search optimization

How people find Sada — and the honest, owner-independent work that keeps the repository and the
landing page discoverable. This is a living checklist, not a growth-hacking manual: the project
makes no telemetry, no analytics and no third-party trackers, and nothing here depends on them.

Related: [README.md](../README.md) · [README.ar.md](../README.ar.md) · [site/](../site) ·
[PRODUCTION-READINESS.md](PRODUCTION-READINESS.md) · [SIGNING.md](SIGNING.md)

## What is already in the repository

| Surface | What it does |
| --- | --- |
| **GitHub About** | Keyword-first description, 20 topics, homepage URL and the bilingual READMEs; the GitHub search ranking reads all of them. |
| **README (EN + AR)** | Keyword-bearing headings and first paragraph, screenshots with descriptive alt text, install/verify steps, measured Arabic benchmark, comparison table, 12-question FAQ, documentation hub and one tasteful star request. |
| **Self-hosted badges** | Static SVG badges under `docs/media/badges/` so the README makes **no third-party image request** (no shields.io tracking of readers). |
| **Landing page** | Bilingual (Arabic at `/sada/`, English at `/sada/en/`), per-page titles and descriptions, canonical + hreflang, Open Graph/Twitter cards, JSON-LD (`SoftwareApplication`, `FAQPage`, `WebSite`), font preloads and a custom bilingual 404. |
| **Social cards** | 1200×630 PNG cards (`site/assets/social-card-ar.png`, `social-card-en.png`) used by Open Graph and Twitter; sources and a rebuild script are committed. |
| **Crawl files** | `site/robots.txt` (allow all, sitemap), `site/sitemap.xml` (both pages with hreflang), `site/llms.txt` + root `llms.txt` for AI agents. |
| **Guard** | `node scripts/seo/check-seo.mjs` fails if titles/descriptions, JSON-LD, OG dimensions, hreflang, sitemap, README links or version references drift. |

Regenerate the share assets after a brand change (requires local Edge or Chrome):

```powershell
pwsh -File scripts/seo/build-share-assets.ps1   # cards + Apple touch icon + 512px PNG
node scripts/seo/check-seo.mjs                  # metadata and link guard
```

## Owner-only actions (cannot be automated from the repository)

These need a person with access to the account or the community, and are deliberately left out of
the agent's scope. They are ordered by impact per effort.

1. **Upload the GitHub social preview.** Repository → *Settings → General → Social preview* →
   upload `site/assets/social-card-en.png` (1200×630, 117 KB). GitHub has no API for this setting;
   it is the image every link to the repository shows on social platforms.
2. **Google Search Console.** Add a *URL prefix* property for
   `https://alshahia.github.io/sada/`; choose the HTML-tag verification. Send the verification
   token to the maintainer so the tag is committed to both pages (one line in each `<head>`),
   then verify and submit `https://alshahia.github.io/sada/sitemap.xml`. A `github.io` host cannot
   be verified by DNS.
3. **Bing Webmaster Tools.** Import the verified property from Search Console (or verify with the
   same meta tag) and submit the sitemap; Bing also feeds ChatGPT search and other AI crawlers.
4. **Enable GitHub Discussions** (optional, *Settings → Features*) if there is capacity to moderate
   Arabic questions. A public Q&A page adds indexed, long-tail Arabic content at no privacy cost.
5. **Distribution posts** where self-promotion is allowed — one per venue, written for the venue,
   never cross-posted as-is: Show HN, `r/Arabic`, `r/arabic`, `r/speechtech`, `r/Windows11`,
   `r/opensource`, relevant Arabic developer and university communities, Product Hunt and
   AlternativeTo. Link the **landing page**, not only the repository, so the Arabic page earns the
   traffic.
6. **Awesome lists / directories** (a small PR each): `awesome-arabic`, `awesome-speech-recognition`,
   `awesome-whisper`, `awesome-tauri`, `awesome-windows-apps`, `awesome-privacy`. Read each list's
   contribution rules first; do not submit to general "free download" directories.
7. **Package managers (later, owner decision).** Winget (PR to `microsoft/winget-pkgs`) and
   Chocolatey are realistic once the installer is code-signed; both improve discoverability for
   Windows users and make installs verifiable. Do not submit before signing to avoid a permanent
   "untrusted publisher" first impression.
8. **Corporate/education channels.** A short Arabic one-pager for universities, newsrooms and
   ministries; link `docs/ENTERPRISE-DEPLOYMENT.md` and the MSI. These are the buyers for the
   managed-deployment work.
9. **Benchmark partners.** Iraqi, Gulf and Levantine broadcasters, universities and podcasters who
   can license a small transcription corpus would unlock the missing dialect benchmark — the single
   strongest SEO/credibility asset still on the table.

## Measurement

There is **no analytics on the site by design**. Measure from the platforms:

- **Search Console:** impressions, clicks, top queries (expect Arabic long-tail first), average
  position; check after 4–6 weeks. Record the baseline once verified — no numbers are invented here.
- **Bing Webmaster Tools:** same, plus AI-crawler visibility.
- **GitHub Insights → Traffic:** referrers, popular content, clones; **Releases:** download counts
  per asset (NSIS vs offline vs MSI tells you which audience found you).
- **Stars/forks:** a lagging signal; do not optimize for them directly.

Decision date: review monthly after Search Console is verified. Continue if organic impressions and
release downloads grow; if only stars move, fix the landing page conversion before spending more on
distribution.

## Maintenance checklist (per release)

1. Bump the version in README install lines, both READMEs' "release" references, site footer,
   JSON-LD `softwareVersion`, `llms.txt` files and `CITATION.cff`.
2. Update `site/sitemap.xml` `lastmod` for both pages.
3. Re-run `node scripts/seo/check-seo.mjs` and `pwsh -File scripts/seo/build-share-assets.ps1`
   only if branding changed (version changes do not affect the cards).
4. Add the release notes under `docs/releases/`; keep the GitHub release body bilingual.
5. After deploy, open both pages with a local browser and confirm the cards render
   (`https://alshahia.github.io/sada/` and `/en/`).

## Deliberately not done

Rejected by the council as either dishonest or incompatible with the project's privacy posture:

- **Third-party badge/tracker images** (shields.io and friends) — every README view would ping a
  third party; the static SVGs do the same job without the request.
- **Fake `aggregateRating` / reviews / download counts** in JSON-LD or copy — a guarantee of manual
  actions and lost trust.
- **Keyword stuffing, hidden text, doorway pages, city/landing-page farms, cloaking** and paid
  backlink schemes.
- **Duplicate Arabic pages for every dialect** — one canonical Arabic page with honest scope beats
  five thin pages.
- **A PWA manifest/service worker and a "web app" version** — Sada is a desktop app; a fake web
  version would compete with the real product for the wrong queries.
- **Google Analytics or any third-party script** on the landing page.
