/* ============================================================
   OPRELL — inner pages only
   project gallery slider · fullscreen lightbox
   Requires common.js first ($, $$, lenis, bgEls). No gsap needed.
   ============================================================ */

/* ---------------- project gallery slider ---------------- */
const pdsImg = $('#pds-img');
const pdsThumbs = $$('.pds-thumb');
const pdsStage = $('#pds-stage');
let pdsIdx = 0;
const pdsSrc = i => pdsThumbs[i].querySelector('img').src;
const pdsShow = i => {
  if (!pdsThumbs.length) return;
  pdsIdx = (i + pdsThumbs.length) % pdsThumbs.length;
  pdsImg.src = pdsSrc(pdsIdx);
  pdsThumbs.forEach((t, j) => t.classList.toggle('on', j === pdsIdx));
  const c = $('#pds-count');
  if (c) c.textContent = String(pdsIdx + 1).padStart(2, '0') + ' / ' + String(pdsThumbs.length).padStart(2, '0');
  /* preload the next slide so the swap doesn't flash */
  const ahead = new Image();
  ahead.src = pdsSrc((pdsIdx + 1) % pdsThumbs.length);
};
if (pdsImg && pdsThumbs.length) {
  $('#pds-prev').addEventListener('click', e => { e.stopPropagation(); pdsShow(pdsIdx - 1); });
  $('#pds-next').addEventListener('click', e => { e.stopPropagation(); pdsShow(pdsIdx + 1); });
  pdsThumbs.forEach((t, i) => t.addEventListener('click', () => pdsShow(i)));
  let sx = 0, swiped = false;
  pdsStage.addEventListener('touchstart', e => {
    sx = e.touches[0].clientX; swiped = false;
  }, { passive: true });
  pdsStage.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 40) { swiped = true; pdsShow(pdsIdx + (dx < 0 ? 1 : -1)); }
  }, { passive: true });
  /* tap opens the lightbox — but a swipe must NOT also fire the click */
  pdsStage.addEventListener('click', () => {
    if (swiped) { swiped = false; return; }
    if (window.__lbOpen) window.__lbOpen(pdsIdx);
  });
}

/* ---------------- gallery lightbox ---------------- */
const lb = $('#lb');
if (lb) {
  const galItems = $$('.gal-item');
  const items = galItems.length ? galItems : pdsThumbs;
  const lbImg = $('#lb-img'), lbCount = $('#lb-count'), lbClose = $('#lb-close');
  let li = 0, lbOpen = false, lastFocus = null;

  const show = i => {
    li = (i + items.length) % items.length;
    lbImg.src = items[li].querySelector('img').src;
    lbCount.textContent = (li + 1) + ' / ' + items.length;
    if (items === pdsThumbs) pdsShow(li);
  };
  const openLb = i => {
    if (!items.length) return;
    lastFocus = document.activeElement;
    show(i);
    lb.classList.add('open'); lb.removeAttribute('inert');
    bgEls.forEach(el => el.setAttribute('inert', ''));   // keep Tab inside the lightbox
    lbOpen = true; lbClose.focus();
    if (lenis) lenis.stop();
  };
  const closeLb = () => {
    lb.classList.remove('open'); lb.setAttribute('inert', '');
    bgEls.forEach(el => el.removeAttribute('inert'));
    lbOpen = false;
    if (lenis) lenis.start();
    if (lastFocus) lastFocus.focus();
  };
  window.__lbOpen = openLb;   // lets the stage click handler above reach it

  galItems.forEach((b, i) => b.addEventListener('click', () => openLb(i)));
  lbClose.addEventListener('click', closeLb);
  $('#lb-prev').addEventListener('click', e => { e.stopPropagation(); show(li - 1); });
  $('#lb-next').addEventListener('click', e => { e.stopPropagation(); show(li + 1); });
  lb.addEventListener('click', e => { if (e.target === lb) closeLb(); });
  addEventListener('keydown', e => {
    if (!lbOpen) return;
    if (e.key === 'Escape') closeLb();
    if (e.key === 'ArrowLeft') show(li - 1);
    if (e.key === 'ArrowRight') show(li + 1);
  });
  let tx = 0;
  lb.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 50) show(li + (dx < 0 ? 1 : -1));
  }, { passive: true });
}
