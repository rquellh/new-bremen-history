// The painting stage: one fixed canvas that shows a chapter's painting with a
// slow camera move, then bleeds the next painting in like ink spreading on wet
// paper. A chapter can also have a video, scrubbed by scroll; until it loads (or
// if it fails) its still painting is shown instead.

const PAPER = '#efe7d6';
const INK = [29, 35, 32];
const FRINGE_ALPHA = 0.45; // darkness of the wet edge of the spreading ink
const EDGE = 0.06; // softness of the ink edge, in field units

export class Stage {
  constructor(canvas, scenes, { reduceMotion = false } = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d', { alpha: false });
    this.scenes = scenes;
    this.reduceMotion = reduceMotion;
    this.onChange = () => {};

    // Offscreen buffers: the incoming painting, its reveal mask, and the ink fringe.
    this.layer = document.createElement('canvas');
    this.lctx = this.layer.getContext('2d');
    this.mask = document.createElement('canvas');
    this.mctx = this.mask.getContext('2d');
    this.fringe = document.createElement('canvas');
    this.fctx = this.fringe.getContext('2d');

    this.fields = new Map();
    this.last = null;
    this.dirty = true;
    for (const s of scenes) s.media = { image: null, video: null, loading: false };
  }

  resize() {
    const small = window.innerWidth < 720;
    const dpr = Math.min(window.devicePixelRatio || 1, small ? 1.5 : 2);
    const W = Math.round(window.innerWidth * dpr);
    const H = Math.round(window.innerHeight * dpr);
    if (W === this.canvas.width && H === this.canvas.height) return;

    this.canvas.width = this.layer.width = W;
    this.canvas.height = this.layer.height = H;

    // The reveal is computed at low resolution and scaled up; the scaling is
    // what softens the edge into a wash.
    const mw = small ? 240 : 400;
    const mh = Math.max(2, Math.round((mw * H) / W));
    this.mask.width = this.fringe.width = mw;
    this.mask.height = this.fringe.height = mh;
    this.maskData = this.mctx.createImageData(mw, mh);
    this.fringeData = this.fctx.createImageData(mw, mh);
    const fd = this.fringeData.data;
    for (let j = 0; j < fd.length; j += 4) {
      fd[j] = INK[0];
      fd[j + 1] = INK[1];
      fd[j + 2] = INK[2];
    }

    this.fields.clear();
    this.dirty = true;
  }

  // Load media near the current chapter and free what is far away.
  prepare(index) {
    this.scenes.forEach((s, j) => {
      const d = j - index;
      if (d >= -1 && d <= 2) this.load(s);
      else if (d < -2 || d > 3) this.release(s);
    });
    const next = this.scenes[index + 1];
    if (next && !this.reduceMotion) idle(() => this.field(next));
  }

  load(s) {
    const m = s.media;
    if (s.image && !m.image && !m.loading) {
      m.loading = true;
      const im = new Image();
      im.decoding = 'async';
      if (s.image.sizes) im.sizes = s.image.sizes;
      if (s.image.srcset) im.srcset = s.image.srcset;
      im.src = s.image.src;
      im.decode()
        .catch(() => {})
        .then(() => {
          m.loading = false;
          if (!im.naturalWidth) return;
          // SVGs are rasterized once; redrawing a filtered SVG every frame is slow.
          m.image = /\.svg([?#]|$)/i.test(im.currentSrc || im.src) ? rasterize(im) : im;
          this.dirty = true;
          this.onChange();
        });
    }
    if (s.video && !this.reduceMotion && !m.video) {
      const v = document.createElement('video');
      v.muted = true;
      v.playsInline = true;
      v.preload = 'auto';
      v.src = s.video;
      const redraw = () => {
        this.dirty = true;
        this.onChange();
      };
      v.addEventListener('loadeddata', redraw);
      v.addEventListener('seeked', redraw);
      v.addEventListener('error', () => {
        m.video = null;
        redraw();
      });
      // Muted inline play is allowed without a gesture; it wakes the decoder on iOS.
      v.play().then(() => v.pause()).catch(() => {});
      m.video = v;
    }
  }

  release(s) {
    const m = s.media;
    if (m.image instanceof HTMLCanvasElement) {
      m.image.width = m.image.height = 0;
      m.image = null;
    }
    if (m.video) {
      m.video.removeAttribute('src');
      m.video.load();
      m.video = null;
    }
  }

  ready(s) {
    const { image, video } = s.media;
    return Boolean(image || (video && video.readyState >= 2));
  }

  // g is the story position: chapter index plus progress through it (0..1).
  render(g) {
    if (!this.dirty && g === this.last) return;
    this.dirty = false;
    this.last = g;

    const N = this.scenes.length;
    const i = Math.max(0, Math.min(Math.floor(g), N - 1));
    const s = this.scenes[i];
    const p = Math.min(Math.max(g - i, 0), 1);
    const T = s.transition;
    const hold = 1 - T;
    const ctx = this.ctx;

    if (!T || p <= hold) {
      this.draw(ctx, s, T ? p / hold : p);
      return;
    }

    const t = (p - hold) / T;
    const next = this.scenes[i + 1];
    this.draw(ctx, s, 1);
    if (!this.ready(next)) return;

    if (this.reduceMotion) {
      ctx.globalAlpha = smooth(0, 1, t);
      this.draw(ctx, next, 0);
      ctx.globalAlpha = 1;
      return;
    }

    const W = this.canvas.width;
    const H = this.canvas.height;
    this.paintMasks(next, smooth(0, 1, t));

    const l = this.lctx;
    l.globalCompositeOperation = 'source-over';
    l.clearRect(0, 0, W, H);
    this.draw(l, next, 0);
    l.globalCompositeOperation = 'destination-in';
    l.imageSmoothingQuality = 'high';
    l.drawImage(this.mask, 0, 0, W, H);
    l.globalCompositeOperation = 'source-over';

    ctx.drawImage(this.layer, 0, 0);
    ctx.globalAlpha = FRINGE_ALPHA;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(this.fringe, 0, 0, W, H);
    ctx.globalAlpha = 1;
  }

  // Draw a scene cover-fit, with its camera move at progress u (0..1).
  draw(ctx, s, u) {
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    const W = this.canvas.width;
    const H = this.canvas.height;
    const { image, video } = s.media;
    let src = null;
    let sw = 0;
    let sh = 0;

    if (video && video.readyState >= 2 && video.videoWidth) {
      const dur = video.duration;
      if (Number.isFinite(dur) && dur > 0) {
        const want = clamp(u, 0, 1) * Math.max(0, dur - 0.04);
        if (!video.seeking && Math.abs(video.currentTime - want) > 1 / 60) video.currentTime = want;
      }
      src = video;
      sw = video.videoWidth;
      sh = video.videoHeight;
    } else if (image) {
      src = image;
      sw = image.naturalWidth || image.width;
      sh = image.naturalHeight || image.height;
    }

    if (!src) {
      ctx.fillStyle = PAPER;
      ctx.fillRect(0, 0, W, H);
      return;
    }

    const e = smooth(0, 1, u);
    const [z0, z1] = s.zoom;

    if (s.fit === 'contain') {
      // The whole photograph, uncropped, laid on the page beside the text like
      // a print. Its ink-treated edges already fade into the paper.
      ctx.fillStyle = PAPER;
      ctx.fillRect(0, 0, W, H);
      const px = W / window.innerWidth; // CSS px to canvas px
      const box = printBox(s.side, W, H, s.copyTop ? s.copyTop * px : 0, px);
      const z = this.reduceMotion ? 1 : z0 + (z1 - z0) * e;
      const scale = Math.min(box.w / sw, box.h / sh) * Math.min(z, 1.06);
      const dw = sw * scale;
      const dh = sh * scale;
      let x = box.x + (box.w - dw) / 2;
      // Phones: rest the photo on the text below it. Elsewhere: center it.
      let y = box.anchorBottom ? box.y + box.h - dh : box.y + (box.h - dh) / 2;
      if (!this.reduceMotion) {
        x += s.drift[0] * W * e;
        y += s.drift[1] * H * e;
      }
      ctx.drawImage(src, x, y, dw, dh);
      return;
    }

    const z = this.reduceMotion ? 1 : Math.max(1, z0 + (z1 - z0) * e);
    const scale = Math.max(W / sw, H / sh) * z;
    const dw = sw * scale;
    const dh = sh * scale;
    let x = (W - dw) * s.focus[0];
    let y = (H - dh) * s.focus[1];
    if (!this.reduceMotion) {
      x += s.drift[0] * W * e;
      y += s.drift[1] * H * e;
    }
    x = clamp(x, W - dw, 0);
    y = clamp(y, H - dh, 0);
    ctx.drawImage(src, x, y, dw, dh);
  }

  // The reveal order for a scene: low values fill first. Distance from the
  // scene's bleed point, pushed around by warped noise so the ink creeps in
  // tendrils. Detail finer than a few mask pixels would turn into blocks when
  // the mask is scaled up, so the noise stays smooth at that scale.
  field(s) {
    let f = this.fields.get(s.index);
    if (f) return f;
    const w = this.mask.width;
    const h = this.mask.height;
    const aspect = this.canvas.width / this.canvas.height;
    const [ox, oy] = s.bleed;
    const seed = 101 + s.index * 7919;

    f = new Float32Array(w * h);
    let min = Infinity;
    let max = -Infinity;
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const nx = x / (w - 1);
        const ny = y / (h - 1);
        const d = Math.hypot((nx - ox) * aspect, ny - oy);
        const px = nx * aspect * 2.2;
        const py = ny * 2.2;
        const wx = fbm(px + 3.1, py + 1.7, seed, 4);
        const wy = fbm(px - 2.3, py + 4.9, seed + 3, 4);
        const n = fbm(px + 1.6 * wx, py + 1.6 * wy, seed + 9, 5);
        const v = d * 0.8 + n * 0.75;
        f[y * w + x] = v;
        if (v < min) min = v;
        if (v > max) max = v;
      }
    }
    const span = max - min || 1;
    for (let k = 0; k < f.length; k++) f[k] = (f[k] - min) / span;
    this.fields.set(s.index, f);
    return f;
  }

  paintMasks(s, t) {
    const f = this.field(s);
    const md = this.maskData.data;
    const fd = this.fringeData.data;
    const tt = t * (1 + 2 * EDGE) - EDGE; // t=0 shows nothing, t=1 shows everything
    for (let k = 0, j = 3; k < f.length; k++, j += 4) {
      const a = smooth(f[k] - EDGE, f[k] + EDGE, tt);
      md[j] = a * 255;
      fd[j] = 4 * a * (1 - a) * 255;
    }
    this.mctx.putImageData(this.maskData, 0, 0);
    this.fctx.putImageData(this.fringeData, 0, 0);
  }
}

// Where a photo sits on the page: opposite its chapter's text. On a tall
// (phone) screen the text is a bottom panel, so the photo spans the width just
// above it; its faded sides run slightly off the screen edges.
function printBox(side, W, H, copyTop, px) {
  if (W / H < 1) {
    const top = 44 * px; // clear of the chapter dots
    const bottom = copyTop ? copyTop - 14 * px : H * 0.55;
    // Never taller than the space above the text, so it can't cover it.
    return { x: -W * 0.11, y: top, w: W * 1.22, h: Math.max(H * 0.06, bottom - top), anchorBottom: true };
  }
  if (side === 'right') return { x: W * 0.04, y: H * 0.08, w: W * 0.52, h: H * 0.84 };
  if (side === 'bottom') {
    // Stop above the text, however tall it runs.
    const bottom = Math.min(H * 0.61, copyTop ? copyTop - 18 * px : H);
    return { x: W * 0.1, y: H * 0.05, w: W * 0.8, h: Math.max(H * 0.3, bottom - H * 0.05) };
  }
  return { x: W * 0.4, y: H * 0.08, w: W * 0.49, h: H * 0.84 };
}

function rasterize(img) {
  const c = document.createElement('canvas');
  c.width = img.naturalWidth;
  c.height = img.naturalHeight;
  c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
  return c;
}

const idle = window.requestIdleCallback
  ? (fn) => window.requestIdleCallback(fn, { timeout: 800 })
  : (fn) => setTimeout(fn, 120);

export function clamp(v, lo, hi) {
  return v < lo ? lo : v > hi ? hi : v;
}

export function smooth(a, b, v) {
  const t = clamp((v - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
}

function hash(ix, iy, seed) {
  let h = Math.imul(ix, 374761393) ^ Math.imul(iy, 668265263) ^ Math.imul(seed, 2246822519);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}

function vnoise(x, y, seed) {
  const ix = Math.floor(x);
  const iy = Math.floor(y);
  const fx = x - ix;
  const fy = y - iy;
  const u = fx * fx * (3 - 2 * fx);
  const v = fy * fy * (3 - 2 * fy);
  const a = hash(ix, iy, seed);
  const b = hash(ix + 1, iy, seed);
  const c = hash(ix, iy + 1, seed);
  const d = hash(ix + 1, iy + 1, seed);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}

function fbm(x, y, seed, octaves) {
  let sum = 0;
  let amp = 0.5;
  let freq = 1;
  let norm = 0;
  for (let o = 0; o < octaves; o++) {
    sum += amp * vnoise(x * freq, y * freq, seed + o * 17);
    norm += amp;
    amp *= 0.5;
    freq *= 2.03;
  }
  return sum / norm;
}
