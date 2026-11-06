# Images: choosing, configuring and treating them

## Choosing

For each chapter, gather three to six candidates and show them to the person with their
captions and dates. Good picks:
- **Show what a sentence says.** A photo of the actual rotator plant beats a generic
  factory exterior when the text is about antenna rotators.
- **Have people or activity:** a barrel shop with its coopers, a race car mid-turn, a
  parade. Empty buildings are the fallback.
- **Read at phone width.** Landscape images work best, both beside the text on desktop
  and full width on phones. Very tall images get small.
- **Vary across the site:** street scenes, interiors, an aerial, an event, a portrait.
- **Are what the caption says.** Check identifications. Compare details such as roofs,
  posts and signs with another dated photo, and write down how you matched them.
- **Have the right date, or show it.** An image from later than its chapter is fine if the
  credit says when it's from.

When nothing fits, use a map, plat, drawing, newspaper clipping or postcard, labelled as
such. Don't make an image.

## One config file drives the images

Keep a per-chapter config (`production/photos.toml` or JSON) and have the build script
write the page's `<img>`, alt text and credit from it. Then the visible credit, the alt
text and the image never drift apart.

```toml
[[photo]]
file   = "03-canal"                  # output name, also the chapter's image slug
source = "Archive photos199"         # the archive's own id
url    = "https://…/photos199.jpg"   # exact URL, copied from the gallery HTML
credit = "The canal at Lock One, looking north, after 1904."
kind   = "photograph"                # or "drawing", "map", "postcard"
clean  = [[0.02, 0.86, 0.40, 0.12]]  # optional: areas with added writing, as fractions [x, y, w, h]
```

- Download originals into a git-ignored folder (`production/references/`).
- Commit only the treated outputs, and only once permission allows.

## Treatment: an ink look with ordinary filters

This is the pipeline the example site uses. It turns a mixed set of old prints, faded,
yellowed and over-contrasted, into one consistent warm ink-on-paper look without
inventing anything. The values are starting points to tune by eye.

1. **Grayscale.** To keep color instead, skip steps 3 and 5 and just even out contrast.
2. **Even out contrast at the original resolution.** Stretch to the full range, then apply
   CLAHE (adaptive histogram equalization, clip about 1.4, 8×8 tiles). Do this before
   enlarging: enlarging first only blurs what the filters see.
3. **Tone.** Mostly the photo's own tone, blended lightly with a stepped version (about 6
   levels) for a hint of ink washes.
4. **Lines.** Run Canny edge detection (thresholds 60/150) on a lightly blurred copy.
   - Keep only connected edges longer than about `max(30 px, width / 35)`, so texture
     such as grass, gravel and film grain doesn't get outlined.
   - Darken the image along those edges by about 0.4.
5. **Color.** A gradient map from paper cream (#f1e9d6) through tan (#a88e68) to sepia
   ink (#342c24).
6. **Size.** Enlarge to 2048 px wide with Lanczos, plus a gentle unsharp mask (about
   1.45 × image − 0.45 × blurred at sigma 1.4).
7. **Grain.** A whisper of film grain from a seeded random generator, so every build is
   identical.
8. **Edges.** Fade into the paper along a slightly irregular border.
9. **Export.** WebP at 2048 and 1280 px wide, quality about 80. A 14-chapter site came to
   about 4 MB in all.

**Tools.** Either stack works; use whichever language the person prefers.
- **Node:** `sharp` to decode and encode, and `@techstark/opencv-js` (OpenCV compiled to
  WebAssembly). The WebAssembly build lacks some functions, such as
  `fastNlMeansDenoising`. Skipping denoise worked better than the substitutes tried.
- **Python:** `opencv-python-headless` and `Pillow`.

**Check every output beside its original at full size.** The filter must never turn one
thing into another, such as a smudge into a figure or a shadow into a doorway. If it
does, lower the line strength or the stepped-tone blend for that image.

## Removing added writing

Archive prints often carry handwritten captions, stamped numbers or inked notes. These
can be removed because they're not part of the scene. Signs, storefront lettering, banners
and printed postcard titles that belong to the artifact all stay.

1. A person chooses the rectangle that holds the writing. Never detect it automatically
   across the whole image.
2. Inside the rectangle, find thin strokes: the absolute difference from a median-blurred
   copy (kernel about 21), a threshold of about 28, then a dilate of a few pixels.
3. Fill only those pixels with classical inpainting (OpenCV Telea, radius about 9). The
   rest of the rectangle stays untouched.
4. Save a before/after preview and look at it.
5. Mention the removal in the colophon.

## Things not to do

- Cropping to fit the layout. Show the whole image and let the layout adapt.
- AI upscaling, colorizing, face restoration or generative fill. They invent detail.
- Generating an image for a chapter that has none.
- Animating stills into video.

If the person wants any of these anyway, explain the risk once. If they still want it,
label it clearly on the page.
