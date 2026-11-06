# AI painting experiment (not in use)

Scripts from an experiment painting the chapters with a local image model
(Z-Image Turbo via mflux), kept in case we return to it. The model and mflux
were removed from this machine on 2026-11-05, so these don't run as-is.

We stopped because the model invented historical details (vehicles, buildings,
hills) even when guided by real photos. The site uses real photographs with a
non-AI ink treatment instead (`scripts/ink_photo.py`).

Lessons, if this is picked up again:
- The model ignores negative prompts; never name what you don't want.
- Anything in the shared style text appears in every scene.
- Black-and-white references pull the palette gray; tint them first.
