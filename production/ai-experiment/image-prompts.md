# Image prompts (draft)

Drafts to work through together. Nothing has been generated yet. Start with the
three style samples (chapters 1, 5 and 10); generate the rest only after the
look is approved.

## Output spec

- 16:9, ideally 2560 x 1440 or larger (the free playground tops out at 1K,
  which is fine for samples). Save the lossless master to
  `production/masters/` (not published), then run `python3 scripts/process_art.py`.
- No text, lettering, signatures, borders or frames in the image.
- Leave the copy side quiet (paper, mist, sky or water), as noted per scene.
- Keep the main subject inside the central 60% so phones can crop to it.

## Style preamble

Prepend to every prompt:

> Traditional East Asian ink-wash painting technique applied to a
> nineteenth-century Ohio canal town. Warm, fibrous off-white paper with visible
> grain. Gray-green and sepia ink washes in layered tones, soft architectural
> edges, dry-brush texture on foreground details, drifting mist that dissolves
> forms into the paper. Restrained color: mostly ink, with muted touches of
> brick red and canal-water teal. Quiet, contemplative, hand-painted, not
> photographic. Wide 16:9 composition.

## Recurring subjects

Keep these consistent across chapters; reuse the earlier image as a reference
when the tool allows it.

- **The canal:** straight, narrow, stone-edged, with a towpath on the east bank.
- **Lock One:** a single chamber with wooden gates and balance beams.
- **Main Street:** two-story brick storefronts with cornices, wide unpaved
  street before 1906.

## Scenes

1. **The Divide** (copy left; subject right): Flat wetland at dawn on the edge of
   a great swamp. Reeds and standing water, a barely raised rise of land. Two
   thin streams leave the rise in opposite directions. Heavy mist, no people,
   no buildings. Leave the left third as pale mist.
2. **Bremen in the Clearing** (copy right; subject left): A small log hut on a
   partly cleared rise at the forest edge, chimney smoke, a covered wagon, a
   few figures in 1830s clothing, survey stakes in the ground. Leave the right
   third as open sky and mist.
3. **The Canal Comes Through** (copy left; subject right): A long wooden canal
   boat drawn by three mules in tandem on the towpath, a driver walking beside
   them, approaching the wooden gates of a canal lock. Leave the left third as
   still water and sky.
4. **A Canal Boomtown** (copy right; subject left): A canal-side street around
   1850: a two-story frame hotel, stacked barrels, a cooper's shop, a boat
   being loaded, small figures at work. Leave the right third as water and mist.
5. **Iron Rails** (copy left; subject right): A quiet canal with an empty
   towpath in the foreground; far off, a small steam locomotive with a short
   train crosses on a low embankment, its smoke trailing. Leave the left third
   as sky.
6. **Frogtown and Cheesequarters** (copy bottom; subject top half): A high view
   down a straight canal that divides two clusters of rooftops and church
   steeples, joined by a small footbridge. Keep the bottom third as mist.
7. **Gaslight and an Opera House** (copy right; subject left): A small-town
   street at dusk around 1890, gas flames in iron lamp posts, a two-story brick
   opera house with warm glowing windows, a small crowd. First gold accents in
   the light. Leave the right third as dusk sky.
8. **The Interurban** (copy left; subject right): A single electric interurban
   railway car on a small-town main street around 1910, overhead trolley wire,
   brick storefronts on both sides, a few pedestrians. Leave the left third as
   pale street and sky.
9. **The Centennial** (copy right; subject left): Main Street in 1933 dressed in
   bunting and flags, a small parade, crowds along the sidewalks. Banners with
   no lettering. Leave the right third as sky with drifting flags.
10. **Still on the Divide** (copy bottom; subject top half): The restored canal
    lock today under tall trees, a paved towpath trail beside it, one cyclist,
    soft festival lights far off. Same paper and ink as scene 1. Keep the
    bottom third as water and mist.

## Video moments (later)

Generate from the approved stills, first and last frame where the tool supports
it. Keep motion slow and continuous with no cuts, so it scrubs well backward.

- **Chapter 3:** "The boat glides slowly forward into the lock; the mules keep
  walking; mist drifts left. Preserve the ink-wash texture."
- **Chapter 8:** "The interurban car rolls slowly down the street toward the
  viewer; pedestrians shift; the overhead wire sways slightly. Preserve the
  ink-wash texture."
