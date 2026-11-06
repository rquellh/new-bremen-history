// Build the chapter images from real photographs listed in production/photos.toml.
//
//     npm run photos               # every chapter
//     npm run photos -- 03-canal   # just one
//
// For each photo it:
// 1. downloads the original into production/references/ (git-ignored) if missing;
// 2. removes captions written or printed on the photo (the `clean` rectangles),
//    filling only the writing itself from the surrounding pixels (OpenCV inpainting);
// 3. renders it in the ink style (scripts/ink.ts), inventing nothing;
// 4. writes WebPs to assets/art/ and a before/after preview of any cleaning to
//    production/masters/photos/;
// 5. points the chapter's image, alt text, caption and credit in index.html at it.

import { existsSync } from 'node:fs';
import { mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { parseArgs } from 'node:util';
import sharp from 'sharp';
import { parse } from 'smol-toml';
import { cv, fromMat, ink, roundHalfEven, toMat, type Raster } from './ink.ts';

const ROOT = join(import.meta.dirname, '..');
const CONFIG = join(ROOT, 'production', 'photos.toml');
const ORIGINALS = join(ROOT, 'production', 'references');
const PREVIEWS = join(ROOT, 'production', 'masters', 'photos');
const ART = join(ROOT, 'assets', 'art');
const PAGE = join(ROOT, 'index.html');
const WIDTHS = [2048, 1280];
const QUALITY = 82;

/** One [[photo]] entry in photos.toml. */
interface Photo {
  file: string;
  nbha: string;
  url: string;
  credit: string;
  kind?: string; // "photograph" (default) or "drawing"
  clean?: number[][]; // [x, y, w, h] rectangles, as fractions of the photo
}

async function fetchOriginal(photo: Photo): Promise<string> {
  const slug = photo.nbha.toLowerCase().replaceAll('nbha', '').replaceAll('photos', '').trim().replaceAll(' ', '-');
  const dest = join(ORIGINALS, `${photo.file}--nbha-${slug}.jpg`);
  if (!existsSync(dest)) {
    const res = await fetch(photo.url, {
      headers: { 'User-Agent': 'new-bremen-history-build/1.0' },
      signal: AbortSignal.timeout(60_000),
    });
    if (!res.ok) throw new Error(`${photo.url}: HTTP ${res.status}`);
    await writeFile(dest, new Uint8Array(await res.arrayBuffer()));
    console.log(`  downloaded ${photo.nbha}`);
  }
  return dest;
}

/** Decode to 8-bit gray as OpenCV's imread does: EXIF rotation applied, ICC profile ignored. */
async function readGray(path: string): Promise<Raster> {
  const { data, info } = await sharp(path, { ignoreIcc: true, autoOrient: true })
    .removeAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const img = { width: info.width, height: info.height, channels: info.channels, data: new Uint8Array(data) };
  if (img.channels === 1) return img;
  const rgb = toMat(img);
  const gray = new cv.Mat();
  try {
    cv.cvtColor(rgb, gray, cv.COLOR_RGB2GRAY);
    return fromMat(gray);
  } finally {
    rgb.delete();
    gray.delete();
  }
}

/** Fill in writing inside the given rectangles. Returns the cleaned photo and the pixels filled. */
function clean(gray: Raster, rects: number[][]): { cleaned: Raster; filled: number } {
  const { width: w, height: h } = gray;
  const src = toMat(gray);
  const background = new cv.Mat();
  const strokes = new cv.Mat();
  const mask = cv.Mat.zeros(h, w, cv.CV_8UC1);
  const kernel = cv.Mat.ones(5, 5, cv.CV_8UC1);
  const dilated = new cv.Mat();
  const cleaned = new cv.Mat();
  try {
    // Writing is a thin stroke that differs sharply from its neighborhood.
    cv.medianBlur(src, background, 21);
    cv.absdiff(src, background, strokes);
    cv.threshold(strokes, strokes, 28, 255, cv.THRESH_BINARY);
    const sd = strokes.data;
    const md = mask.data;
    const clamp = (v: number, hi: number) => Math.min(Math.max(Math.trunc(v), 0), hi);
    for (const [x, y, rw, rh] of rects) {
      const [x0, x1] = [clamp(x * w, w), clamp((x + rw) * w, w)];
      const [y0, y1] = [clamp(y * h, h), clamp((y + rh) * h, h)];
      for (let row = y0; row < y1; row++) md.set(sd.subarray(row * w + x0, row * w + x1), row * w + x0);
    }
    cv.dilate(mask, dilated, kernel);
    cv.inpaint(src, dilated, cleaned, 9, cv.INPAINT_TELEA);
    return { cleaned: fromMat(cleaned), filled: cv.countNonZero(dilated) };
  } finally {
    for (const m of [src, background, strokes, mask, kernel, dilated, cleaned]) m.delete();
  }
}

/** Shrink an RGB raster with area averaging. */
function resizeArea(img: Raster, width: number, height: number): Raster {
  const src = toMat(img);
  const dst = new cv.Mat();
  try {
    cv.resize(src, dst, new cv.Size(width, height), 0, 0, cv.INTER_AREA);
    return fromMat(dst);
  } finally {
    src.delete();
    dst.delete();
  }
}

async function build(photo: Photo): Promise<void> {
  console.log(photo.file);
  let gray = await readGray(await fetchOriginal(photo));
  if (photo.clean?.length) {
    const { cleaned, filled } = clean(gray, photo.clean);
    await mkdir(PREVIEWS, { recursive: true });
    const preview = Buffer.concat([gray.data, cleaned.data]); // before above after
    await sharp(preview, { raw: { width: gray.width, height: gray.height * 2, channels: 1 } })
      .png()
      .toFile(join(PREVIEWS, `${photo.file}-clean.png`));
    console.log(`  cleaned ${filled} px of written caption`);
    gray = cleaned;
  }
  const inked = ink(gray, { width: WIDTHS[0] });
  for (const width of WIDTHS) {
    const height = roundHalfEven((inked.height * width) / inked.width);
    const img = width === inked.width ? inked : resizeArea(inked, width, height);
    const out = join(ART, `${photo.file}-${width}.webp`);
    await sharp(img.data, { raw: { width: img.width, height: img.height, channels: 3 } })
      .webp({ quality: QUALITY })
      .toFile(out);
    console.log(`  ${relative(ROOT, out)}  ${width}x${height}  ${Math.floor((await stat(out)).size / 1024)} KB`);
  }
  await syncPage(photo, inked.width, inked.height);
}

/** Point the chapter's image, alt text, caption and credit in index.html at this photo. */
async function syncPage(photo: Photo, width: number, height: number): Promise<void> {
  const before = await readFile(PAGE, 'utf8');
  const f = photo.file;
  const credit = escapeHtml(photo.credit);
  const kind = photo.kind ?? 'photograph'; // or "drawing"
  const label = kind === 'drawing' ? 'Drawing' : 'Photo';
  const lazy = f.startsWith('01') ? 'fetchpriority="high"' : 'loading="lazy"';
  const figure =
    `<figure class="art">\n        <img src="assets/art/${f}-1280.webp" ` +
    `srcset="assets/art/${f}-1280.webp 1280w, assets/art/${f}-2048.webp 2048w" ` +
    `sizes="(max-width: 720px) 100vw, 60vw" width="${width}" height="${height}" ${lazy}\n` +
    `             alt="${kind[0].toUpperCase()}${kind.slice(1).toLowerCase()}: ${credit}">\n` +
    `        <figcaption>${credit} New Bremen Historic Association.</figcaption>\n      </figure>`;
  const found = new RegExp(`<figure class="art">\\s*<img src="assets/art/${escapeRegExp(f)}-1280\\.webp"[\\s\\S]*?</figure>`).exec(before);
  if (!found) {
    console.error(`  index.html: no figure found for ${f}; left unchanged`);
    return;
  }
  let page = before.slice(0, found.index) + figure + before.slice(found.index + found[0].length);
  // The credit line in the same chapter: the first one after this figure.
  const creditRe = /<p class="credit">(?:Photo|Drawing): [\s\S]*?<\/p>/g;
  creditRe.lastIndex = found.index;
  const line = creditRe.exec(page);
  if (line) {
    const updated = `<p class="credit">${label}: ${credit} <span>New Bremen Historic Association</span></p>`;
    page = page.slice(0, line.index) + updated + page.slice(line.index + line[0].length);
  }
  if (page === before) {
    console.log('  index.html already up to date');
    return;
  }
  await writeFile(PAGE, page, 'utf8');
  console.log('  index.html updated');
}

// Escape text for HTML, with a curly apostrophe.
function escapeHtml(s: string): string {
  return s
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&rsquo;');
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

async function main(): Promise<number> {
  const { values, positionals } = parseArgs({ allowPositionals: true, options: { help: { type: 'boolean', short: 'h' } } });
  if (values.help) {
    console.log('usage: npm run photos [-- file ...]   chapter files to build, e.g. 03-canal (default: all)');
    return 0;
  }
  const photos = (parse(await readFile(CONFIG, 'utf8')) as unknown as { photo: Photo[] }).photo;
  const picked = photos.filter((p) => !positionals.length || positionals.includes(p.file));
  if (!picked.length) {
    console.error('no matching photos');
    return 1;
  }
  await mkdir(ORIGINALS, { recursive: true });
  await mkdir(ART, { recursive: true });
  for (const photo of picked) await build(photo);
  return 0;
}

process.exitCode = await main();
