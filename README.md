# New Bremen History

The history of New Bremen, Ohio, told as a scrolling ink-wash painting. Served at
https://www.ryanquellhorst.com/new-bremen-history/ from the `main` branch.

It's a static site: plain HTML, CSS and JavaScript, with no build step and no
dependencies beyond Google Fonts.

## How it works

- Each chapter in `index.html` is a `<section class="chapter">` holding its
  painting, its text, and settings in `data-` attributes (documented at the top
  of `assets/js/main.js`).
- With JavaScript, the paintings are drawn on one fixed canvas
  (`assets/js/stage.js`). Scrolling moves a slow camera across each painting,
  then the next one bleeds in like ink on wet paper. A chapter can also have a
  video clip that scroll scrubs, with its still painting as the fallback.
- Without JavaScript, or with reduced motion, it reads as a plain illustrated
  article (reduced motion keeps the stage but swaps the ink and camera moves
  for simple cross-fades).

## Run it locally

```sh
python3 -m http.server 8000
# open http://localhost:8000/
```

## Production

Planning lives in `production/`:

- [storyboard.md](production/storyboard.md): the ten chapters, layout rules,
  and the approval gates.
- [sources.md](production/sources.md): every fact in the copy and where it came
  from, plus what was left out and why.
- [image-prompts.md](production/image-prompts.md): draft prompts for the
  paintings and the two video moments.

The paintings are placeholders for now (`assets/art/placeholder/`, made by
`scripts/make_placeholders.py`).

### Adding a painting

1. Save the approved master (16:9, at least 2560 x 1440) to
   `production/masters/`, for example `03-canal.png`. Masters are git-ignored.
2. Run `python3 scripts/process_art.py production/masters/03-canal.png` (needs
   `cwebp`). It writes 2560 and 1440 wide WebPs to `assets/art/`.
3. Point the chapter's image at them; the script prints the markup to use.
4. Update the image's `alt` text and, if the composition changed, the
   chapter's `data-focus` and `data-bleed`.

### Adding a video moment

1. Generate the clip from the chapter's approved still as its first frame.
2. Run `python3 scripts/normalize_clip.py generated.mp4 assets/video/03-canal.mp4`
   (needs `ffmpeg`).
3. Add `data-video="assets/video/03-canal.mp4" data-zoom="1 1"` to the chapter.

## Credits

History from the [New Bremen Historic Association](https://newbremenhistory.org/en/),
including its excerpts from the 1933 *New Bremen Centennial* book by
C. A. Schrage and W. W. Grothaus. A personal project by Ryan Quellhorst; not
affiliated with the association.
