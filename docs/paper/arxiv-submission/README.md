# arXiv submission bundle — GroundClock

Flat bundle (files at root) ready to upload to arXiv.

## Contents
- `groundclock-paper.tex` — main source (article class).
- `groundclock.bib` — bibliography.

## Build locally
```bash
pdflatex groundclock-paper
bibtex groundclock-paper
pdflatex groundclock-paper
pdflatex groundclock-paper
```

## Submit
1. Rebuild the tarball: `python ../../../scripts/build_arxiv.py` (or see the repo's arxiv-bundle skill).
2. Upload `arxiv-submission.tar.gz` to https://arxiv.org/submit (category: cs.CL).
3. Paste the Title / Abstract / Comments from the repo's paper-polish output. Use `--` not em-dashes
   and straight quotes in the arXiv abstract field.

No figures in v0, so total size is well under the 50 MB limit.
