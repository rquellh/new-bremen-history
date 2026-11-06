// Turns the chapters into a scroll-driven story. Each <section class="chapter">
// is a stretch of scroll; its position drives the painting stage, the copy
// fades, and the chapter rail. Chapter settings come from data attributes:
//   data-span   scroll length in viewport heights (default 3)
//   data-focus  "x y" point of the painting to keep in view when cropped
//   data-zoom   "from to" camera zoom across the chapter
//   data-drift  "x y" camera drift across the chapter, as a fraction of the screen
//   data-bleed  "x y" point the ink spreads from when this chapter arrives
//   data-video  optional clip, scrubbed by scroll in place of the still
//   data-fit    "contain" (default: the whole photo beside the text) or "cover"
// and on each .copy, data-show="in out" in chapter progress (0..1).

import { Stage, smooth } from './stage.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const TRANSITION_VH = 0.9; // scroll length of each ink transition, in viewport heights
const FADE = 0.06; // copy fade length, in chapter progress

const nums = (value, fallback) => (value || fallback).trim().split(/\s+/).map(Number);

const chapterEls = [...document.querySelectorAll('.chapter')];
const railLinks = [...document.querySelectorAll('.rail a')];

const scenes = chapterEls.map((el, index) => {
  const img = el.querySelector('.art img');
  const span = Number(el.dataset.span || 3);
  el.style.setProperty('--span', span);
  return {
    index,
    el,
    id: el.id,
    span,
    transition: index === chapterEls.length - 1 ? 0 : Math.min(0.4, TRANSITION_VH / span),
    focus: nums(el.dataset.focus, '0.5 0.5'),
    zoom: nums(el.dataset.zoom, '1 1.05'),
    drift: nums(el.dataset.drift, '0 0'),
    bleed: nums(el.dataset.bleed, '0.5 0.5'),
    image: img && {
      aspect: Number(img.getAttribute('height')) / Number(img.getAttribute('width')) || 0.7,
      src: img.getAttribute('src'),
      srcset: img.getAttribute('srcset'),
      sizes: img.getAttribute('sizes'),
    },
    video: el.dataset.video || null,
    // "contain" lays the whole photo beside the text; "cover" fills the screen.
    fit: el.dataset.fit || 'contain',
    side: (el.querySelector('.copy:not(.opening)')?.className.match(/copy--(left|right|bottom|center)/) || [])[1] || 'left',
    copies: [...el.querySelectorAll('.copy')].map((node) => ({
      node,
      show: nums(node.dataset.show, '0.06 0.66'),
      o: -1,
    })),
    top: 0,
    height: 1,
  };
});

const stage = new Stage(document.querySelector('.stage'), scenes, { reduceMotion });

// Phone layout (matches stage.js printBox): the photo runs full width, its
// top just under the chapter dots, with the text right below it.
const phone = window.matchMedia('(max-width: 720px)');
const PHOTO_TOP = 44; // px, clear of the chapter dots
const PHOTO_GAP = 14; // px between the photo's faded edge and the text
const PHOTO_SCALE = 1.22; // the photo is drawn this much wider than the screen

function placeCopy(s, inner) {
  const copy = inner.parentElement;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  let top = 0;
  if (phone.matches && vw < vh && s.image) {
    // If the photo at full width plus the text fit on screen, start the text
    // under the photo and leave the spare room at the bottom. Otherwise the
    // text stays at the bottom and the photo shrinks to fit above it.
    const textTop = PHOTO_TOP + vw * PHOTO_SCALE * s.image.aspect + PHOTO_GAP;
    const bottomPad = parseFloat(getComputedStyle(copy).paddingBottom) || 24;
    if (textTop + inner.offsetHeight + bottomPad <= vh) top = textTop;
  }
  copy.classList.toggle('is-top', top > 0);
  copy.style.setProperty('--copy-top', `${Math.round(top)}px`);
}

function measure() {
  for (const s of scenes) {
    const r = s.el.getBoundingClientRect();
    s.top = r.top + window.scrollY;
    s.height = r.height;
    // Top of the chapter's text panel on screen (it's fixed, so this ignores
    // scroll); phones place the photo just above it.
    const inner = s.el.querySelector('.copy:not(.opening) .copy__inner');
    if (inner) placeCopy(s, inner);
    s.copyTop = inner ? inner.offsetTop : 0;
  }
}

// Which chapter the top of the viewport is in, and how far through it.
function locate(y) {
  if (y <= scenes[0].top) return { index: 0, p: 0 };
  for (const s of scenes) {
    if (y < s.top + s.height) return { index: s.index, p: (y - s.top) / s.height };
  }
  return { index: scenes.length - 1, p: 1 };
}

function updateCopy(y) {
  for (const s of scenes) {
    const p = (y - s.top) / s.height;
    for (const c of s.copies) {
      const [a, b] = c.show;
      let o = smooth(a, a + FADE, p) * (1 - smooth(b - FADE, b, p));
      o = Math.round(o * 1000) / 1000;
      if (o === c.o) continue;
      c.o = o;
      c.node.style.opacity = o;
      const shift = reduceMotion || o >= 1 ? 0 : (1 - o) * (p < (a + b) / 2 ? 14 : -14);
      c.node.style.transform = shift ? `translate3d(0, ${shift.toFixed(1)}px, 0)` : '';
      c.node.classList.toggle('is-visible', o > 0.01);
    }
  }
}

let railIndex = -1;
function updateRail(index, p) {
  const s = scenes[index];
  const i = s.transition && p > 1 - s.transition / 2 ? index + 1 : index;
  if (i === railIndex) return;
  railIndex = i;
  // Match links by chapter id; the opening has no link, so nothing is current there.
  const href = `#${scenes[i]?.id}`;
  railLinks.forEach((a) => {
    if (a.getAttribute('href') === href) a.setAttribute('aria-current', 'step');
    else a.removeAttribute('aria-current');
  });
}

// The stage eases toward the scroll position so wheel steps feel like a
// brush moving, not a slideshow. Big jumps (chapter links) snap.
let shown = null;
let currentIndex = -1;
let lastTime = 0;
let rafId = 0;

function frame(now) {
  rafId = 0;
  const y = window.scrollY;
  const { index, p } = locate(y);
  const target = index + p;

  if (index !== currentIndex) {
    currentIndex = index;
    stage.prepare(index);
  }
  updateCopy(y);
  updateRail(index, p);

  const dt = lastTime ? Math.min(64, now - lastTime) : 16;
  lastTime = now;
  if (shown === null || reduceMotion || Math.abs(target - shown) > 1.2) shown = target;
  else shown += (target - shown) * (1 - Math.exp(-dt / 110));
  if (Math.abs(target - shown) < 0.0005) shown = target;

  stage.render(shown);

  if (shown !== target) request();
  else lastTime = 0;
}

function request() {
  if (!rafId) rafId = requestAnimationFrame(frame);
}
stage.onChange = request;

function onResize() {
  measure();
  stage.resize();
  stage.dirty = true;
  request();
}

function scrollToScene(s, behavior) {
  const offset = s.index === 0 ? 0 : s.height * 0.12; // land where the copy is showing
  window.scrollTo({ top: s.top + offset, behavior });
}

document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  const s = scenes.find((sc) => `#${sc.id}` === a.getAttribute('href'));
  if (!s) return;
  e.preventDefault();
  scrollToScene(s, reduceMotion ? 'auto' : 'smooth');
  history.replaceState(null, '', `#${s.id}`);
});

window.addEventListener('scroll', request, { passive: true });
window.addEventListener('resize', onResize);
window.addEventListener('pageshow', onResize);

measure();
stage.resize();
const fromHash = scenes.find((s) => `#${s.id}` === window.location.hash);
if (fromHash) scrollToScene(fromHash, 'auto');
request();
