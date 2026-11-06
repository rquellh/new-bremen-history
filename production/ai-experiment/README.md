# AI painting experiment (not in use)

Notes and prompts from an experiment painting the chapters with a local image
model (Z-Image Turbo via mflux), kept in case we return to it. The model and
mflux were removed from this machine on 2026-11-05.

Its Python scripts (`paint.py`, which read `prompts.toml`, and
`tint_references.py`) were removed on 2026-11-06, when the project's tools
moved to TypeScript. They're in git history: `git show
b5b8eb8:production/ai-experiment/paint.py`.

We stopped because the model invented historical details (vehicles, buildings,
hills) even when guided by real photos. The site uses real photographs with a
non-AI ink treatment instead (`scripts/ink.ts`).

Lessons, if this is picked up again:
- The model ignores negative prompts; never name what you don't want.
- Anything in the shared style text appears in every scene.
- Black-and-white references pull the palette gray; tint them first.
