# Human in the Loop pipeline log

## 2026-08-26 audit

- Incoming collection `Y6F6S4IY` resolved live; 88 records returned, including 44 top-level records and child attachments.
- Podcasted collection `6K25XW39` contains the five pilot sources only; they are not selected again.
- Existing live feed has one item, episode 001, currently 04:27. Existing pilot assets are preserved.
- Remaining source planning is limited to PDF-bearing research with a substantive games/game-based-learning context, plus directly relevant EDM/learning-analytics methods used to study educational game systems. Unrelated Incoming PDFs are retained in Incoming and not forced into episodes.
- Planned packages: episode 002 (analytics and inference), episode 003 (scaffolding and design), episode 004 (affect and assessment).

## 2026-08-26 production checkpoint

- Episode 002 rendered at 12:33, episode 003 at 12:20, and episode 004 at 12:48. Each uses distinct host/correspondent neural voices, has spoken synthetic/dramatized disclosure, and has no spoken role labels.
- GitHub Pages commit `0ac0e30` published episodes 002–004, notes, and the noindex queue UI. Pages build commit `e565279` adds the queue report.
- Live RSS verification passed after Pages build: 4 XML items parse; all four enclosures return HTTP 206 for `Range: bytes=0-1023`; all new MP3s and notes returned HTTP 200; enclosure lengths match local files.
- Three lawful OA PDFs were imported into Incoming with metadata, child attachments, and provenance/access notes: `EVXUJ7VA`/`KECJPWBF` (10.18608/jla.2023.7681), `E4V92SVH`/`NGACMWJ3` (10.1007/s10639-022-11087-4), and `3T6P8QGD`/`RBH77UHV` (10.1007/s11423-010-9183-0).
- One promising subscription-preview match was queued without downloading: `I6KXM39M`, DOI 10.1007/s11528-025-01142-5. Collection `4WAAFA26` is `Needs Full Text`; queue report is exposed at `needs-full-text.html`/`.json` with noindex.
- After live verification, 14 unique episode source parents were moved from Incoming to Podcasted using version-guarded updates. The parent `CWE62TKC` retained its other collection `KZBPJKLB`; no item was deleted.
- Final live check after notes update: RSS parsed with 4 items; all 4 audio enclosures returned HTTP 206 for byte range `0-1023`; each episode notes page returned HTTP 200 and contained its direct Zotero links plus DOI/publisher links; the live queue JSON contains the queued DOI and Zotero link.

## 2026-08-26 incremental correction checkpoint

- Episode 002 was rechecked after rendering: local MP3 is byte-identical to the live enclosure (`12:33`, 12,048,812 bytes), RSS episode 2 is present with its stable GUID, and its live audio returned HTTP 206 for `Range: bytes=0-1023`.
- Removed the accidental source overlap for `XDYFELXE`: it remains assigned only to episode 002; episode 003 now has four sources, its notes contain no `XDYFELXE`, and its audio was re-rendered without the duplicated source discussion (`11:20`, 10,881,068 bytes).
- Pages commit `d0253ad3e48a28484689c0e9194cae4c9e63fb9a` published the corrected episode 003 audio/notes and regenerated RSS. Live feed returned HTTP 200, parsed 4 items, episode 003 reported `00:11:20`, all episode notes returned HTTP 200, and all three new episode enclosures returned HTTP 206 for `Range: bytes=0-1023`.
- The unique move list remains 14 parents; no Zotero move was repeated and no item was deleted.

## 2026-08-26 source-uniqueness correction

- A full manifest audit found two additional accidental overlaps: `PMHSYCZM` and `ME88PUW3` had been listed in both episodes 003 and 004. Ownership is now unique: episode 003 uses `67TNQNST`, `V52FZLXT`, and `97KF32WL`; episode 004 uses `6SLNA7ZV`, `25FRUUXF`, `PMHSYCZM`, `ME88PUW3`, and `CWE62TKC`.
- Episode 003 was re-rendered without the duplicate AR-feedback/formative-assessment material (`10:03`); episode 004 was re-rendered without the duplicate Learning, Education, and Games material (`11:56`). Every source parent remains in the move list exactly once.
- Pages commit `555947c18d27abcc47d0befa595fee0047eb95f0` published both corrected audio files, notes, and RSS. Live RSS returned HTTP 200 and parsed 4 items with durations 12:33, 10:03, and 11:56 for episodes 002–004; all three enclosures returned HTTP 206 for `Range: bytes=0-1023`; all notes and the full-text queue returned HTTP 200.

## Safety rule

No source is moved from Incoming until its episode audio, notes, RSS entry, and live HTTP/RSS/range checks all pass. Moves must preserve all other collection memberships and use a fresh item version when updating.

## 2026-08-26 publication repair

- Reconciled the live Pages deployment: the active repository is
  `mrdavidgagnon/human-in-the-loop-AI-podcast`; the retired
  `mrdavidgagnon/human-in-the-loop-feed` URL returned 404.
- Regenerated the local feed with the current rendered assets, complete source
  metadata in episode notes, explicit fictional-correspondent and AI-summary
  disclosures in RSS extended content, and corrected enclosure URLs.
- Published feed commit `6d1b754`. Live RSS now has four items; episode 002,
  003, and 004 report 14:48, 14:50, and 14:51, respectively. Their enclosures
  return HTTP 206 for `Range: bytes=0-1023`, with lengths matching the feed.
- Live episode notes return HTTP 200 and contain complete citations, direct
  Zotero links, evidence boundaries, and the required citations sentence. The
  full-text queue remains open for `I6KXM39M`; no source was moved by this
  repair.

## 2026-08-26 book-only correction

- Corrected the earlier grouping error: `97KF32WL` (*Learning, Education, and
  Games, Volume 3*) and `ME88PUW3` (*Playful Testing*) are books and now each
  has its own single-source episode, 005 and 006. They are no longer discussed
  in episodes 003 or 004.
- Episode 003 now contains only `67TNQNST` and `V52FZLXT`; episode 004 contains
  only `6SLNA7ZV`, `25FRUUXF`, `PMHSYCZM`, and `CWE62TKC`. Source ownership is
  unique across all six episodes.
- Episodes 005 and 006 were scripted, rendered, noted, and added to RSS. The
  current durations are computed from the rendered MP3s by the publisher.

## 2026-08-26 episode 007 panel review and production

- Remaining eligible Incoming items were the three lawful, substantive PDFs imported during this run: `EVXUJ7VA` (Lu et al., 2023), `E4V92SVH` (Daoudi, 2022), and `3T6P8QGD` (Wouters et al., 2011). They form one coherent episode on designing and interpreting evidence from serious-game traces; no source overlaps the six published episodes.
- A three-reviewer panel convened before audio rendering: Mara Chen (EDM/validity), Nia Okafor (learning sciences/complexity), and Theo Alvarez (OpenGameData). All three issued **revise, then pass** judgments. The full judgments, suggested reading, and revision record are in `episodes/007/review-panel.md`.
- Panel-required revisions were made before rendering: the script now identifies Lu et al.’s study-specific 24-student expert proxy and Wouters et al.’s 19 participants plus three-expert referent. The draft already retained the key limitations: Lu et al.’s missing external pre/post assessment, Daoudi’s 80-paper non-pooled review corpus, and Wouters et al.’s low-n case and absent predictive-validity comparison.
- Episode 007 script includes a complete title/author block at the top; complete spoken citations; one short direct quote per source with page number and source boundary; continuity links to Episodes 002–006; and a practical OpenGameData provenance/contestability theme. No audio was rendered before panel authorization.
- Local post-render validation passed: all 43 dialogue parts are non-empty; final MP3 decodes cleanly; duration is 12:58 and size is 12,453,164 bytes; RSS parses 7 items with episode 007 enclosure length matching; direct DOI/PMC source checks returned HTTP 200; all 17 source keys across episodes are unique; required disclosures, show-notes sentence, title/author block, and direct Zotero links are present. The rendered correspondent uses `en-GB-SoniaNeural` (female British voice).
- Publication handoff is blocked at the external-write step: the configured GitHub credential returned HTTP 401 and the canonical repository push was rejected. The canonical clone contains the complete package in commit `e5b05b300db52ca781a80c869b5a2526ffbfca85`, one commit ahead of `origin/main`. The live Pages feed therefore remains unchanged until a valid GitHub credential is supplied.
- Zotero move handoff is also pending: Zotero Desktop/local API was unavailable (`127.0.0.1:23119` connection refused) and no valid remote Zotero API key was configured. Per the safety rule, `EVXUJ7VA`, `E4V92SVH`, and `3T6P8QGD` were not moved or deleted; they remain in Incoming pending a fresh post-publication collection update.
