/* ============================================================
   OPRELL — inner pages only
   project gallery slider · fullscreen lightbox
   Requires common.js first ($, $$, lenis, bgEls). No gsap needed.
   ============================================================ */

/* ---------------- deck sliders (per-section, atzedent-style) ---------------- */
const deckRots = $$('.pd-deck').map(deck => {
  const track = deck.querySelector('.deck-track');
  const kids = () => [...track.children];
  const hydrate = () => kids().slice(0, 7).forEach(li => {
    const im = li.querySelector('img');
    if (im.dataset.src) { im.src = im.dataset.src; delete im.dataset.src; }
  });
  const prog = deck.querySelector('.deck-prog i');
  const bg = deck.querySelector('.deck-bg');
  const ni = kids().length;
  const chips = deck.closest('.pd-body').querySelectorAll('.sec-chip');
  const updProg = () => {
    const li = kids()[1];
    if (!li) return;
    if (prog) prog.style.width = ((+li.dataset.i + 1) / ni * 100) + '%';
    if (chips.length) chips.forEach(c =>
      c.classList.toggle('on', c.dataset.sec === li.dataset.sec));
    if (bg) {
      const im = li.querySelector('img');
      const url = im.dataset.src || im.src;
      if (url && bg.dataset.cur !== url) {
        bg.dataset.cur = url;
        bg.style.backgroundImage = `url("${url}")`;
      }
    }
  };
  const upgrade = () => {   // swap the active slide to its full-res source
    const li = kids()[1], im = li && li.querySelector('img');
    if (im && im.dataset.full) {
      const want = new URL(im.dataset.full, location.href).href;
      if (im.src !== want) im.src = want;
    }
    updProg();
  };
  const rot = dir => {
    const items = kids();
    if (dir > 0) track.append(items[0]);
    else track.prepend(items[items.length - 1]);
    hydrate();
    upgrade();
  };
  const seek = i => {                    // rotate until slide i is active
    const items = kids();
    const pos = items.findIndex(li => +li.dataset.i === i);
    if (pos < 0) return;
    const stepsF = (pos - 1 + items.length) % items.length;
    const fwd = stepsF <= items.length - stepsF; // shortest way around
    while (+kids()[1].dataset.i !== i) {
      if (fwd) track.append(track.children[0]);
      else track.prepend(track.children[track.children.length - 1]);
    }
    hydrate();
    upgrade();
  };
  chips.forEach(c => c.addEventListener('click', () => seek(+c.dataset.i)));
  upgrade();
  deck.querySelector('.deck-next').addEventListener('click',
    e => { e.stopPropagation(); rot(1); });
  deck.querySelector('.deck-prev').addEventListener('click',
    e => { e.stopPropagation(); rot(-1); });
  track.addEventListener('click', e => {
    const li = e.target.closest('.deck-slide');
    if (!li) return;
    const idx = kids().indexOf(li);
    if (idx === 1) {
      const gi = $$('.deck-slide, .gal-item').indexOf(li);
      if (window.__lbOpen && gi > -1) window.__lbOpen(gi);
    } else if (idx > 1) {
      for (let k = 0; k < idx - 1; k++) track.append(track.children[0]);
      hydrate();
      upgrade();
    }
  });
  let sx = 0, dragging = false;
  deck.addEventListener('touchstart', e => {
    sx = e.touches[0].clientX; dragging = true;
  }, { passive: true });
  deck.addEventListener('touchmove', e => {
    if (!dragging) return;
    const dx = e.touches[0].clientX - sx;
    deck.style.setProperty('--x-off',
      Math.max(-60, Math.min(60, dx)) + 'px');
  }, { passive: true });
  deck.addEventListener('touchend', e => {
    if (!dragging) return;
    dragging = false;
    deck.style.setProperty('--x-off', '0px');
    const dx = e.changedTouches[0].clientX - sx;
    if (dx < -50) rot(1); else if (dx > 50) rot(-1);
  }, { passive: true });
  return rot;
});
/* arrow keys drive whichever deck is in the middle of the viewport */
addEventListener('keydown', e => {
  if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
  if ($('#lb.open')) return;
  const i = $$('.pd-deck').findIndex(el => {
    const r = el.getBoundingClientRect();
    return r.top < innerHeight / 2 && r.bottom > innerHeight / 2;
  });
  if (i > -1) deckRots[i](e.key === 'ArrowRight' ? 1 : -1);
});

/* ---------------- projects filter ---------------- */
const pf = $('.pfilter');
if (pf) {
  const cards = $$('.pgrid .pcard');
  const chips = $$('.pf-chip');
  const sIn = $('#pf-search'), cnt = $('#pf-count');
  const ltags = $$('.pcard-ltag');
  let sector = 'all', loc = 'all';
  const apply = () => {
    const q = sIn.value.trim().toLowerCase();
    let n = 0;
    cards.forEach(c => {
      const ok = (sector === 'all' || c.dataset.s === sector)
        && (loc === 'all' || c.dataset.loc === loc)
        && (!q || c.textContent.toLowerCase().includes(q));
      c.classList.toggle('off', !ok);
      if (ok) n++;
    });
    ltags.forEach(t => t.classList.toggle('on',
      loc !== 'all' && t.closest('.pcard').dataset.loc === loc));
    cnt.textContent = n + ' project' + (n === 1 ? '' : 's');
  };
  chips.forEach(x => x.addEventListener('click', () => {
    sector = x.dataset.s;
    chips.forEach(c => c.classList.toggle('on', c === x));
    apply();
  }));
  sIn.addEventListener('input', apply);
  $$('.pcard-tag').forEach(t => t.addEventListener('click', e => {
    e.preventDefault();
    e.stopPropagation();
    const card = t.closest('.pcard');
    if (t.classList.contains('pcard-ltag')) {
      loc = loc === card.dataset.loc ? 'all' : card.dataset.loc;
    } else {
      sector = card.dataset.s;
      chips.forEach(c => c.classList.toggle('on', c.dataset.s === sector));
    }
    apply();
  }));
  apply();
}

/* ---------------- gallery lightbox ---------------- */
const lb = $('#lb');
if (lb) {
  const items = $$('.gal-item, .deck-slide');
  const lbImg = $('#lb-img'), lbCount = $('#lb-count'), lbClose = $('#lb-close');
  let li = 0, lbOpen = false, lastFocus = null;

  const show = i => {
    li = (i + items.length) % items.length;
    const im = items[li].querySelector('img');
    lbImg.src = im.dataset.full || im.src;
    lbCount.textContent = (li + 1) + ' / ' + items.length;
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
