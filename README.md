# New Bremen History

The history of New Bremen, Ohio, told as a scrolling story in real photographs. Served at
https://www.ryanquellhorst.com/new-bremen-history/ from the `main` branch.

It's a static site: plain HTML, CSS and JavaScript, with no build step and no
dependencies beyond Google Fonts.

## How it works

- Each chapter in `index.html` is a `<section class="chapter">` holding its
  photo, its text, and settings in `data-` attributes (documented at the top
  of `assets/js/main.js`).
- With JavaScript, the photos are drawn on one fixed canvas
  (`assets/js/stage.js`), each laid whole on the page beside its text. Scrolling
  moves a slow camera over it, then the next one bleeds in like ink on wet paper.
- Without JavaScript, or with reduced motion, it reads as a plain illustrated
  article (reduced motion keeps the stage but swaps the ink and camera moves
  for simple cross-fades).

## Run it locally

```sh
python3 -m http.server 8000
# open http://localhost:8000/
```

## Images

Every image is a real photograph from the New Bremen Historic Association's
galleries, shown whole with its date and credit. `scripts/build_photos.py`
renders them in ink tones with ordinary image filters (`scripts/ink_photo.py`);
nothing is generated or invented. Captions that were written on a photo are
removed; real signs in the scene stay.

```sh
uv venv .venv && uv pip install --python .venv/bin/python opencv-python-headless numpy pillow
.venv/bin/python scripts/build_photos.py          # all chapters
.venv/bin/python scripts/build_photos.py 03-canal # one chapter
```

Each chapter's photo, source URL, caption and any cleanup areas are in
`production/photos.toml`. Originals are downloaded to `production/references/`,
which is git-ignored: the photos are the association's, and the site must not
be published until they give permission.

## Production notes

- [storyboard.md](production/storyboard.md): the chapters and layout rules.
- [sources.md](production/sources.md): every fact in the text and where it came
  from, plus what was left out and why.
- [ai-experiment/](production/ai-experiment/): an abandoned attempt at AI
  paintings, and why it was dropped.

## Credits

History from the [New Bremen Historic Association](https://newbremenhistory.org/en/),
including its excerpts from the 1933 *New Bremen Centennial* book by
C. A. Schrage and W. W. Grothaus. A personal project by Ryan Quellhorst; not
affiliated with the association.
