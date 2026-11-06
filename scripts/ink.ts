// Render a real photograph in the site's ink-wash style, without AI.
//
// Every step is an ordinary, deterministic image filter: nothing is generated
// or invented, so every building, vehicle and person stays exactly as
// photographed. Only the rendering changes:
//
// 1. even out the contrast;
// 2. break the tones into soft ink-wash layers;
// 3. trace the photo's own edges as thin ink lines;
// 4. map paper white to cream and black to sepia ink;
// 5. enlarge with Lanczos and gentle sharpening, and let the borders fade into the paper.
//
// The filters are OpenCV's, compiled to WebAssembly (@techstark/opencv-js).

import cvModule from '@techstark/opencv-js';
import type { Mat } from '@techstark/opencv-js';

/** OpenCV, once its WebAssembly runtime is ready. */
export const cv: typeof cvModule = await cvModule;

/** Pixels in row-major order: 1 byte per pixel (gray) or 3 (RGB). */
export interface Raster {
  width: number;
  height: number;
  channels: number;
  data: Uint8Array;
}

export interface InkOptions {
  /** Output width in pixels (default 2048). */
  width?: number;
  /** Ink-wash tone layers (default 6). */
  levels?: number;
  /** Ink line strength, 0-1 (default 0.4). */
  lineStrength?: number;
  /** Fade the edges into the paper (default true). */
  border?: boolean;
}

const PAPER = [241, 233, 214]; // #f1e9d6, cream
const MID = [168, 142, 104]; // tan
const INK = [52, 44, 36]; // sepia-black

/** Copy a raster into a new Mat (delete it when done). */
export function toMat(img: Raster): Mat {
  const m = new cv.Mat(img.height, img.width, img.channels === 3 ? cv.CV_8UC3 : cv.CV_8UC1);
  m.data.set(img.data);
  return m;
}

/** Copy an 8-bit Mat out of the WebAssembly heap. */
export function fromMat(m: Mat): Raster {
  return { width: m.cols, height: m.rows, channels: m.channels(), data: m.data.slice() };
}

/** Round halves to the even neighbor, as the first version of this build did, so sizes stay put. */
export function roundHalfEven(v: number): number {
  const r = Math.round(v);
  return r - v === 0.5 && r % 2 !== 0 ? r - 1 : r;
}

/** The ink treatment for a grayscale photo; returns RGB at `width` pixels wide. */
export function ink(gray: Raster, { width = 2048, levels = 6, lineStrength = 0.4, border = true }: InkOptions = {}): Raster {
  const mats: { delete(): void }[] = [];
  const keep = <T extends { delete(): void }>(m: T): T => (mats.push(m), m);
  const mat = (rows?: number, cols?: number, type?: number): Mat =>
    keep(rows === undefined ? new cv.Mat() : new cv.Mat(rows, cols ?? 0, type ?? cv.CV_8UC1));
  const blur = (src: Mat, sigma: number): Mat => {
    const dst = mat();
    cv.GaussianBlur(src, dst, new cv.Size(0, 0), sigma);
    return dst;
  };
  // Typed-array views into the WebAssembly heap go stale when it grows, so
  // each loop below takes its views after the last allocation before it.

  try {
    const w0 = gray.width;
    const h0 = gray.height;
    const n = w0 * h0;

    // 1. Even out the contrast, at the photo's own resolution: enlarging first
    // only blurs what the filters then see.
    const src = keep(toMat(gray));
    const stretched = mat();
    cv.normalize(src, stretched, 0, 255, cv.NORM_MINMAX);
    const clahe = keep(new cv.CLAHE(1.4, new cv.Size(8, 8)));
    const g = mat();
    clahe.apply(stretched, g);
    // No denoise. The first version of this build ran OpenCV's
    // fastNlMeansDenoising (h=5) here, which opencv.js lacks; the substitutes
    // tried (bilateral, median) all came out further from its result than none
    // at all, and blurrier.

    // 2. Mostly the photo's own tone, with a faint hint of stepped ink washes.
    const tone = new Float32Array(256);
    const step = new Float32Array(256);
    for (let v = 0; v < 256; v++) {
      tone[v] = v / 255;
      step[v] = Math.min(1, Math.floor(Math.fround(tone[v] * levels)) / (levels - 1));
    }
    const stepped = mat(h0, w0, cv.CV_32FC1);
    {
      const gd = g.data;
      const sd = stepped.data32F;
      for (let i = 0; i < n; i++) sd[i] = step[gd[i]];
    }
    const steps = blur(stepped, 1.5);

    // 3. Thin ink lines on the photo's long structural edges only, so texture
    // (dirt, grass, grain) doesn't get outlined.
    const edges = mat();
    cv.Canny(blur(g, 1.0), edges, 60, 150);
    const labels = mat();
    const stats = mat();
    const count = cv.connectedComponentsWithStats(edges, labels, stats, mat(), 8, cv.CV_32S);
    const minLen = Math.max(30, Math.floor(w0 / 35));
    const long = new Float32Array(count);
    {
      const st = stats.data32S;
      for (let k = 1; k < count; k++) {
        const size = Math.max(st[k * 5 + cv.CC_STAT_WIDTH], st[k * 5 + cv.CC_STAT_HEIGHT]);
        long[k] = size >= minLen ? 1 : 0;
      }
    }
    const traced = mat(h0, w0, cv.CV_32FC1);
    {
      const lab = labels.data32S;
      const td = traced.data32F;
      for (let i = 0; i < n; i++) td[i] = long[lab[i]];
    }
    const lines = blur(traced, 0.7);

    // 4. Gradient map to cream paper and sepia ink (t: 1 = paper, 0 = ink).
    const color = mat(h0, w0, cv.CV_32FC3);
    {
      const gd = g.data;
      const sd = steps.data32F;
      const ld = lines.data32F;
      const cd = color.data32F;
      for (let i = 0; i < n; i++) {
        const wash = 1 - (1 - (0.2 * sd[i] + 0.8 * tone[gd[i]])) * 0.88;
        const t = Math.min(1, Math.max(0, wash * (1 - ld[i] * lineStrength)));
        for (let c = 0; c < 3; c++) {
          cd[i * 3 + c] = t > 0.5 ? MID[c] + (PAPER[c] - MID[c]) * ((t - 0.5) / 0.5) : INK[c] + (MID[c] - INK[c]) * (t / 0.5);
        }
      }
    }

    // 5. Enlarge with Lanczos and a gentle unsharp mask, then a whisper of grain.
    const height = roundHalfEven((h0 * width) / w0);
    const size = new cv.Size(width, height);
    const big = mat();
    cv.resize(color, big, size, 0, 0, cv.INTER_LANCZOS4);
    const sharp = mat();
    cv.addWeighted(big, 1.45, blur(big, 1.4), -0.45, 0, sharp);
    const noise = mat(height, width, cv.CV_32FC1);
    fillNormal(noise.data32F, mulberry32(1));
    const grain = blur(noise, 0.8);

    // The borders fade into the paper along a slightly irregular edge.
    const speckle = mat((height >> 4) + 1, (width >> 4) + 1, cv.CV_32FC1);
    const random = mulberry32(2);
    const sp = speckle.data32F;
    for (let i = 0; i < sp.length; i++) sp[i] = random();
    const rough = mat();
    cv.resize(blur(speckle, 1.5), rough, size, 0, 0, cv.INTER_LINEAR);

    const out = new Uint8Array(width * height * 3);
    const cd = sharp.data32F;
    const gr = grain.data32F;
    const ro = rough.data32F;
    for (let y = 0, i = 0; y < height; y++) {
      const fy = Math.min(y, height - 1 - y) / (height * 0.12);
      for (let x = 0; x < width; x++, i++) {
        let m = 1;
        if (border) {
          m = Math.min(1, Math.max(0, Math.min(Math.min(x, width - 1 - x) / (width * 0.1), fy)));
          m = Math.min(1, Math.max(0, m * 1.15 - (ro[i] - 0.5) * 0.5));
          m = m * m * (3 - 2 * m);
        }
        for (let c = 0; c < 3; c++) {
          const v = PAPER[c] + (cd[i * 3 + c] + gr[i] * 2 - PAPER[c]) * m;
          out[i * 3 + c] = v < 0 ? 0 : v > 255 ? 255 : v; // truncates, like numpy's astype
        }
      }
    }
    return { width, height, channels: 3, data: out };
  } finally {
    for (const m of mats) m.delete();
  }
}

// Seeded randomness for the grain and the ragged border, the same on every build.
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), a | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Standard normal samples (Box-Muller).
function fillNormal(out: Float32Array, rand: () => number): void {
  for (let i = 0; i < out.length; i += 2) {
    const r = Math.sqrt(-2 * Math.log(1 - rand()));
    const a = 2 * Math.PI * rand();
    out[i] = r * Math.cos(a);
    if (i + 1 < out.length) out[i + 1] = r * Math.sin(a);
  }
}
