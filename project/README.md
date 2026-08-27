# Human in the Loop AI Podcast

Repository name: `human-in-the-loop-ai-podcast`

This project turns research in David Gagnon's Zotero library into a private,
playful audio review. It exists so David can stay caught up on that library
while walking his cockapoo or biking to work.

The current working directory is still named `zotero-podcast`. Rename the
repository and its checkout separately when the hosting repository is renamed;
published feed URLs are deliberately not changed by this internal preparation.

## Episode production contract

These requirements apply to every article included in an episode, without
exception:

1. Verify the bibliographic metadata against Zotero and, when available, the
   publisher or DOI record before scripting.
2. Cite the article in the spoken episode with every author name, the complete
   article title, the journal or other publication venue, and the publication
   year. Do not shorten an author list to "et al." in this citation.
3. Give the same complete citation in the show notes. Each show-notes entry must
   include a direct link to the Zotero item when the listener has been granted
   access. A DOI or publisher link may be included as an additional public link,
   but it does not replace the Zotero link.
4. Tell listeners in every episode: "The complete citations are in the show
   notes, with links to the Zotero files when you have been granted access."
5. Before rendering or publishing, check the script and notes article by
   article. An episode is not ready if a source is merely named, if any author
   is omitted, or if the title, venue, year, or access-appropriate Zotero link
   is missing.

The spoken citation can appear when an article is introduced or in a dedicated
source segment. Clarity matters more than citation-style punctuation; all five
bibliographic elements must be audible.

## Robust production tooling

Use [pipeline/ROBUST_PIPELINE.md](pipeline/ROBUST_PIPELINE.md) and
`pipeline/robust_pipeline.py` for new production work. The wrapper keeps a
durable ledger and inventory, serializes mutating operations with a lock,
requires the three-reviewer gate, performs deterministic preflight checks,
resumes rendering from valid parts with atomic outputs, and verifies local or
explicitly requested remote feed/audio/notes checks. `publish` is local-only:
it never commits, pushes, or uploads. Start a ledger with:

```sh
python3 pipeline/robust_pipeline.py reconcile --write
python3 pipeline/robust_pipeline.py status
```

## Repository and feed names

`human-in-the-loop-ai-podcast` is the project/repository name. The podcast title
remains *Human in the Loop*. The separately hosted feed currently uses
`mrdavidgagnon/human-in-the-loop-AI-podcast`; its public base URL is
`https://mrdavidgagnon.github.io/human-in-the-loop-AI-podcast/`.
