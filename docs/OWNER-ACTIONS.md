# Owner actions — what is left for you

Everything in the repository is done and verified; this page lists the work that **only the owner**
(or someone with the owner's accounts, hardware or money) can complete. The agent can prepare,
draft and check every item, but it cannot click an account page, receive a verification token, buy
a certificate or supply physical hardware.

Status legend: **P0 = do this week**, **P1 = this month**, **P2 = decide later**.
Track a box by changing `[ ]` to `[x]`. The scheduled reminders (see the end) point back here.

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
| [A9](#a9--triage-dependabot-prs-36-57) | Triage the 22 Dependabot PRs (#36–#57) | P1 | done 2026-11-21 (20 merged, #44 → #68, #53 held) | — |
| [A10](#a10--dialect-benchmark-corpus) | Find an Iraqi/Gulf/Levantine benchmark corpus | P2 | ongoing | outreach + licence |
| [A11](#a11--external-audit-sl-a-and-legal-optional) | External audit / SLA / legal review (optional) | P2 | weeks | budget |
| [A12](#a12--measurement-review) | Measure results in Search Console / GitHub | **P0** | 15 min monthly | A2 + 4–6 weeks |
| [A13](#a13--enable-github-discussions-optional) | Enable GitHub Discussions (optional) | P2 | 5 min | moderation capacity |
| [A14](#a14--tag-v3100) | Tag v3.10.0 and verify the release | **P0** | done 2026-11-19, verified 2026-11-21 | — |
| [A15](#a15--authorise-the-two-step-zero-tests) | Authorise the two Step Zero tests (read-aloud, Arabic subtitle burn-in) | P1 | done 2026-11-21 (B pass, A fail) | — |
| [A16](#a16--open-the-p7-milestone-and-issues) | Open the P7 milestone and FC-1…FC-9 issues | P1 | done 2026-11-19 | — |

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

**Status (2026-11-21, done).** Reviewed by a review room and **executed the same day** —
[execution report](reviews/2026-11-21-dependabot-merge/execution-report.md), [triage](DEPENDABOT-TRIAGE.md).
20 of 20 cleared PRs merged in four batches (npm, root Rust, server, workflows last); the four predicted
conflict points (#54, #48, #40, #46) were rebased and re-checked before merging. **#44** was closed (it could
not compile: `utoipa-swagger-ui` 10.0.2 pulls `utoipa` 6 while the server pinned 5) and replaced by **#68**,
the coordinated `utoipa` 5 to 6 upgrade (`utoipa` 6.0.0, `utoipa-axum` 0.3.0, `utoipa-swagger-ui` 10.0.2),
which is merged. **#53** remains open and held for its Tauri installer gate before v3.11.0. Final master
`c2b8012`, final CI green; **no tag, version bump, release or `release.yml` dispatch** — v3.10.0 is
unchanged.

**Steps:**
1. Group them: GitHub Actions (safe, merge after CI), frontend npm (run `pnpm build` + `pnpm test`
   locally first), Rust/cargo (run `cargo test --release`), server crates.
2. Merge low-risk groups one at a time; close PRs that are superseded by a major bump with a comment.
3. For majors that need code changes (e.g. Tauri plugins), open a tracking issue instead of merging
   blind.
4. ~~Ask the agent to run the triage and prepare a merge order~~ — done: batches and commands are in [DEPENDABOT-TRIAGE.md](DEPENDABOT-TRIAGE.md).

**Done when:** no Dependabot PR is older than one release cycle and CI is green on each merge. Met for 20 of 22 on 2026-11-21 (all merge CI green); #53 is the deliberate exception, held to its Tauri installer gate before v3.11.0.

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

## A14 — Tag v3.10.0

**Done 2026-11-19, verified 2026-11-21.** The owner authorised the tag in the "Docs commit and push
then A14 then A15" instruction, so the release was tagged and verified exactly as this action
described; code signing stayed dormant (unsigned build, owner decision).

**Result:**
- Tag `v3.10.0` (`ab6b1dea71494c66df7d73541e29dbd7b2f88abf`) points at release commit `be27bd5`.
- Release workflow [44526120606](https://github.com/alshahia/sada/actions/runs/44526120606) green
  (44m49s), publishing [release v3.10.0](https://github.com/alshahia/sada/releases/tag/v3.10.0) on
  2026-11-19T13:24:05Z with the Arabic notes from [releases/v3.10.0.md](releases/v3.10.0.md).
- Assets: `Sada_3.10.0_x64-setup.exe` (44,942,730 B), `Sada_3.10.0_x64-setup-offline.exe`
  (262,848,448 B), `Sada_3.10.0_x64_en-US.msi` (70,942,720 B), `SHA256SUMS.txt`,
  `sbom-cyclonedx.json`, `THIRD-PARTY-NOTICES.md`, `NOTICE`, `LICENSE`.
- Re-downloaded all three installers on 2026-11-21; each SHA-256 matches its `SHA256SUMS.txt` line.
- `gh attestation verify` succeeds for the default and offline installers: the Sigstore bundle names
  `.github/workflows/release.yml@refs/tags/v3.10.0` and the tag's commit `be27bd5`.
- Docs guard and site deploy were green on the same source before tagging; nothing in this step
  changed app code, dependencies or version.
- Remaining human step: smoke-test the downloaded installer on a clean machine — tracked separately
  as A8 (clean-machine acceptance), not part of A14.

## A15 — Authorise the two Step Zero tests

**Done 2026-11-21.** The owner authorised the tests in the "then A14 then A15" instruction, so both
ran report-only and are in the repository with dated verdicts:

- **Step Zero B (subtitle burn-in) — PASS 5/5, tested 2026-11-19.** The bundled FFmpeg 9.0.2
  (libass/fribidi/harfBuzz) burned five 720p clips with correct Arabic shaping, RTL order,
  diacritics, mixed Latin and digits. One caveat for native typography review (percent placement,
  bracket mirroring). Report: [STEP-ZERO-B-BURN-IN.md](STEP-ZERO-B-BURN-IN.md).
- **Step Zero A (read-aloud, Habibi-TTS) — FAIL, tested 2026-11-21.** The Python-only runtime fails
  the "no Python at runtime" criterion outright; CPU RTF 58–67 against a ≤ 3.0 limit; GPU mean 0.87
  but 3/10 clips over 1.0 (max 1.15); the native-listener naturalness score was not evaluated (no
  listener available). Quality itself was good: MSA re-transcription drift 0.0 %, Iraqi raw CER
  3.6 % mean, and the Apache-2.0 licences/1.26 GiB checkpoints are suitable. Report:
  [STEP-ZERO-A-READ-ALOUD.md](STEP-ZERO-A-READ-ALOUD.md).

**Decision:** read-aloud keeps its no-go for this cycle — no TTS code, model or UI in v3.11.
Re-check needs a non-Python runtime proven on these checkpoints (candidates: ONNX exports, the
Apache-2.0 community `audio.cpp` GGUF port — neither tested), plus a native listener and new speed
measurements. The burned-in-subtitle result is a gated candidate for the next UI wave after the
five-user gate.

**Optional owner action:** the ten test WAVs are preserved on this host (scratch, not committed);
listen to them if you want to judge naturalness yourself. Nothing else is needed from you — the
test results are recorded either way.

## A16 — Open the P7 milestone and issues

**Done 2026-11-19.** gh is authenticated as `alshahia`. Milestone [P7 — parity, proof & platform #8](https://github.com/alshahia/sada/milestone/8) contains nine issues, [#58](https://github.com/alshahia/sada/issues/58) (FC-1) through [#66](https://github.com/alshahia/sada/issues/66) (FC-9), each with its acceptance block, gate and evidence links. ROADMAP, [P7-PLAN.md](P7-PLAN.md) and this page carry the real numbers. FC-1 and FC-9 close when the pending docs commit lands; no tag or release is involved.

## Release sign-off (every release)

The agent can prepare version bumps, notes, the build, provenance and verification. The owner's
part each release is: approve the notes (bilingual), decide whether to ship, approve any signing
step, and tag the release after the release branch is green. The release workflow requires
`docs/releases/v<version>.md`, so the notes are always reviewable before tagging.

## Scheduled reminders

- **2026-11-21** — quick wins (reminder sent): A1 (social preview), start A2/A3
  (Search Console/Bing), decide A5 (signing route).
- **2026-12-19** — measurement baseline: A12 (Search Console/Bing/GitHub numbers), check whether
  A5/A6 unblocked Winget, whether A10 outreach got any answer, then act on the Step Zero verdicts
  (delivered 2026-11-21: A FAIL, B PASS; FC-2/FC-3 closed) and decide whether to schedule the
  non-Python runtime re-check or the five-user gate.

The agent can also do on request: draft the launch posts (A4), prepare the Winget manifests (A6),
triage the Dependabot PRs (A9), write the corpus outreach email (A10), run the clean-machine
acceptance script (A8) on any machine you connect, and re-check all repository facts before a
release.
