/* ============================================================
   OPRELL — homepage only
   hero carousel · word rotator · before/after · process line
   Requires common.js first ($, $$, ANIM, FX, REDUCED, lenis).
   Everything degrades gracefully without gsap.
   ============================================================ */

/* ---------------- hero image settle (was tied to loader) ---------------- */
if (ANIM) gsap.to('.hero-carousel img', { scale: 1, duration: 1.6, ease: 'power3.out', delay: .2 });

/* ---------------- services — cards swipe up on scroll ---------------- */
if (ANIM) $$('.svcard').forEach(card => {
  gsap.fromTo(card, { y: 110, opacity: 0, scale: .96 }, {
    y: 0, opacity: 1, scale: 1, ease: 'none',
    scrollTrigger: { trigger: card, start: 'top 98%', end: 'top 58%', scrub: .8 }
  });
});

/* ---------------- hero slider — swipe ---------------- */
const hImgs = $$('#hero-carousel img');
const dotsBox = $('#hero-dots');
const hCar = $('#hero-carousel');
const HN = hImgs.length;
let hCur = 0, hTimer = null, swiping = false;
let swIdx = -1, swDir = 0;         // incoming slide index + direction (+1 next / -1 prev)

/* per-slide context for the floating chips */
const HERO_CTX = [
  { b: 'Hattan Villa',    s: 'Arabian Ranches — Dubai', y: 'Residential', t: 'Renovation',    href: 'project-hattan-villa/' },
  { b: 'Landscape & Pools', s: 'Outdoor works — UAE',   y: 'Landscape',   t: 'Design + build', href: 'project-landscape/' },
  { b: 'CFO Office',      s: 'Jafza LOB 17 — Dubai',    y: 'Commercial',  t: 'Fit-out',        href: 'project-cfo-office/' },
];
const chipA = $('#chip-a'), chipB = $('#chip-b'), chipM = $('#chip-m');
const setCtx = i => {
  const c = HERO_CTX[i % HERO_CTX.length];
  [chipA, chipB, chipM].forEach(ch => { if (ch) ch.href = c.href; });
  chipA.innerHTML = `<b>${c.b}</b><span>${c.s}</span>`;
  chipB.innerHTML = `<b>${c.y}</b><span>${c.t}</span>`;
  if (chipM) chipM.innerHTML = `<b>${c.b}</b><span>${c.s} →</span>`;
  if (ANIM) gsap.fromTo([chipA, chipB], { opacity: 0, y: 10 },
    { opacity: 1, y: 0, duration: .55, ease: 'power3.out', stagger: .08, delay: .15 });
};

const updateUI = () => {
  [...dotsBox.children].forEach((d, i) => {
    d.classList.toggle('on', i === hCur);
    d.toggleAttribute('aria-current', i === hCur);
  });
  setCtx(hCur);
};

if (HN > 1) {
  hImgs.forEach((_, i) => {
    const d = document.createElement('button');
    d.type = 'button';
    d.setAttribute('aria-label', 'Go to slide ' + (i + 1));
    if (!i) { d.classList.add('on'); d.setAttribute('aria-current', 'true'); }
    dotsBox.appendChild(d);
  });

  const stop = () => { clearInterval(hTimer); hTimer = null; };
  const auto = () => { if (!REDUCED && !hTimer) hTimer = setInterval(() => go(1), 5500); };

  let go;
  if (ANIM) {
    const cW = () => hCar.offsetWidth;
    const begin = (dir, idx) => {            // stage the incoming slide at the edge
      swDir = dir;
      swIdx = idx !== undefined ? idx : (hCur + dir + HN) % HN;
      hImgs[swIdx].classList.add('on');
      gsap.set(hImgs[hCur], { x: 0 });
      gsap.set(hImgs[swIdx], { x: dir * cW() });
    };
    const settle = commit => {               // snap to the slide or back
      const incoming = hImgs[swIdx], outgoing = hImgs[hCur];
      swiping = true;
      gsap.to(outgoing, { x: commit ? -swDir * cW() : 0, duration: .55, ease: 'power3.out' });
      gsap.to(incoming, { x: commit ? 0 : swDir * cW(), duration: .55, ease: 'power3.out',
        onComplete() {
          (commit ? outgoing : incoming).classList.remove('on');
          gsap.set(commit ? outgoing : incoming, { x: 0 });
          if (commit) { hCur = swIdx; updateUI(); }
          swiping = false; swIdx = -1; swDir = 0;
        }});
    };
    go = (dir, idx) => {                     // arrows / dots / autoplay
      if (swiping || startX !== null) return;
      if (idx !== undefined && (idx === hCur || idx >= HN)) return;
      begin(dir, idx);
      settle(true);
    };

    /* swipe — slides follow the finger */
    let startX = null, swDx = 0;
    hCar.addEventListener('pointerdown', e => {
      if (swiping || e.target.closest('.hc-arrow')) return;
      stop();                                // don't let autoplay hijack the drag
      startX = e.clientX; swDx = 0;
      hCar.classList.add('used');
      hCar.setPointerCapture(e.pointerId);
    });
    hCar.addEventListener('pointermove', e => {
      if (startX === null || swiping) return;
      const dx = e.clientX - startX;
      swDx = dx;
      const dir = dx < -8 ? 1 : dx > 8 ? -1 : 0;
      if (dir && dir !== swDir) {            // reversing direction mid-swipe
        if (swIdx >= 0) { hImgs[swIdx].classList.remove('on'); gsap.set(hImgs[swIdx], { x: 0 }); }
        begin(dir);
      }
      if (swIdx >= 0) {
        gsap.set(hImgs[hCur], { x: dx });
        gsap.set(hImgs[swIdx], { x: dx + swDir * cW() });
      }
    });
    const endSwipe = () => {
      if (startX === null) return;
      startX = null;
      if (swIdx < 0 || swiping) return;
      settle(Math.abs(swDx) > cW() * 0.18);  // past 18% of width → commit
      if (!hCar.matches(':hover')) auto();   // resume autoplay unless still hovering
    };
    hCar.addEventListener('pointerup', endSwipe);
    hCar.addEventListener('pointercancel', endSwipe);
  } else {
    /* no-gsap fallback — instant/fade switch, same controls */
    let downX = null;
    go = (dir, idx) => {
      const next = idx !== undefined ? idx : (hCur + dir + HN) % HN;
      if (next === hCur || next >= HN) return;
      hImgs[hCur].classList.remove('on');
      hImgs[next].classList.add('on');
      hCur = next; updateUI();
    };
    hCar.addEventListener('pointerdown', e => { downX = e.clientX; stop(); });
    hCar.addEventListener('pointerup', e => {
      if (downX === null) return;
      const dx = e.clientX - downX; downX = null;
      if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1);
      auto();
    });
  }

  auto();
  [...dotsBox.children].forEach((d, i) => d.addEventListener('click', () => {
    stop(); go(i > hCur ? 1 : -1, i); auto();
  }));
  $('#hc-prev').addEventListener('click', e => { e.stopPropagation(); stop(); go(-1); auto(); });
  $('#hc-next').addEventListener('click', e => { e.stopPropagation(); stop(); go(1); auto(); });
  hCar.addEventListener('mouseenter', stop);
  hCar.addEventListener('mouseleave', () => { if (!hTimer) auto(); });
  document.addEventListener('visibilitychange', () =>
    document.hidden ? stop() : auto());
}

/* ---------------- hero word rotator — letter flip ---------------- */
(() => {
  const rw = $('.rw'), words = $$('.rw i');
  if (!rw || words.length < 2) return;
  words.forEach(w => {
    w.innerHTML = [...w.textContent].map(c => `<b>${c}</b>`).join('');
  });
  let wi = 0, busy = false;
  const sizeTo = () => { rw.style.width = words[wi].offsetWidth + 'px'; };
  sizeTo();
  /* first measure ran before the webfont — re-measure once it lands */
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(sizeTo);
  if (!ANIM) return;
  const flip = () => {
    if (busy) return; busy = true;
    const out = words[wi], next = words[(wi + 1) % words.length];
    wi = (wi + 1) % words.length;
    const outChars = out.querySelectorAll('b'), inChars = next.querySelectorAll('b');
    const outDur = .38 + outChars.length * .022;   // let the old word fully leave first
    gsap.to(outChars, {
      yPercent: -115, opacity: 0, duration: .38, ease: 'power2.in', stagger: .022,
      onComplete: () => { out.classList.remove('on'); gsap.set(outChars, { yPercent: 0, opacity: 1 }); }
    });
    gsap.to(rw, { width: next.offsetWidth, duration: .55, ease: 'power3.inOut', delay: outDur * .5 });
    next.classList.add('on');
    gsap.fromTo(inChars,
      { yPercent: 115, opacity: 0 },
      { yPercent: 0, opacity: 1, duration: .5, ease: 'power3.out', stagger: .024, delay: outDur,
        onComplete: () => { busy = false; } });
  };
  setInterval(flip, 3600);
})();

/* ---------------- hero media tilt + chip parallax ---------------- */
if (FX) {
  const media = $('#hero-media'), chips = $$('.hero-chip');
  media.addEventListener('mousemove', e => {
    const r = media.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
    gsap.to(media, { rotateY: px * 3.5, rotateX: -py * 3, duration: .8, ease: 'power3.out', transformPerspective: 1400 });
    gsap.to(chips[0], { x: px * -18, y: py * -14, duration: .8, ease: 'power3.out' });
    gsap.to(chips[1], { x: px * 22, y: py * 16, duration: .8, ease: 'power3.out' });
  });
  media.addEventListener('mouseleave', () => {
    gsap.to(media, { rotateX: 0, rotateY: 0, duration: .9, ease: 'power3.out' });
    chips.forEach(c => gsap.to(c, { x: 0, y: 0, duration: .9, ease: 'power3.out' }));
  });
}

/* ---------------- before / after slider ---------------- */
(() => {
  const ba = $('#ba'), wrap = $('#ba-before-wrap'), handle = $('#ba-handle'), ui = $('#ba-ui');
  if (!ba) return;
  const setPct = p => {
    p = Math.min(Math.max(p, 2), 98);
    wrap.style.width = p + '%';
    handle.style.left = p + '%';
    handle.setAttribute('aria-valuenow', Math.round(p));
    wrap.querySelector('img').style.width = ba.offsetWidth + 'px';
    if (ui) ui.style.clipPath = `inset(0 0 0 ${p}%)`;
  };
  const setX = x => {
    const r = ba.getBoundingClientRect();
    setPct((x - r.left) / r.width * 100);
  };
  setPct(50);
  addEventListener('resize', () => setPct(parseFloat(wrap.style.width) || 50));

  /* invite: gentle sweep when it scrolls into view */
  if (ANIM) ScrollTrigger.create({
    trigger: ba, start: 'top 70%', once: true,
    onEnter() {
      const proxy = { p: 50 };
      gsap.timeline()
        .to(proxy, { p: 66, duration: 1.0, ease: 'power3.inOut', onUpdate: () => setPct(proxy.p) })
        .to(proxy, { p: 46, duration: 1.0, ease: 'power3.inOut', onUpdate: () => setPct(proxy.p) });
    }
  });

  /* only engage after a real horizontal move — taps meant to scroll don't jiggle the handle */
  let drag = false, armed = false, sx = 0;
  ba.addEventListener('pointerdown', e => {
    if (e.target.closest('.ba-spot')) return;
    armed = true; sx = e.clientX;
    ba.setPointerCapture(e.pointerId);
  });
  ba.addEventListener('pointermove', e => {
    if (!armed) return;
    if (!drag && Math.abs(e.clientX - sx) > 6) { drag = true; ba.classList.add('used'); }
    if (drag) setX(e.clientX);
  });
  const endDrag = () => { armed = false; drag = false; };
  addEventListener('pointerup', endDrag);
  ba.addEventListener('pointercancel', endDrag);

  /* keyboard access — the handle is a real slider */
  handle.addEventListener('keydown', e => {
    const cur = parseFloat(handle.getAttribute('aria-valuenow')) || 50;
    let p = cur;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') p -= 4;
    else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') p += 4;
    else if (e.key === 'Home') p = 2;
    else if (e.key === 'End') p = 98;
    else return;
    e.preventDefault();
    ba.classList.add('used');
    setPct(p);
  });

  /* hotspots — tap toggles the note (hover still works on desktop) */
  const spots = $$('.ba-spot');
  spots.forEach(sp => sp.addEventListener('click', e => {
    e.stopPropagation();
    const was = sp.classList.contains('open');
    spots.forEach(o => o.classList.remove('open'));
    if (!was) sp.classList.add('open');
  }));
  document.addEventListener('click', () =>
    spots.forEach(o => o.classList.remove('open')));
})();

/* ---------------- process — dashed curve through the cards ---------------- */
(() => {
  const wrap = $('#pcwrap'), line = $('#pc-line'), fill = $('#pc-fl');
  const cells = $$('.pcell'), badges = $$('.pcell-n');
  if (!wrap || !cells.length) return;

  let L = 0, fracs = [];
  const narrow = matchMedia('(max-width:1024px)');   // 2-col/1-col grids: the snake crosses cards
  const draw = () => {
    if (narrow.matches) {
      line.setAttribute('d', ''); fill.setAttribute('d', '');
      cells.forEach(c => c.classList.add('step-on'));
      return;
    }
    const wr = wrap.getBoundingClientRect();
    const pts = badges.map(b => {
      const r = b.getBoundingClientRect();
      return { x: r.left - wr.left + r.width / 2, y: r.top - wr.top + r.height / 2, r: r.width / 2 + 5 };
    });
    // bowed segments between badges — alternates direction so the line snakes
    let d = '';
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1], b = pts[i];
      const dx = b.x - a.x, dy = b.y - a.y, dist = Math.hypot(dx, dy) || 1;
      const ux = dx / dist, uy = dy / dist;
      const x0 = a.x + ux * a.r, y0 = a.y + uy * a.r;
      const x1 = b.x - ux * b.r, y1 = b.y - uy * b.r;
      const mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
      const bow = (i % 2 ? 1 : -1) * Math.min(38, dist * 0.22);
      d += ` M ${x0.toFixed(1)} ${y0.toFixed(1)} Q ${(mx - uy * bow).toFixed(1)} ${(my + ux * bow).toFixed(1)}, ${x1.toFixed(1)} ${y1.toFixed(1)}`;
    }
    line.setAttribute('d', d); fill.setAttribute('d', d);
    $('#pc-svg').setAttribute('viewBox', `0 0 ${wrap.offsetWidth} ${wrap.offsetHeight}`);
    L = line.getTotalLength();
    fill.style.strokeDasharray = `${L * 0.26} ${L}`;
    fill.style.strokeDashoffset = 0;
    // badge positions as fractions along the path
    fracs = pts.map(p => {
      let best = 0, bd = 1e9;
      for (let s = 0; s <= 200; s++) {
        const pt = line.getPointAtLength(L * s / 200);
        const dd = Math.hypot(pt.x - p.x, pt.y - p.y);
        if (dd < bd) { bd = dd; best = s / 200; }
      }
      return best;
    });
  };
  draw();
  addEventListener('load', draw);
  addEventListener('resize', draw);
  narrow.addEventListener('change', draw);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);

  /* continuous travelling pulse — always animating */
  if (ANIM) {
    const pulse = { v: 0 };
    gsap.to(pulse, {
      v: 1, duration: 4.6, ease: 'none', repeat: -1,
      onUpdate() {
        if (narrow.matches) return;   // draw() already lit every step
        fill.style.strokeDashoffset = -(pulse.v * L);
        cells.forEach((c, i) => {
          c.classList.toggle('step-on', pulse.v + 0.26 >= fracs[i]);
        });
      }
    });
  } else {
    fill.style.strokeDasharray = 'none';
    cells.forEach(c => c.classList.add('step-on'));
  }
})();
