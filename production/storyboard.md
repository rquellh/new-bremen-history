# Storyboard

A scroll-driven ink-wash history of New Bremen, Ohio, in fourteen chapters. One fixed
full-screen stage shows each chapter's photo; scrolling moves a slow camera
over it, then the next photo bleeds in like ink spreading on wet paper. Text
sits beside the photo (below it on phones) and fades out before each transition.

The display copy lives in `index.html`. Facts and their sources are in
[sources.md](sources.md).

## Visual approach

- **Real photographs only.** Each chapter shows one photo from the New Bremen
  Historic Association's galleries, whole and uncropped, with its real date and
  credit. It is rendered in ink tones with ordinary image filters, so nothing is
  invented (see `production/photos.toml` and `scripts/build-photos.ts`).
- **On the page:** the photo sits like a print on the side opposite the text; on
  phones it sits above the text. A slow camera move, then the next photo bleeds
  in like ink spreading on wet paper.
- **Paper:** warm cream mulberry paper with fibers, laid over everything.

## Chapters

| # | Year | Title | Copy | Photo |
|---|------|-------|------|------------------|
| 1 | Before 1832 | The Divide | left | Strawberry fields at the Walnut Hill Fruit Farm, 1909. |
| 2 | 1832–1833 | Bremen in the Clearing | right | Drawing: The Luelleman House, built about 1837. |
| 3 | 1845 | The Canal Comes Through | left | The canal at Lock One, looking north, after 1904. |
| 4 | 1850 | A Canal Boomtown | right | August Schneider and Henry Wiegman at a barrel shop, 1898. |
| 5 | 1871 | Iron Rails | left | The New Bremen railroad depot, 1962. |
| 6 | 1875–1876 | Frogtown and Cheesequarters | bottom | Looking south from St. Paul Church, about 1900. |
| 7 | 1888–1896 | Gaslight and an Opera House | right | A play on the opera house stage, early 1900s. |
| 8 | 1902–1931 | The Interurban | left | Looking north from Monroe Street as a Western Ohio Railway car approaches, early 1900s. |
| 9 | 1930s–1970s | The Speedway | right | A race car takes a turn in front of the grandstand at the New Bremen Speedway. |
| 10 | 1933 | The Centennial | left | An ox-drawn covered wagon in the 1933 Centennial Parade. |
| 11 | 1945 | Crown | right | Crown's former antenna rotator plant, in the old Rabe Hardware Store building, 1970s. |
| 12 | 1968–1976 | Saving the Story | left | The Luelleman House, now the association's museum, 2024. |
| 13 | Since the mid-1970s | Bremenfest | right | A band plays in the gazebo of a Bremenfest float carrying the 1975 Bremenfest queen. |
| 14 | Today | The Story Continues | bottom | The canal through the middle of town, with the Crown Pavilion beside it, 2019. |

## Layout rules

- Each chapter's copy sits on one side (`left`, `right` or `bottom`, from its
  `copy--` class in `index.html`). On desktop the photo is drawn whole, like a
  print, on the opposite side: on the right for `left` copy, on the left for
  `right` copy, and above the text for `bottom` copy, stopping short of the
  text however tall it runs.
- On phones in portrait, the photo runs full width at the top, just below the
  chapter dots, with its faded sides slightly off the screen edges. The text
  follows right under it. If the photo and the text don't both fit, the text
  stays at the bottom and the photo shrinks to fit the space above it.
- The placement is set by `printBox` in `assets/js/stage.js` and `placeCopy`
  in `assets/js/main.js`.
- Copy is hidden during transitions. The opening title shows over chapter 1
  until the reader starts scrolling.

## Before publishing

1. Ask the New Bremen Historic Association for permission to show their photos.
2. Check the open items at the bottom of sources.md.
