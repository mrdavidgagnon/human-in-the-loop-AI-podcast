# Google Scholar monitoring protocol

- Status: working protocol for *Human in the Loop* research discovery
- Owner: podcast research workflow
- Review cadence: quarterly, or sooner when an episode review exposes a gap

This protocol finds scholarly work that can support future episodes. Google
Scholar is a discovery index, not an evidence-quality filter. A result is a
lead until its metadata, access, methods, and claim boundaries have been
checked. The podcast's README and style guide remain the authority for source
verification, complete spoken citations, evidence notes, and disclosures.

## Initial monitoring scope

Run both search tracks on every monitoring cycle. A paper may belong to both
tracks, but the record should say which question it serves.

### 1. Educational data mining or learning analytics involving games

Include work where a game, game-based learning environment, simulation, or
playful interaction is the setting, data source, intervention, or assessment
context, and educational data mining, learning analytics, educational data,
telemetry, or related inference is a substantive part of the work. Relevant
questions include how learning is measured or inferred, what interaction data
can and cannot support, dashboards and feedback, assessment, equity, validity,
and teacher or learner decision-making.

Do not require the authors to use the exact labels “educational data mining” or
“learning analytics.” Screen for the underlying activity and method as well as
the terminology.

### 2. Trends in public media or educational media that utilize games

Include research or authoritative sector analysis about public media, public
service media, educational media, informal learning media, children’s media,
edutainment, museums, broadcasting, video, or audio that uses games, gaming,
play, interactive stories, game-based formats, or gamification. A useful result
should address a trend, design pattern, audience/learning context, production
practice, distribution model, or public-value question—not merely mention a
game in passing.

## Semantic synonym clusters

Use these as interchangeable concept clusters when making or adapting queries.
Keep the cluster names in the search log so a later reviewer can reproduce the
search.

| Cluster | Terms and phrases |
| --- | --- |
| Analytics and EDM | `"educational data mining"`, `EDM`, `"learning analytics"`, `"educational analytics"`, `"academic analytics"`, `"learner analytics"`, `telemetry`, `"process data"`, `"interaction logs"`, `trace data`, `dashboard`, `assessment analytics` |
| Learning and education | `learning`, `learner*`, `student*`, `education*`, `school*`, `classroom*`, `teaching`, `instruction`, `assessment`, `curriculum`, `literacy`, `informal learning` |
| Games and play | `game`, `games`, `gaming`, `gameplay`, `videogame*`, `"video game*"`, `"digital game*"`, `"serious game*"`, `"educational game*"`, `"game-based learning"`, `"game based learning"`, `simulation`, `playful`, `gamification`, `"stealth assessment"` |
| Media and public context | `"public media"`, `"public service media"`, `broadcast*`, `PBS`, `television`, `radio`, `podcast*`, `video`, `museum*`, `"educational media"`, `"learning media"`, `edutainment`, `children*`, `youth`, `informal`, `civic`, `public value` |
| Trend and practice | `trend*`, `landscape`, `ecosystem`, `adoption`, `innovation`, `production`, `distribution`, `participation`, `audience`, `engagement`, `design`, `implementation`, `policy`, `future`, `emerging` |

The asterisk is a useful Scholar wildcard in some contexts but is not relied
on for recall. Repeat important searches with singular/plural or alternate
spellings when the result set looks unexpectedly small. Google Scholar's
Boolean behavior is limited: use uppercase `OR`, quotation marks for phrases,
and separate focused queries instead of one enormous expression.

## Query set

These are the starting queries. Record the exact string used, the date, and
the result cutoff. Run the broad queries first, then the narrower method or
context queries. In Scholar, use the custom date range only as a supplement to
the all-years baseline; “Since last cycle” can miss older papers newly indexed
or newly relevant through citation chaining.

### Track A: EDM and learning analytics in games

```text
"educational data mining" (game OR games OR "game-based learning" OR "serious games")
"learning analytics" ("game-based learning" OR "serious games" OR gameplay)
("educational analytics" OR "learner analytics") (game OR games OR simulation) education
(telemetry OR "interaction logs" OR "process data" OR "trace data") ("educational game" OR "serious game")
("game analytics" OR "game learning analytics") (student OR learner OR education)
("stealth assessment" OR "game-based assessment") learning
(dashboard OR feedback OR prediction OR classification) (gameplay OR "educational game") learning
("digital games" OR videogames OR "serious games") ("learning outcomes" OR assessment) (analytics OR data)
```

Useful targeted variants:

```text
intitle:"learning analytics" game education
intitle:"educational data mining" game
"game-based learning" (validity OR inference OR measurement) data
"educational game" (fairness OR equity OR bias OR privacy) analytics
```

### Track B: public or educational media using games

```text
("public media" OR "public service media" OR broadcasting OR PBS) (game OR games OR gaming OR playful) (education OR learning OR literacy)
("educational media" OR "learning media" OR edutainment OR "informal learning") (game OR games OR "game-based")
(television OR radio OR podcast OR video OR museum) ("educational game" OR "serious game" OR gamification) audience
(children OR youth OR family) ("public media" OR "educational media") (games OR gaming OR play)
("public value" OR participation OR engagement OR adoption) ("game-based" OR gamification) media
(trend OR landscape OR ecosystem OR future) ("educational games" OR "serious games") media
```

Useful targeted variants:

```text
intitle:"public media" game education
intitle:"public service media" game education
"public broadcasting" (games OR gaming) learning
"educational television" (game OR games OR interactive) literacy
"children's media" (game OR games OR play) learning
```

Scholar may not parse every parenthesized expression consistently. If a query
returns no results, split it into two or three quoted-phrase searches and log
the split. Do not silently broaden a failed query without recording the change.

## Inclusion and exclusion rules

Screen title and abstract first, then the full text when available. Apply the
rules below to each version cluster, not to every duplicate record.

### Include

- The work has a clear connection to Track A or Track B, with a game/play
  element and the relevant educational, analytic, media, or public context.
- The result contributes evidence, a systematic or scoping review, a clearly
  identified conceptual/design framework, or an authoritative trend analysis.
- The method and setting are sufficiently described to write a claim together
  with its boundary (for example, sample, platform, age group, intervention,
  or media system).
- Bibliographic metadata can be verified against Zotero and, when available,
  the DOI, publisher, or proceedings record.
- For a focal episode source, a lawful full text or adequate source record is
  available for checking. A promising citation without full text may remain a
  lead in the `Needs Full Text` queue, but is not episode-ready.
- A result can add a distinct contribution to a proposed episode rather than
  duplicating a source already assigned in the current production run.

### Exclude or retain only as a lead

- Game design or entertainment research with no meaningful learning,
  educational, media, or public-value connection.
- Generic gamification papers where games are only a metaphor or a reward
  mechanic and the work does not illuminate the initial scope.
- Analytics papers about commercial games that do not study learning,
  education, or a relevant public/educational media context.
- Marketing copy, vendor claims, unsourced web pages, slide decks, or search
  snippets used as if they were scholarly evidence. They may point to a source,
  but do not count as the source.
- Results whose only connection is a passing keyword mention.
- Retracted, superseded, or methodologically opaque work, unless it is retained
  explicitly as a historical or cautionary background lead.
- A duplicate or alternate version after it has been linked to the canonical
  record. Do not delete it; mark the relationship.

When relevance is uncertain, use `lead—review` rather than forcing an include
or exclude decision. Record the specific uncertainty and resolve it at the
next screening pass.

## Capture, deduplication, and screening

### Search run

For each query, capture the first 50 results by relevance and any newer results
since the previous run that fall within the scope. For a particularly useful
paper, inspect `Cited by`, `Related articles`, and the paper's reference list;
label those as citation-chaining discoveries rather than pretending they came
from the original query. Stop chasing a branch after 20 new candidates or when
three consecutive pages produce no plausible result.

Save the exact query and date in a run log. A minimal run identifier is
`GS-YYYY-MM-DD-A01` or `GS-YYYY-MM-DD-B01`, where A/B identifies the track and
the final number distinguishes query variants.

### Deduplication order

1. Normalize DOI to lowercase, remove `https://doi.org/`, URL parameters, and
   trailing punctuation, then match on DOI where present.
2. Match normalized title (Unicode-normalized, case-folded, punctuation and
   repeated whitespace removed) plus first author and year.
3. Cluster conference paper, repository manuscript, preprint, journal article,
   and Google Scholar “versions” when they represent the same work. Prefer the
   version with the most complete metadata and the lawful full text, while
   retaining links and version notes.
4. Check Zotero for an existing item and for current episode ownership before
   importing. Link `duplicate_of` or `version_of`; never create a second
   episode assignment for a duplicate.

Do not treat title similarity alone as proof of duplication: a conference
paper and a substantially expanded journal article may both be useful, but the
relationship and distinct contribution must be recorded.

### Screening record

Use one row or note per canonical work with these fields:

```text
run_id; found_on; query_or_chain; scholar_rank; title; authors; year; venue;
doi_or_url; scholar_cited_by; zotero_key; item_type; full_text_status;
scope (A/B/both); game_role; media_role; population_and_setting; study_design;
data_or_evidence; outcome_or_claim; evidence_boundary; relevance (include /
lead—review / exclude); evidence_tier (focal / background / lead);
exclusion_reason; duplicate_of_or_version_of; episode_candidate; reviewer;
screened_on; notes
```

At minimum, `game_role`, `population_and_setting`, `study_design`,
`data_or_evidence`, and `evidence_boundary` must be filled before a candidate
can become a focal episode source. The `evidence_boundary` should answer what
the work supports and what it does not establish, in the same claim-plus-
boundary style used by the show.

## Cadence and maintenance

- **Weekly, 20–30 minutes:** run the core queries in both tracks; capture new
  candidates, citation-chain leads, and obvious duplicates. Use the date filter
  for triage, but retain a small all-years check.
- **Monthly, 45–60 minutes:** deduplicate, complete title/abstract screening,
  check Zotero and current episode ownership, and promote only the strongest
  candidates to full-text review or an episode theme.
- **Before each episode plan:** rerun the relevant narrow queries, inspect
  citation chains for the central papers, and check that no selected source is
  already assigned to another episode in that production run.
- **Quarterly:** review recall and precision by query family, add missing
  terminology discovered in screening, retire noisy queries, and record the
  change here. Do not rewrite the historical run log.

## Feeding the podcast workflow

1. Add a promising result to Zotero's `Incoming` workflow with the monitoring
   run ID, scope tag, and screening status. Import lawful open-access files
   only; if the record is promising but inaccessible, add its metadata and put
   it in `Needs Full Text` rather than bypassing access controls.
2. Verify metadata against Zotero and, where available, the DOI or publisher
   record. Read enough of the source to identify the research question,
   setting, method, key finding, and boundary. A Scholar title, abstract, or
   citation count is never sufficient for scripting.
3. Group included works around one coherent human-scale question. Favor a
   small set of complementary sources; do not add a weakly related paper to
   reach a target count. Assign each focal source to only one episode in a
   production run.
4. In the script and notes, give every included article its complete citation
   (all authors, full title, venue, and year), direct Zotero link when access
   has been granted, and an evidence note. Apply the fictional-correspondent
   and AI-summary disclosures required by the style guide.
5. Before any collection move, run the existing production checks: rendered
   audio, notes, RSS entry, live HTTP/RSS/range checks, and source-ownership
   audit must pass. Move only the verified source parent, preserving other
   collection memberships. Leave unresolved leads and inaccessible papers in
   Incoming or `Needs Full Text` with their screening record.

The output of a monitoring cycle is therefore a reproducible candidate set,
not an automatic episode. Human editorial judgment remains responsible for
selection, interpretation, claim boundaries, and final publication checks.
