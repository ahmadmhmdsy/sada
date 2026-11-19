# Owner actions — what is left for you

Everything in the repository is done and verified; this page lists the work that **only the owner**
(or someone with the owner's accounts, hardware or money) can complete. The agent can prepare,
draft and check every item, but it cannot click an account page, receive a verification token, buy
a certificate or supply physical hardware.

Status legend: **P0 = do this week**, **P1 = this month**, **P2 = decide later**.
Track a box by changing `[ ]` to `[x]`. The two scheduled reminders (see the end) point back here.

| # | Action | Priority | Effort | Blocked by |
| --- | --- | --- | --- | --- |
| [A1](#a1--github-social-preview) | Upload the GitHub social preview | **P0** | 5 min | — |
| [A2](#a2--google-search-console--sitemap) | Verify Google Search Console, submit sitemap | **P0** | 20 min | your Google account |
| [A3](#a3--bing-webmaster-tools) | Verify Bing Webmaster Tools, submit sitemap | P1 | 10 min | A2 or your Microsoft account |
| [A4](#a4--launch-posts) | Distribution launch posts (one per venue) | P1 | 2–3 h | your accounts |
| [A5](#a5--code-signing-issue-18) | Buy/enable code signing (#18) | P1 | 2–10 days + cost | identity validation, CA |
| [A6](#a6--winget--chocolatey-after-signing) | Submit to Winget / Chocolatey | P2 | 1–2 h | A5 |
| [A7](#a7--microsoft-store-optional) | Microsoft Store listing (optional) | P2 | 1 day | A5 |
| [A8](#a8--clean-machine-acceptance-issue-17) | Clean-machine acceptance rows B–E (#17) | P1 | 1 day | physical machines |
| [A9](#a9--triage-dependabot-prs-36-57) | Triage the 22 Dependabot PRs (#36–#57) | P1 | 1–2 h | your review/merge decision |
| [A10](#a10--dialect-benchmark-corpus) | Find an Iraqi/Gulf/Levantine benchmark corpus | P2 | ongoing | outreach + licence |
| [A11](#a11--external-audit-sl-a-and-legal-optional) | External audit / SLA / legal review (optional) | P2 | weeks | budget |
| [A12](#a12--measurement-review) | Measure results in Search Console / GitHub | **P0** | 15 min monthly | A2 + 4–6 weeks |
| [A13](#a13--enable-github-discussions-optional) | Enable GitHub Discussions (optional) | P2 | 5 min | moderation capacity |

---

## A1 — GitHub social preview

**Why:** every link to the repository on social platforms currently shows a generic GitHub card.
The image is the first impression before anyone reads the README.

**Steps:**
1. Open <https://github.com/alshahia/sada/settings> → **General** → scroll to **Social preview**.
2. Upload `site/assets/social-card-en.png` (1200×630; for an Arabic-first audience
   `social-card-ar.png` also works — pick one, GitHub allows a single image).
3. Click **Save**, then share the repo URL in a private message to yourself and confirm the card.

**Done when:** the upload shows the card and a fresh share preview renders it.
**Note:** GitHub has no API for this setting, so it cannot be automated.

## A2 — Google Search Console + sitemap

**Why:** without Search Console you are blind to impressions, queries and indexing problems; this
is the only measurement channel the privacy-first site has.

**Steps:**
1. Open <https://search.google.com/search-console> → **Add property** → **URL prefix** and enter
   `https://alshahia.github.io/sada/`.
2. Choose **HTML tag** verification; copy the `<meta name="google-site-verification" ...>` line.
3. Send that line to the agent (or commit it yourself): it must go into `site/index.html` and
   `site/en/index.html` inside `<head>`. A `github.io` host cannot use DNS verification.
4. After the next deploy, click **Verify**.
5. Open **Sitemaps**, submit `https://alshahia.github.io/sada/sitemap.xml`.
6. In **URL Inspection**, request indexing for both `/` and `/en/` once.

**Done when:** the property is verified and the sitemap status is *Success*.

## A3 — Bing Webmaster Tools

**Why:** Bing indexes the site for Bing/Copilot, and its import from Search Console takes minutes.

**Steps:**
1. Open <https://www.bing.com/webmasters> → **Add site** → either **Import from Google Search
   Console** (recommended, after A2) or add `https://alshahia.github.io/sada/` with the same meta
   tag.
2. Submit `https://alshahia.github.io/sada/sitemap.xml` under **Sitemaps**.
3. Check **Site Explorer** for the two URLs.

**Done when:** site verified and sitemap accepted.

## A4 — Launch posts

**Why:** the repository and site are ready; discovery only compounds when real people see it.
GitHub search alone will not reach Arabic users who have never heard of Sada.

**Rules:** one post per venue, written for that venue, never copy-pasted everywhere; answer
comments for a day or two; link the **Arabic landing page** <https://alshahia.github.io/sada/> (not
only GitHub) so Arabic search and social previews work for you.

**Suggested order (read each venue's self-promotion rules first):**
1. **Show HN** — title in English, body explains the Arabic-first/offline problem honestly and
   mentions the benchmark + limits; link the English page. Post on a weekday morning US time.
2. **Reddit** — `r/Arabic`, `r/arabic`, `r/speechtech`, `r/Windows11`, `r/opensource`;
   one subreddit per post, Arabic text for the Arabic subreddits.
3. **Product Hunt / AlternativeTo** — free listing; AlternativeTo especially fits "offline
   alternative to cloud transcription".
4. **Arabic communities** — university CS groups, Arabic developer Telegram/Discord groups,
   local tech newsletters; ask first, do not spam.
5. **Awesome lists** (small PRs, not posts): `awesome-arabic`, `awesome-speech-recognition`,
   `awesome-whisper`, `awesome-tauri`, `awesome-windows-apps`.

**Done when:** at least 3 posts are live and each has its link recorded in the *Measurement* section.
**Watching for:** comments asking about SmartScreen/unsigned installer — answer with the checksum +
provenance steps and the signing plan (A5).

## A5 — Code signing (issue #18)

**Why:** SmartScreen's "Windows protected your PC" is the single biggest conversion blocker for
non-technical users, and Winget/Store submissions need a trusted publisher. The workflow is already
wired; it stays dormant until `SIGNING_ENABLED` is `true`.

**Steps:**
1. Choose a route: **Azure Trusted Signing** (cheapest for individuals, needs a verifiable identity
   and ~1–2 weeks validation) or an **OV code-signing certificate** from a CA.
2. Complete identity/organisation validation and buy the certificate/subscription.
3. Put the signing secrets into the repository as described in [SIGNING.md](SIGNING.md).
4. Set the repository variable `SIGNING_ENABLED=true`, then re-run the release workflow for a patch
   version (e.g. 3.9.1) and verify the signature on a clean machine.
5. Update the SmartScreen note in both READMEs and [DISCOVERABILITY.md](DISCOVERABILITY.md) once the
   signed build is published.

**Done when:** the published installer is signed, SmartScreen no longer warns on a clean machine,
and the README no longer carries the unsigned warning.
**Blocked by:** budget + identity validation (days, not hours). Ask the agent for the packet that
was already prepared.

## A6 — Winget / Chocolatey (after signing)

**Why:** Winget is the default "install software" path for many Windows users; it also provides
verifiable manifests and update automation.

**Steps (after A5):**
1. `winget install Microsoft.WingetCreate`, then `wingetcreate new` and point it at the signed
   installer URL and its SHA-256 from `SHA256SUMS.txt`.
2. Test the manifest locally: `winget install --manifest <file>`.
3. Open a PR to <https://github.com/microsoft/winget-pkgs> (one package per PR, follow the bot
   template). Chocolatey: create a package and push to <https://community.chocolatey.org>.
4. Add the install command to the README once accepted.

**Done when:** `winget install Sada` succeeds on a clean machine and the package page is live.
**Do not** submit before A5 — an unsigned publisher in Winget is a permanent bad first impression.

## A7 — Microsoft Store (optional)

**Why:** extra trust and discoverability for non-technical users; useful after signing.

**Steps:** create a Partner Center account (individual ~$19 one-time), package the MSIX or submit
the signed installer, complete the age-rating and privacy questionnaires (the privacy policy URL is
`https://github.com/alshahia/sada/blob/master/PRIVACY.md`), and note that Store distribution
replaces the NSIS installer for Store users.

**Done when:** the listing is approved and the Store install launches with Arabic defaults.

## A8 — Clean-machine acceptance (issue #17)

**Why:** the release evidence covers the developer machine; enterprise buyers ask for rows on
*their* hardware profiles (no GPU, old CPU, 4 GB RAM, Windows 11 ARM, locked-down EDR).

**Steps:**
1. Open [ACCEPTANCE.md](ACCEPTANCE.md), rows B–E.
2. For each row: clean Windows VM or physical machine, install from the MSI or offline NSIS,
   transcribe the 30-second Arabic sample, open/save a project, export PDF, then run
   `scripts/verify-release.ps1`.
3. Record the result, machine spec, OS build and date directly in the table; open an issue if a row
   fails.
4. Add the hardware rows to the release notes or acceptance evidence.

**Done when:** rows B–E are filled with a pass/fail and evidence (screenshot or log) is attached.
**Blocked by:** access to the physical machines / VMs.

## A9 — Triage Dependabot PRs (#36–#57)

**Why:** 22 dependency PRs are open; the longer they sit the harder the upgrade and the larger the
audit surface.

**Steps:**
1. Group them: GitHub Actions (safe, merge after CI), frontend npm (run `pnpm build` + `pnpm test`
   locally first), Rust/cargo (run `cargo test --release`), server crates.
2. Merge low-risk groups one at a time; close PRs that are superseded by a major bump with a comment.
3. For majors that need code changes (e.g. Tauri plugins), open a tracking issue instead of merging
   blind.
4. Ask the agent to run the triage and prepare a merge order when you are ready.

**Done when:** no Dependabot PR is older than one release cycle and CI is green on each merge.

## A10 — Dialect benchmark corpus

**Why:** the honest benchmark says Iraqi, Gulf and Levantine are unmeasured. A small licensed
corpus would turn the project's biggest content gap into its strongest evidence — and the best
Arabic SEO asset.

**What to ask for:** 20–60 clips (30–120 s each), human transcripts, speaker consent, and a written
licence allowing commercial use and publication of aggregate metrics. Broadcasters, universities,
podcasters and call-centre vendors are realistic sources.

**Steps:**
1. Send a short email: "we are building a free offline Arabic transcription tool; we publish only
   aggregate error rates, never audio or transcripts; would you license a small corpus for
   benchmarking?"
2. If yes, put the clips behind the existing harness in `benchmarks/arabic-asr/` (do not commit the
   audio unless the licence allows it; commit the manifest + results).
3. Update `docs/MODELS-DECISIONS.md`, the README benchmark table and the site copy.

**Done when:** a licensed Gulf/Iraqi/Levantine slice exists and the "not measured" caveat shrinks.

## A11 — External audit / SLA / legal (optional)

**Why:** enterprise procurement often asks for an independent security assessment, an SLA and a
support contract. This is a business decision, not a repository task.

**Steps:** decide whether to pursue paid support; if yes, obtain a quote for a lightweight pentest
of the desktop app (scope: installer, local HTTP surface, MCP stdio, update path), and have a lawyer
review the MIT fork attribution and the FFmpeg GPLv3 distribution notice. Record the outcome in
[PRODUCTION-READINESS.md](PRODUCTION-READINESS.md).

**Done when:** a decision (with or without documents) is recorded; no repository change is required
to decline.

## A12 — Measurement review

**Why:** the site has no analytics by design, so the only honest signal is Search Console, Bing and
GitHub traffic/download counts. Review monthly and decide whether to continue investing.

**Steps (15 minutes, monthly):**
1. Search Console → **Performance**: impressions, clicks, top queries (expect Arabic long-tail
   first), average position; check **Pages** for indexing problems.
2. Bing Webmaster → same, plus AI-crawler visibility.
3. GitHub → **Insights → Traffic** (referrers, popular content, clones) and **Releases** (download
   counts per asset: NSIS vs offline vs MSI tells you which audience found you).
4. Record the numbers and one decision in the *Measurement* section of
   [DISCOVERABILITY.md](DISCOVERABILITY.md).

**Done when:** the first baseline is recorded (after A2 + 4–6 weeks) and a monthly review is on the
calendar.
**Decision rule:** continue if organic impressions and release downloads grow; if only stars grow,
fix the landing-page conversion before spending more on distribution.

## A13 — Enable GitHub Discussions (optional)

**Why:** a public Q&A page adds indexed long-tail Arabic content with no privacy cost.

**Steps:** repository → Settings → General → **Features** → tick **Discussions**; create categories
"أسئلة / Q&A", "الأفكار / Ideas", "أظهر إعدادك / Show your setup". Add the link to the README once it
has a few answers.

## Release sign-off (every release)

The agent can prepare version bumps, notes, the build, provenance and verification. The owner's
part each release is: approve the notes (bilingual), decide whether to ship, approve any signing
step, and tag the release after the release branch is green. The release workflow requires
`docs/releases/v<version>.md`, so the notes are always reviewable before tagging.

## Scheduled reminders

- **2026-11-21** — quick wins: A1 (social preview), start A2/A3 (Search Console/Bing), decide A5
  (signing route).
- **2026-12-19** — measurement baseline: A12 (Search Console/Bing/GitHub numbers), check whether
  A5/A6 unblocked Winget, and whether A10 outreach got any answer.

The agent can also do on request: draft the launch posts (A4), prepare the Winget manifests (A6),
triage the Dependabot PRs (A9), write the corpus outreach email (A10), run the clean-machine
acceptance script (A8) on any machine you connect, and re-check all repository facts before a
release.
