# Building the site

## Structure: an article first

Write `index.html` so it's a complete illustrated article on its own. Each chapter is a
`<section>` holding:
- a `<figure>` with the `<img>` (with `srcset`) and a `<figcaption>`;
- a text panel with the era label, an `<h2>`, the paragraphs and the credit line.

Put per-chapter settings in `data-` attributes, so the script stays generic and the
chapters stay data:
- scroll length in screen heights;
- camera zoom from/to and drift;
- the point the transition spreads from;
- which side the text sits on.

Without JavaScript, this is the whole site. It should read well that way.

## The enhancement: a scroll-driven stage

There are two good options. Ask which the person wants.

**Simple:** a sticky figure per chapter, with a cross-fade driven by
`IntersectionObserver`. It has few moving parts and is robust. It's the right choice for
most people.

**Ink stage** (the example site's approach):
- **The stage.** One fixed full-screen `<canvas>` draws the current chapter's image. The
  scroll position maps to "chapter index + progress (0–1)".
- **The camera.** Within a chapter it drifts and zooms slightly, for example from 1.00 to
  1.06.
- **The transition.** The next image arrives through a mask that spreads from a point,
  like ink soaking into wet paper. Build the mask from a noise field and threshold it
  over time.
- **The text.** It fades out before the transition and back in after it.
- **Reduced motion.** With `prefers-reduced-motion`, swap the bleed and camera for plain
  cross-fades.
- **Memory.** Load images one chapter ahead and release far-away ones.

## Layout rules, learned the hard way

- **Desktop.** Draw the image whole ("contain"), like a print laid on paper, on the side
  opposite the text. Very wide images can sit above the text instead.
  - Measure the text panel's actual box, and fit the image in the space that's left.
  - The text must never cover the image.
- **Phones in portrait.** Image full width at the top, just below the chapter navigation,
  with the text directly under it.
  - Leave the spare room at the bottom of the screen. A gap above the photo looks like a
    bug; one below the text doesn't.
  - If the image and text don't both fit, shrink the image. Never overlap.
- **Short phones** (about 667 px tall). Reduce the type a step so the title isn't pushed
  under the photo.
- **Re-test after every text edit.** Longer text is the usual way an overlap comes back.
- **Behind the text.** Give the panel a soft, edge-free wash of the paper color, so it
  stays readable over any image.

## Navigation and pages

- A chapter rail of dots or short labels: real links to each chapter's `id`, reachable by
  keyboard, with `aria-current` on the current one.
- An opening title over chapter 1 until the reader starts scrolling.
- A colophon at the end. See `writing.md`.

## Accessibility and performance

- Alt text starts with the image's kind and includes its date (see `writing.md`).
- Text has enough contrast over the paper color. Headings go in order. Set the page
  language.
- Respect `prefers-reduced-motion`. Don't hijack scrolling; the page scrolls normally and
  the stage follows it.
- Images: two WebP widths with `srcset` and `sizes`. The first image gets
  `fetchpriority="high"`, the rest `loading="lazy"`.
- Fonts: one or two families (a readable serif suits history), loaded with
  `display=swap`.

## Tooling (keep it small)

- **A local static server** bound to `127.0.0.1`, with a guard against paths like
  `../../`. A dozen lines in Node or Python. The site itself needs no build step.
- **Type checking.** If the person likes TypeScript, plain browser `.js` with JSDoc
  comments can be checked by `tsc` (`allowJs` + `checkJs`) and still ship as-is.
- **The image build script** (see `images.md`), plus one command per task in
  `package.json` scripts or a Makefile, listed in the README.

## Test checklist

Use a headless browser such as Playwright. Run at 1440×900 (desktop), 390×844 (phone)
and 375×667 (short phone).

For each chapter, scroll to about 35% of the way through it, then check:
- the visible text panel belongs to this chapter;
- the navigation marks this chapter as current;
- the image's box doesn't intersect the text's box;
- there are no page errors and no failed requests.

Save a few screenshots and look at them. Also:
- load the page with JavaScript off;
- load it with reduced motion on;
- tab through the chapter rail.

Rerun this after every copy or layout change, not only at the end.
