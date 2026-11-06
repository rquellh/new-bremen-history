# Storyboard

A scroll-driven ink-wash history of New Bremen, Ohio, in eleven chapters. One fixed
full-screen stage shows a painting per chapter; scrolling moves a slow camera
across it, then the next painting bleeds in like ink spreading on wet paper. Text
sits in the painting's empty space and fades out before each transition.

The display copy lives in `index.html`. Facts and their sources are in
[sources.md](sources.md). Image prompts are drafted in
[image-prompts.md](image-prompts.md).

## Visual approach

- **Real photographs only.** Each chapter shows one photo from the New Bremen
  Historic Association's galleries, whole and uncropped, with its real date and
  credit. It is rendered in ink tones with ordinary image filters, so nothing is
  invented (see `production/photos.toml` and `scripts/build_photos.py`).
- **On the page:** the photo sits like a print on the side opposite the text; on
  phones it sits above the text. A slow camera move, then the next photo bleeds
  in like ink spreading on wet paper.
- **Paper:** warm cream mulberry paper with fibers, laid over everything.

## Chapters

| # | Year | Title | Copy | Photo |
|---|------|-------|------|------------------|
| 1 | Before 1832 | The Divide | left | Strawberry fields at the Walnut Hill Fruit Farm, 1909. The land is still this flat. |
| 2 | 1832–1833 | Bremen in the Clearing | right | The Luelleman House, begun in 1837, now the association's museum. |
| 3 | 1845 | The Canal Comes Through | left | The canal at Lock One, looking north, after 1904. |
| 4 | 1850 | A Canal Boomtown | right | August Schneider and Henry Wiegman at their barrel shop, 1898. |
| 5 | 1871 | Iron Rails | left | The New Bremen railroad depot, photographed in 1962. |
| 6 | 1875–1876 | Frogtown and Cheesequarters | bottom | Looking south from St. Paul Church, about 1900. |
| 7 | 1888–1896 | Gaslight and an Opera House | right | The crew installing natural gas lines to New Bremen, 1888. |
| 8 | 1902–1931 | The Interurban | left | Looking north on Main Street from Monroe Street as a Western Ohio Railway car approaches, early 1900s. |
| 9 | 1933 | The Centennial | right | An ox-drawn covered wagon in the 1933 Centennial Parade. |
| 10 | 1930s–1970s | The Speedway | right | A race car takes a turn in front of the grandstand at the New Bremen Speedway, early years. |
| 11 | Today | The Story Continues | bottom | The restored canal and towpath trail, 2018. |

## Layout rules

- The copy column sits in the painting's empty third (`left`, `right`, or
  `bottom`), so every composition must leave that area quiet. The image prompts
  say which side to leave open.
- On narrow screens the copy moves to a bottom panel, and the canvas crops
  around each chapter's focus point (`data-focus` in `index.html`).
- Copy is hidden during transitions. The opening title shows over chapter 1
  until the reader starts scrolling.

## Before publishing

1. Ask the New Bremen Historic Association for permission to show their photos.
2. Check the open items at the bottom of sources.md.
