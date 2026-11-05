# Storyboard

A scroll-driven ink-wash history of New Bremen, Ohio, in ten chapters. One fixed
full-screen stage shows a painting per chapter; scrolling moves a slow camera
across it, then the next painting bleeds in like ink spreading on wet paper. Text
sits in the painting's empty space and fades out before each transition.

The display copy lives in `index.html`. Facts and their sources are in
[sources.md](sources.md). Image prompts are drafted in
[image-prompts.md](image-prompts.md).

## Visual approach

- **Most chapters:** a still painting with a slow camera move (zoom and drift)
  and an ink-bleed reveal into the next chapter. This is all done in the
  browser, so each chapter costs one image.
- **Two video moments:** chapters 3 (canal boat entering Lock One) and 8 (the
  interurban on Main Street) are candidates for short generated clips, scrubbed
  by scroll. The page falls back to the still if a clip is missing.
- **Style:** warm, fibrous paper; gray-green and sepia ink washes; soft
  architectural edges; drifting mist; restrained color. Later chapters can warm
  up (gaslight gold in 7, festival color in 9 and 10) but must still read as the
  same painting.
- **Markers:** a small red seal with the chapter's year, like a painter's chop.

## Chapters

| # | Year | Title | Copy | Main composition | Transition into the next chapter |
|---|------|-------|------|------------------|----------------------------------|
| 1 | Before 1832 | The Divide | left | Flat wetland at dawn: reeds, standing water, a low rise. Two thin streams leave the rise in opposite directions. Mist over everything. | Mist thickens; the camera pushes through the reeds toward a clearing. |
| 2 | 1832–1833 | Bremen in the Clearing | right | A small log hut in a partly cleared rise, chimney smoke, a covered wagon and a few figures, survey stakes in the ground. Forest edge behind. | Smoke drifts right and becomes the canal's mist. |
| 3 | 1845 | The Canal Comes Through | left | A canal boat drawn by three mules in tandem on the towpath, approaching the wooden gates of Lock One. **Video candidate.** | The boat passes out of frame; the lock opens onto a busy bank. |
| 4 | 1850 | A Canal Boomtown | right | Canal-side street: a two-story hotel, stacked barrels, a cooper's shop, a boat being loaded. Busy but small. | Ink spreads from the barrels across the bank. |
| 5 | 1871 | Iron Rails | left | Quiet canal and empty towpath in the foreground; a small steam train crossing the far distance on a low embankment. | The train's smoke becomes cloud over two rooftops. |
| 6 | 1875–1876 | Frogtown and Cheesequarters | bottom | High view down the canal, which splits two clusters of rooftops; a footbridge joins them. | Dusk falls; lamps begin to glow. |
| 7 | 1888–1896 | Gaslight and an Opera House | right | Dusk street, gas flames in lamps, the Boesel Opera House with warm windows, a small crowd. First gold accents. | Glow from the windows spreads into morning light on Main Street. |
| 8 | 1902–1931 | The Interurban | left | An electric interurban car on Main Street under its overhead wire, storefronts on both sides. **Video candidate.** | The car rolls out; bunting appears along the street. |
| 9 | 1933 | The Centennial | right | Main Street in bunting and flags, a parade, crowds on the sidewalks. No lettering on banners. | Confetti and flags soften into trees along the towpath. |
| 10 | Today | Still on the Divide | bottom | Restored Lock One, the towpath trail under trees, a cyclist, festival lights far off. Same paper and ink as chapter 1. | End. The page's closing credits scroll over it. |

## Layout rules

- The copy column sits in the painting's empty third (`left`, `right`, or
  `bottom`), so every composition must leave that area quiet. The image prompts
  say which side to leave open.
- On narrow screens the copy moves to a bottom panel, and the canvas crops
  around each chapter's focus point (`data-focus` in `index.html`).
- Copy is hidden during transitions. The opening title shows over chapter 1
  until the reader starts scrolling.

## Production gates

1. Approve this storyboard and the copy.
2. Generate three style samples (chapters 1, 5 and 10) and approve the look.
3. Generate the remaining stills.
4. Decide on the two video moments and generate them from the approved stills.
5. Ask the New Bremen Historic Association before publishing anything based on
   their photos.
