---
name: local-history-site
description: Plan, research and build a scroll-driven story website about local history (a hometown, neighborhood, school, church, farm, company or any historical subject), told in chapters with real archival photographs, sourced facts and the archive's permission, and published as a static site, for example on GitHub Pages with a custom domain. Use this whenever someone wants to make a town history website, a digital exhibit for a historical society, an anniversary or centennial site, a "story of our town" page, or a scrolling story with old photos, even if they don't say "scroll" or "skill". Also use it for any single part of such a project, such as finding an archive, choosing photos, fact-checking the text, treating old photos without AI, asking an archive for permission, or putting the site online.
---

# Local history site

Help someone tell the history of a place (or a school, church, company or family) as a
scrolling story. It runs to about a dozen chapters, each a moment in time with:

- one real archival image;
- a few sentences of sourced text;
- a credit line.

The finished site is static (HTML, CSS and a little JavaScript), so it's cheap to host and
easy to keep. A worked example is New Bremen, Ohio:
https://newbremen.ryanquellhorst.com/, with source at
https://github.com/rquellh/new-bremen-history. Its `production/sources.md` and
`production/storyboard.md` show the fact ledger and chapter table described below. Read
its code for ideas if useful, but write the new site's code fresh, fitted to its own
story.

## What makes these sites work

These principles come from building the example. Each has a reason; keep the reason in
mind when a situation doesn't fit the rule exactly.

1. **Real images, shown honestly.** The point of a history site is that this is what the
   place really looked like.
   - In the example project, an AI image model was tried first, guided by real photos. It
     still invented cars, grandstands, buildings, hills and reeds, and readers have no
     way to tell. It quietly rewrites history. So use archival images only.
   - Change only how they're rendered, with ordinary deterministic filters: contrast,
     tone, color, grain and edges.
   - Show each one whole, with its real date and source.
   - Label drawings, maps and postcards as what they are.
   - Removing writing someone added to a print, such as a handwritten caption, is fine.
     Real signs in the scene stay.
   - Don't use AI generation, AI upscaling, colorizing, "restoration", or video made from
     stills unless the person explicitly asks for it. Even then, label it on the page.
2. **Every fact has a source.** Local history repeats its own errors, sources often
   disagree on dates, and the readers include people who know the town well. Keep a
   ledger (`sources.md`) that ties each fact in the text to where it came from.
3. **Permission before publishing.** Archives and historical societies hold the scans and
   often the rights. Asking first is courteous and builds goodwill. It often turns up
   better scans and a fact-checker too. Once something is public it can be copied and
   cached, so ask before it goes live, not after.
4. **Voice is a feature.** Readers enjoy a warm narrator with opinions. When fixing
   wording, fix the specific awkward or inaccurate phrases and keep the personality.
   Rewriting everything flat is a common over-correction that people then ask you to
   undo.
5. **It reads everywhere.** Phones are where most people will open a link to their
   hometown's history. The site should also work with reduced motion and without
   JavaScript; it falls back to an illustrated article.

## Working with the person

Many people doing this are historians, genealogists or volunteers, not developers. Use
plain language, explain any technical step you ask them to do, and give exact clicks for
settings pages.

**Ask these early, once:**
- The subject and its boundaries: years, place.
- The audience and the tone: celebratory, or warts-and-all. Which hard parts of the
  history belong in it?
- How many chapters. Ten to fifteen is a good range: long enough for a story, short
  enough to finish.
- Whether they have a contact at a local archive or historical society.
- Where it will live, and whether they own a domain.
- What language they want any tooling in, if they care. Switching later means rewriting
  it.

**Stop at checkpoints.** Show your work and get a yes before moving on. Each stage builds
on the last, and a wrong chapter list or photo pick is cheap to fix early and expensive
later:
1. scope;
2. chapter outline;
3. image picks;
4. text draft;
5. the built site, on a phone and on a desktop;
6. permission email, then publishing.

**Before installing anything, say what, roughly how big, and where.** Keep installs inside
the project folder (`node_modules`, a virtual environment) and say how to remove them.
People sometimes do personal projects on a work computer.

## The phases

### 1. Scope
Agree on the subject, years, tone, chapter count and audience. Write them at the top of
`production/storyboard.md`.

### 2. Find the archive and the sources
Find where the photos live and which written histories to trust. Start a `sources.md`
ledger right away, before writing any text. Read `references/sources-and-rights.md`. It
covers:
- where to look for photos and facts;
- how to search a big captioned gallery;
- the ledger's format;
- how to handle sources that disagree;
- the basics of copyright and public domain.

### 3. Outline the chapters
Draft a table: number, era label, title, the one or two facts the chapter turns on, and
candidate images. A typical arc runs:
- the land before the town;
- founding;
- growth;
- turning points (transport, industry, disasters);
- institutions and people;
- preservation;
- today.

Chapters should be moments, not encyclopedia sections: "The canal comes through, 1845",
not "Transportation".

### 4. Pick the images
One per chapter. Prefer images that show the exact thing a sentence describes, and people
or activity over empty buildings. Read `references/images.md`, which covers choosing
images, the per-chapter image config, and checking that an image is what its caption
says.

### 5. Write the text
Read `references/writing.md` for:
- chapter length and structure;
- voice;
- the accuracy pass;
- credits and alt text;
- how to edit without flattening the voice.

### 6. Treat the images
Build each image with a script, so it's reproducible:

1. download the original into a git-ignored folder;
2. optionally remove added writing;
3. apply the filters;
4. export WebP at two widths;
5. write the image path, alt text and credit into the page from one config file, so they
   never drift apart.

Read the treatment section of `references/images.md`.

### 7. Build the site
Read `references/site.md` for:
- the page structure;
- the scroll-driven stage (or a simpler sticky alternative);
- the phone and desktop layout rules that were learned the hard way;
- accessibility and performance.

### 8. Test
Use a headless browser. Visit every chapter at desktop, phone and short-phone sizes, and
check:
- the right text shows;
- the navigation marks it;
- nothing overlaps;
- there are no console errors.

Test again after any text edit: longer text is the usual cause of the photo covering the
words. `references/site.md` has a checklist.

### 9. Permission and publishing
Read `references/publishing.md`. It has:
- a permission email template;
- how to keep things private until permission comes;
- GitHub Pages setup;
- custom domain DNS (including a common path-vs-subdomain trap);
- domain verification and HTTPS.

## Suggested project layout

```
index.html               the whole story; readable without JavaScript
assets/css/  assets/js/  assets/art/   (treated images only)
production/
  storyboard.md          scope, chapter table, layout notes
  sources.md             every fact and where it came from
  photos.toml            per-chapter image config (or .json)
  references/            downloaded originals, git-ignored
scripts/                 build-photos, serve, test
README.md                what it is, how to run it, credits
```

## Pitfalls seen before

- **Sweeping edits flatten the voice.** When asked to fix odd wording, change only the
  phrases that are odd and list what changed.
- **Counts and summary claims drift.** "Every photograph on this page" breaks once one
  image is a drawing, and "thirteen photos" breaks once one is swapped. Recheck the
  colophon whenever an image changes.
- **An image's date doesn't match its chapter.** That's fine, as long as the credit gives
  the image's real date. A 1962 photo of the depot can illustrate the 1871 railroad.
- **Dull picks.** A building shot when a photo of people at work exists. When the person
  says a picture is boring, look for one that shows the specific thing the text
  describes.
- **Guessed archive URLs.** Copy exact filenames from the gallery's HTML; guessed names
  are often slightly wrong.
- **Publishing before permission,** for example by pushing images to a public repo.
- **The custom domain path trap.** `example.com/town-history/` only works when the domain
  belongs to the account's `<user>.github.io` site. A subdomain is simpler. See
  `references/publishing.md`.
