(() => {
  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const setHidden = (el, hidden) => {
    if (!el) return;
    el.hidden = hidden;
  };

  const lockScroll = (locked) => {
    document.documentElement.style.overflow = locked ? "hidden" : "";
  };



  const createFocusTrap = (container, onClose) => {
    const getFocusables = () =>
      qsa(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        container
      ).filter((el) => !el.hidden && el.offsetParent !== null);

    const onKeyDown = (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
        return;
      }

      if (e.key !== "Tab") return;

      const focusables = getFocusables();
      if (focusables.length === 0) return;

      const first = focusables[0];
      const last = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
        return;
      }

      if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    return { onKeyDown, getFocusables };
  };

  const initMenu = () => {
    const menuButton = qs(".menu-button");
    const menu = qs(".mobile-menu");
    const overlay = qs(".menu-overlay");
    const closeBtn = qs(".menu-close");

    if (!menuButton || !menu || !overlay || !closeBtn) return;

    let lastActive = null;
    const trap = createFocusTrap(menu, () => closeMenu());

    const openMenu = () => {
      lastActive = document.activeElement;
      setHidden(overlay, false);
      menu.classList.add('is-open');
      menuButton.setAttribute("aria-expanded", "true");
      lockScroll(true);
      menu.addEventListener("keydown", trap.onKeyDown);
      const focusables = trap.getFocusables();
      (focusables[0] || closeBtn).focus();
    };

    const closeMenu = () => {
      setHidden(overlay, true);
      menu.classList.remove('is-open');
      menuButton.setAttribute("aria-expanded", "false");
      lockScroll(false);
      menu.removeEventListener("keydown", trap.onKeyDown);
      if (lastActive && typeof lastActive.focus === "function") lastActive.focus();
    };

    menuButton.addEventListener("click", openMenu);
    closeBtn.addEventListener("click", closeMenu);
    overlay.addEventListener("click", closeMenu);

    qsa("a", menu).forEach((a) => a.addEventListener("click", closeMenu));
  };

  const initNavDropdown = () => {
    const dropdown = qs(".nav-dropdown");
    const toggle = qs(".nav-dropdown-toggle");
    if (!dropdown || !toggle) return;

    const links = qsa(".nav-dropdown-link", dropdown);

    const close = () => {
      dropdown.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    };

    toggle.addEventListener("click", (e) => {
      e.preventDefault();
      const next = !dropdown.classList.contains("is-open");
      dropdown.classList.toggle("is-open", next);
      toggle.setAttribute("aria-expanded", next ? "true" : "false");
      try {
        toggle.blur();
      } catch {}
    });

    links.forEach((a) =>
      a.addEventListener("click", () => {
        close();
      })
    );

    document.addEventListener("click", (e) => {
      if (!dropdown.contains(e.target)) close();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
  };

  const initHeader = () => {
    const header = qs(".site-header");
    if (!header) return;
    const onScroll = () => {
      const scrolled = window.scrollY > 8;
      header.classList.toggle("is-scrolled", scrolled);
      header.classList.add("is-visible");
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  };

  const initScrollProgress = () => {
    const rail = qs(".scroll-rail");
    const fill = qs(".scroll-rail-fill");
    if (!fill) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let ticking = false;
    let dragging = false;
    let dragPointerId = null;

    const set = () => {
      ticking = false;
      const doc = document.documentElement;
      const max = Math.max(1, doc.scrollHeight - window.innerHeight);
      const p = Math.min(1, Math.max(0, window.scrollY / max));
      const v = reduceMotion ? p : p;
      doc.style.setProperty("--scroll-progress", String(v));
      if (rail) rail.setAttribute("aria-valuenow", String(Math.round(v * 100)));
    };

    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(set);
      window.setTimeout(() => {
        if (!ticking) return;
        set();
      }, 80);
    };

    const jumpTo = (clientY) => {
      if (!rail) return;
      const rect = rail.getBoundingClientRect();
      const trackTop = rect.top + 8;
      const trackHeight = Math.max(1, rect.height - 16);
      const p = Math.min(1, Math.max(0, (clientY - trackTop) / trackHeight));
      const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      window.scrollTo({ top: p * max, behavior: reduceMotion ? "auto" : "auto" });
    };

    if (rail) {
      rail.addEventListener("pointerdown", (e) => {
        e.preventDefault();
        dragging = true;
        dragPointerId = e.pointerId;
        rail.setPointerCapture(e.pointerId);
        jumpTo(e.clientY);
      });

      rail.addEventListener("pointermove", (e) => {
        if (!dragging || e.pointerId !== dragPointerId) return;
        jumpTo(e.clientY);
      });

      const endDrag = (e) => {
        if (!dragging || e.pointerId !== dragPointerId) return;
        dragging = false;
        dragPointerId = null;
        try {
          rail.releasePointerCapture(e.pointerId);
        } catch {}
      };

      rail.addEventListener("pointerup", endDrag);
      rail.addEventListener("pointercancel", endDrag);

      rail.addEventListener("keydown", (e) => {
        const step = e.key === "PageDown" || e.key === "PageUp" ? 0.2 : 0.08;
        if (e.key !== "ArrowDown" && e.key !== "ArrowUp" && e.key !== "PageDown" && e.key !== "PageUp")
          return;
        e.preventDefault();
        const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        const cur = window.scrollY / max;
        const dir = e.key === "ArrowDown" || e.key === "PageDown" ? 1 : -1;
        const next = Math.min(1, Math.max(0, cur + dir * step));
        window.scrollTo({ top: next * max, behavior: "auto" });
      });
    }

    set();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", set);
  };

  const initReveal = () => {
    // Reveal animations are disabled for faster initial load.
  };

  const initScrollSpy = () => {
    const navLinks = [
      ...qsa(".nav-shell .nav-link"),
      ...qsa(".nav-shell .nav-dropdown-link"),
      ...qsa(".mobile-nav .mobile-nav-link")
    ];
    if (navLinks.length === 0) return;

    const nextBtn = qs(".fab-next");
    const topBtn = qs(".fab-top");
    const scrollRail = qs(".scroll-rail");

    const linksById = new Map();
    navLinks.forEach((a) => {
      const href = a.getAttribute("href") || "";
      if (!href.startsWith("#")) return;
      const id = href.slice(1);
      if (!id) return;
      const list = linksById.get(id) || [];
      list.push(a);
      linksById.set(id, list);
    });

    const hero = qs(".hero");
    const ordered = [];
    if (hero) ordered.push({ id: "main", el: hero });
    qsa("main > section[id]").forEach((el) => ordered.push({ id: el.id, el }));
    qsa("footer[id]").forEach((el) => ordered.push({ id: el.id, el }));

    if (ordered.length === 0) return;

    const navIdsOrdered = ordered.map((x) => x.id).filter((id) => linksById.has(id));
    let activeSectionId = null;

    const setScrollTarget = (id) => {
      if (!nextBtn || ordered.length === 0) return;

      const idx = ordered.findIndex((x) => x.id === id);
      const currentIdx = idx >= 0 ? idx : 0;
      const next = ordered[(currentIdx + 1) % ordered.length];
      const prev = ordered[(currentIdx - 1 + ordered.length) % ordered.length];

      nextBtn.removeAttribute("href");
      nextBtn.setAttribute(
        "aria-label",
        "Scroll to next section"
      );
      nextBtn.dataset.direction = "down";
      nextBtn.dataset.targetId = next.id;

      if (topBtn) {
        topBtn.removeAttribute("href");
        topBtn.setAttribute(
          "aria-label",
          "Scroll to previous section"
        );
        topBtn.dataset.direction = "up";
        topBtn.dataset.targetId = prev.id;
      }
    };

    const setNavActive = (id) => {
      linksById.forEach((links, key) => {
        const isActive = key === id;
        links.forEach((a) => a.classList.toggle("is-active", isActive));
      });
    };

    const setActiveSection = (id) => {
      if (activeSectionId === id) return;
      activeSectionId = id;
      setScrollTarget(id);

      const variant = id === "main" || id === "hero" ? "dark" : "light";
      if (nextBtn) nextBtn.dataset.variant = variant;
      if (topBtn) topBtn.dataset.variant = variant === "dark" ? "dark" : "light";
      if (scrollRail) scrollRail.dataset.variant = variant;

      if (topBtn) {
        topBtn.hidden = id === "main" || id === "hero";
      }

      const idx = ordered.findIndex((x) => x.id === id);
      if (idx < 0) return;

      let navId = navIdsOrdered[0] || null;
      for (const candidate of navIdsOrdered) {
        const cIdx = ordered.findIndex((x) => x.id === candidate);
        if (cIdx <= idx) navId = candidate;
      }
      if (navId) setNavActive(navId);
    };

    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible.length === 0) return;
        const id = visible[0].target.getAttribute("data-spy-id");
        if (id) setActiveSection(id);
      },
      { rootMargin: "-45% 0px -45% 0px", threshold: [0.01, 0.2, 0.35, 0.6] }
    );

    ordered.forEach(({ id, el }) => {
      el.setAttribute("data-spy-id", id);
      io.observe(el);
    });

    // Add click event listeners for scroll buttons
    if (nextBtn) {
      nextBtn.addEventListener("click", (e) => {
        e.preventDefault();
        const targetId = nextBtn.dataset.targetId;
        if (targetId) {
          const targetEl = qs(`#${targetId}`);
          if (targetEl) {
            targetEl.scrollIntoView({ behavior: "smooth" });
          }
        }
      });
    }

    if (topBtn) {
      topBtn.addEventListener("click", (e) => {
        e.preventDefault();
        const targetId = topBtn.dataset.targetId;
        if (targetId) {
          const targetEl = qs(`#${targetId}`);
          if (targetEl) {
            targetEl.scrollIntoView({ behavior: "smooth" });
          }
        }
      });
    }

    setActiveSection("main");
  };

  const initCountUp = () => {
    const items = qsa("[data-count]");
    if (items.length === 0) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const getData = (el) => {
      const value = el.getAttribute("data-count");
      const suffix = el.getAttribute("data-suffix") || "";
      
      // If data-suffix is provided, use it
      if (suffix) {
        const n = Number(value);
        if (!Number.isFinite(n)) return null;
        return { n, suffix };
      }
      
      // Otherwise, extract numeric value and suffix from the string
      const match = value.match(/^([\d.]+)(.*)$/);
      if (!match) return null;
      const n = Number(match[1]);
      if (!Number.isFinite(n)) return null;
      const autoSuffix = match[2] || "";
      return { n, suffix: autoSuffix };
    };

    items.forEach((el) => {
      const d = getData(el);
      if (!d) return;
      el.textContent = `0${d.suffix}`;
    });

    const animate = (el) => {
      if (el.dataset.counted === "1") return;
      const d = getData(el);
      if (!d) return;
      el.dataset.counted = "1";

      if (reduceMotion) {
        el.textContent = `${d.n}${d.suffix}`;
        return;
      }

      const start = performance.now();
      const duration = 900;
      const tick = (now) => {
        const p = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - p, 3);
        const current = d.n * eased;
        // decide decimals: use 1 decimal for 'B' suffix or fractional targets < 10
        const useOneDecimal = d.suffix === "B" || (!Number.isInteger(d.n) && d.n < 10);
        let display;
        if (useOneDecimal) {
          display = current.toFixed(1);
          if (display.endsWith('.0')) display = display.slice(0, -2);
        } else {
          display = String(Math.round(current));
        }
        el.textContent = `${display}${d.suffix}`;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          animate(e.target);
        });
      },
      { threshold: 0.55 }
    );

    items.forEach((el) => io.observe(el));
  };

  const initHeroSlider = () => {
    const hero = qs("[data-hero-slider]");
    if (!hero) return;

    const slides = qsa(".hero-slide", hero);
    const dots = qsa("[data-hero-dot]", hero);
    const connectors = qsa(".hero-connector", hero);
    if (
      slides.length < 2 ||
      dots.length < 1 ||
      connectors.length !== Math.max(0, dots.length - 1)
    )
      return;

    const titleEl = qs("[data-hero-title]", hero);
    const leadEl = qs("[data-hero-lead]", hero);
    const kickerEl = qs("[data-hero-kicker]", hero);
    const ctaPrimary = qs("[data-hero-cta-primary]", hero);
    const ctaSecondary = qs("[data-hero-cta-secondary]", hero);
    const ctaPrimaryLabel = qs("[data-hero-cta-primary-label]", hero);
    const ctaSecondaryLabel = qs("[data-hero-cta-secondary-label]", hero);
    const contentEl = qs(".hero-content", hero);

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let idx = 1;
    let contentIdx = 1;
    let timer = null;
    const slideDurations = [10000, 10000];
    const contentDuration = 5000;
    const getSlideDuration = (i) => slideDurations[i % slideDurations.length] || 5000;

    const decodeHtmlEntities = (text) => {
      if (!text) return "";
      let decoded = text.replace(/&bull;/g, "·").replace(/&mdash;/g, "–").replace(/&ndash;/g, "-");

      return decoded;
    };

    const slideContent = window.HERO_SLIDES_DATA || [
      {
        kicker: "OPRELL Interiors — Dubai, UAE",
        title: "Space is never just space.",
        lead: "Interior design, fit-out, villa renovation and landscape — designed and built in-house across the UAE.",
        primaryLabel: "See our work",
        primaryHref: "#projects",
        secondaryLabel: "Start a project",
        secondaryHref: "contact/"
      }
    ];
    const getSlideContent = (i) => slideContent[i] || slideContent[0];
    let contentTimer = null;

    const restartProgress = () => {
      if (reduceMotion) return;
      hero.style.setProperty("--hero-interval", `${contentDuration}ms`);
      connectors.forEach((el) => el.classList.remove("is-progressing"));
      if (connectors[contentIdx]) {
        void connectors[contentIdx].offsetHeight;
        connectors[contentIdx].classList.add("is-progressing");
      }
    };

    const applyContent = (c) => {
      if (kickerEl) kickerEl.textContent = decodeHtmlEntities(c.kicker || "");
      if (titleEl) {
        const decodedTitle = decodeHtmlEntities(c.title);
        titleEl.textContent = decodedTitle;
      }
      if (leadEl) leadEl.textContent = decodeHtmlEntities(c.lead);
      if (ctaPrimary) ctaPrimary.setAttribute("href", c.primaryHref);
      if (ctaPrimaryLabel) ctaPrimaryLabel.textContent = decodeHtmlEntities(c.primaryLabel);
      if (ctaSecondary) ctaSecondary.setAttribute("href", c.secondaryHref);
      if (ctaSecondaryLabel) ctaSecondaryLabel.textContent = decodeHtmlEntities(c.secondaryLabel);
      
      // Add/remove arrows based on link type
      const isInternalPage = (href) => href && href.startsWith('/') && !href.startsWith('/#');
      
      // Primary button arrow
      let primaryArrow = ctaPrimary?.querySelector('.icon');
      if (isInternalPage(c.primaryHref)) {
        if (!primaryArrow) {
          primaryArrow = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
          primaryArrow.classList.add('icon', 'icon-18');
          primaryArrow.setAttribute('viewBox', '0 0 24 24');
          primaryArrow.setAttribute('aria-hidden', 'true');
          primaryArrow.innerHTML = '<path d="M19 5a1 1 0 0 1 1 1v9a1 1 0 1 1-2 0V8.4l-9.3 9.3a1 1 0 0 1-1.4-1.4L16.6 7H10a1 1 0 1 1 0-2h9Z"/>';
          ctaPrimary.appendChild(primaryArrow);
        }
      } else {
        if (primaryArrow) primaryArrow.remove();
      }
      
      // Secondary button arrow
      let secondaryArrow = ctaSecondary?.querySelector('.icon');
      if (isInternalPage(c.secondaryHref)) {
        if (!secondaryArrow) {
          secondaryArrow = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
          secondaryArrow.classList.add('icon', 'icon-18');
          secondaryArrow.setAttribute('viewBox', '0 0 24 24');
          secondaryArrow.setAttribute('aria-hidden', 'true');
          secondaryArrow.innerHTML = '<path d="M19 5a1 1 0 0 1 1 1v9a1 1 0 1 1-2 0V8.4l-9.3 9.3a1 1 0 0 1-1.4-1.4L16.6 7H10a1 1 0 1 1 0-2h9Z"/>';
          ctaSecondary.appendChild(secondaryArrow);
        }
      } else {
        if (secondaryArrow) secondaryArrow.remove();
      }
    };

    const swapContent = (c) => {
      if (!contentEl || reduceMotion) {
        applyContent(c);
        return;
      }

      if (contentTimer) window.clearTimeout(contentTimer);
      contentEl.classList.add("is-switching");

      contentTimer = window.setTimeout(() => {
        applyContent(c);
        contentEl.classList.remove("is-switching");
      }, 170);
    };

    const setActive = (nextIdx) => {
      idx = (nextIdx + slides.length) % slides.length;
      slides.forEach((s, i) => s.classList.toggle("is-active", i === idx));
      restartProgress();
    };

    const setActiveContent = (nextContentIdx) => {
      contentIdx = (nextContentIdx + slideContent.length) % slideContent.length;
      const c = getSlideContent(contentIdx);
      swapContent(c);
      
      dots.forEach((d, i) => {
        const active = i === contentIdx;
        d.classList.toggle("is-active", active);
        d.setAttribute("aria-selected", active ? "true" : "false");
      });
    };

    const cycleContent = () => {
      // Increment to next slide and loop back to 0 if at end
      contentIdx = (contentIdx + 1) % slideContent.length;
      
      const c = getSlideContent(contentIdx);
      swapContent(c);
      
      dots.forEach((d, i) => {
        const active = i === contentIdx;
        d.classList.toggle("is-active", active);
        d.setAttribute("aria-selected", active ? "true" : "false");
      });
      
      restartProgress();
    };

    const stop = () => {
      if (timer) window.clearTimeout(timer);
      if (contentTimer) window.clearTimeout(contentTimer);
      timer = null;
      contentTimer = null;
      hero.classList.add("is-paused");
    };

    const start = () => {
      if (reduceMotion) return;
      stop(); // Ensure all timers are cleared before starting
      hero.classList.remove("is-paused");
      restartProgress();
      
      // Start content cycling timer (5 seconds) - independent
      startContentCycling();
      
      // Start video cycling timer (5 seconds) - independent
      startVideoCycling();
    };
    
    const startContentCycling = () => {
      contentTimer = window.setTimeout(() => {
        cycleContent();
        startContentCycling(); // Recursive call
      }, contentDuration);
    };
    
    const startVideoCycling = () => {
      if (timer) window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        setActive(idx + 1);
        startVideoCycling();
      }, getSlideDuration(idx));
    };
    
    // Initialize with first video
    setActive(idx);

    dots.forEach((btn) => {
      btn.addEventListener("click", () => {
        const n = Number(btn.getAttribute("data-hero-dot"));
        if (Number.isFinite(n)) {
          // Only stop content timer, not video timer
          if (contentTimer) window.clearTimeout(contentTimer);
          contentTimer = null;
          
          contentIdx = n;
          const c = getSlideContent(contentIdx);
          
          // Apply content immediately
          applyContent(c);
          
          // Then trigger transition effect
          if (contentEl && !reduceMotion) {
            contentEl.classList.remove("is-switching");
            void contentEl.offsetHeight; // Trigger reflow
            contentEl.classList.add("is-switching");
            setTimeout(() => {
              contentEl.classList.remove("is-switching");
            }, 170);
          }
          
          dots.forEach((d, i) => {
            const active = i === contentIdx;
            d.classList.toggle("is-active", active);
            d.setAttribute("aria-selected", active ? "true" : "false");
          });
          
          restartProgress();
          
          // Always restart content timer for continuous looping
          startContentCycling();
        }
      });
    });

    hero.addEventListener("focusin", stop);
    hero.addEventListener("focusout", (e) => {
      if (!hero.contains(e.relatedTarget)) start();
    });

    hero.addEventListener("keydown", (e) => {
      if (e.key === "ArrowUp" || e.key === "ArrowLeft") {
        e.preventDefault();
        stop();
        setActive(idx - 1);
        start();
        return;
      }
      if (e.key === "ArrowDown" || e.key === "ArrowRight") {
        e.preventDefault();
        stop();
        setActive(idx + 1);
        start();
      }
    });

    setActive(0);
    contentIdx = 0;
    
    // Apply content to ensure arrows are set correctly on initial load
    const initialContent = getSlideContent(contentIdx);
    applyContent(initialContent);
    
    dots.forEach((d, i) => {
      const active = i === 0;
      d.classList.toggle("is-active", active);
      d.setAttribute("aria-selected", active ? "true" : "false");
    });
    
    restartProgress();
    start();
  };

  const initFeaturedProjectsSlider = () => {
    const slider = qs("[data-featured-slider]");
    if (!slider) return;

    const track = qs(".featured-projects-track", slider);
    const prevBtn = qs(".featured-projects-prev", slider.parentElement);
    const nextBtn = qs(".featured-projects-next", slider.parentElement);
    const cards = qsa(".project-card", slider);

    if (!track || cards.length < 2) return;

    let currentSlide = 0;
    let touchStartX = 0;
    let touchEndX = 0;

    const getCardsPerView = () => {
      const width = window.innerWidth;
      if (width <= 768) return 1;
      return 3;
    };

    const updateSlider = () => {
      const cardsPerView = getCardsPerView();
      const maxSlide = Math.max(0, cards.length - cardsPerView);
      const cardWidth = cards[0].offsetWidth + 18; // card width + gap
      const translateX = -(currentSlide * cardWidth);
      track.style.transform = `translateX(${translateX}px)`;

      // Update buttons if they exist
      if (prevBtn) prevBtn.disabled = currentSlide === 0;
      if (nextBtn) nextBtn.disabled = currentSlide >= maxSlide;
    };

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (currentSlide > 0) {
          currentSlide--;
          updateSlider();
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        const cardsPerView = getCardsPerView();
        const maxSlide = Math.max(0, cards.length - cardsPerView);
        if (currentSlide < maxSlide) {
          currentSlide++;
          updateSlider();
        }
      });
    }

    // Recalculate on resize
    window.addEventListener("resize", updateSlider);

    // Initialize
    updateSlider();
  };

  const initUaeMap = () => {
    const obj = qs("#uae-svg");
    if (!obj) return;

    const dropdown = qs("#map-dropdown");
    const dropdownTitle = qs("#map-dropdown-title");
    const dropdownMeta = qs("#map-dropdown-meta");
    const dropdownBody = qs("#map-dropdown-body");
    const dropdownFooter = qs("#map-dropdown-footer");
    const dropdownClose = qs("#map-dropdown-close");
    const regionIdsByCity = {
      "dubai": "AE-DU",
      "abu-dhabi": "AE-AZ",
      "al-ain": "AE-AZ",
      "ras-al-khaimah": "AE-RK",
      "ajman": "AE-AJ",
      "fujairah": "AE-FU"
    };

    const openDropdown = ({ title, meta, body, type, id, slug, page, moreUrl }) => {
      if (!dropdown || !dropdownTitle || !dropdownMeta || !dropdownBody) return;
      dropdownTitle.innerHTML = title || "";
      dropdownMeta.textContent = meta || "";
      dropdownBody.textContent = body || "";

      // Set class based on type for styling
      dropdown.classList.remove("is-project", "is-default");
      if (type === "project") {
        dropdown.classList.add("is-project");
      } else if (type === "default") {
        dropdown.classList.add("is-default");
      }

      if (dropdownFooter) {
        dropdownFooter.innerHTML = "";
        let href;
        if (type === "project") {
          const pageParam = page && page > 1 ? `?page=${page}` : "";
          href = `projects/${pageParam}#project-${slug || id}`;
        } else {
          href = moreUrl || "#services";
        }
        const label = type === "project" ? "View project" : "More";
        if (href) {
          const button = document.createElement("a");
          button.className = "map-dropdown-action";
          button.href = href;
          button.target = "_self";
          button.rel = "";
          button.innerHTML = `${label}`;
          dropdownFooter.appendChild(button);
        }
      }

      dropdown.classList.add("is-open");
    };

    const officeCards = qsa(".presence-card[data-location-id]");

    const closeDropdown = () => {
      if (!dropdown) return;
      dropdown.classList.remove("is-open");
      // Remove active state from all cards
      officeCards.forEach((c) => {
        c.classList.remove("is-primary");
      });
      // Remove active state from all map pins
      const doc = obj.contentDocument;
      if (doc) {
        qsa(".uae-pin.is-active", doc).forEach((pin) => pin.classList.remove("is-active"));
      }
    };

    if (dropdownClose) dropdownClose.addEventListener("click", closeDropdown);

    const setActiveLocation = (locationId) => {
      if (!locationId) return;
      officeCards.forEach((c) => {
        c.classList.toggle("is-primary", c.getAttribute("data-location-id") === String(locationId));
      });
    };

    const onSvgReady = async () => {
      const doc = obj.contentDocument;
      if (!doc) return;
      const svg = doc.querySelector("svg");
      if (!svg) return;
      
      const widthAttr = parseFloat(svg.getAttribute("width") || "760.1441");
      const heightAttr = parseFloat(svg.getAttribute("height") || "612.53363");
      const pad = 18;
      svg.setAttribute("viewBox", `${-pad} ${-pad} ${widthAttr + pad * 2} ${heightAttr + pad * 2}`);
      svg.removeAttribute("width");
      svg.removeAttribute("height");
      svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
      svg.classList.add("uae-svg");

      const geoRaw = svg.getAttribute("mapsvg:geoViewBox") || svg.getAttribute("geoViewBox");
      const geo = (() => {
        if (!geoRaw) return null;
        const parts = geoRaw.trim().split(/\s+/).map((n) => Number(n));
        if (parts.length !== 4 || parts.some((n) => Number.isNaN(n))) return null;
        const [west, north, east, south] = parts;
        if (east === west || north === south) return null;
        return { west, north, east, south };
      })();

      const geoToSvg = (lon, lat) => {
        if (!geo) return null;
        const x = ((lon - geo.west) / (geo.east - geo.west)) * widthAttr;
        const y = ((geo.north - lat) / (geo.north - geo.south)) * heightAttr;
        if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
        return { x: Math.min(Math.max(x, 0), widthAttr), y: Math.min(Math.max(y, 0), heightAttr) };
      };

      const style = doc.createElementNS("http://www.w3.org/2000/svg", "style");
      style.textContent = `
        .uae-svg { width: 100%; height: 100%; }
        .uae-region { fill: rgba(0, 0, 0, 0.12); stroke: rgba(0, 0, 0, 0.45); stroke-width: 1.2; vector-effect: non-scaling-stroke; transition: fill 180ms ease; }
        .uae-region:hover { fill: rgba(184, 150, 62, 0.14); }
        .uae-region.is-selected { fill: rgba(0, 0, 0, 0.2); }
        #OM-MU, #AE-NZ1, #AE-NZ2 { display: none; }
        .uae-pin { transform-origin: center; transition: transform 180ms ease, filter 180ms ease; cursor: pointer; }
        .uae-pin:focus, .uae-pin:focus-visible { outline: none; }
        .uae-pin .ring { fill: rgba(184, 150, 62, 0.16); transform-origin: center; opacity: 0; }
        .uae-pin.is-primary .ring { opacity: 0.55; }
        .uae-pin.is-active .ring { opacity: 0.7; }
        .uae-pin .dot { fill: #000; stroke: #fff; stroke-width: 2; }
        .uae-pin.is-primary .dot, .uae-pin.is-active .dot { fill: #b8963e; }
        .uae-pin.is-active, .uae-pin:focus-visible { filter: drop-shadow(0 10px 18px rgba(0, 0, 0, 0.22)); transform: scale(1.06); }
        .uae-pin.is-project .ring { fill: rgba(184, 150, 62, 0.12); opacity: 0.6; }
        .uae-pin.is-project .diamond { fill: rgba(255, 255, 255, 0.95); stroke: #b8963e; stroke-width: 2.4; }
        .uae-pin.is-project.is-active .diamond, .uae-pin.is-project:focus-visible .diamond { fill: #b8963e; stroke: #ffffff; }
      `;
      svg.prepend(style);

      const regions = qsa('path[id^="AE-"]', doc).filter(
        (p) => !["AE-NZ1", "AE-NZ2"].includes(p.id)
      );
      regions.forEach((p) => p.classList.add("uae-region"));

      const selectRegion = (regionId) => {
        if (!regionId) return;
        regions.forEach((r) => r.classList.toggle("is-selected", r.id === regionId));
      };

      const locationPins = {};

      const locations = window.MAP_LOCATIONS_DATA || [];

      try {
        if (Array.isArray(locations) && locations.length) {
          const locationLayer = doc.createElementNS("http://www.w3.org/2000/svg", "g");
          locationLayer.setAttribute("id", "uae-location-layer");
          
          locations.forEach((loc) => {
            // Skip office locations, only show project locations on the map
            if (loc.type !== "project") return;
            
            const ns = "http://www.w3.org/2000/svg";
            const g = doc.createElementNS(ns, "g");
            g.classList.add("uae-pin");
            if (loc.isPrimary) g.classList.add("is-primary");
            if (loc.type === "project") g.classList.add("is-project");
            g.setAttribute("tabindex", "0");
            g.setAttribute("role", "button");
            g.setAttribute("data-location-id", loc.id || "");
            g.setAttribute("data-city", loc.city.toLowerCase().replace(/ /g, '-'));
            g.setAttribute("aria-label", loc.title || "Location");

            const x = loc.x;
            const y = loc.y;

            const ring = doc.createElementNS(ns, "circle");
            ring.setAttribute("class", "ring");
            ring.setAttribute("cx", String(x));
            ring.setAttribute("cy", String(y));
            ring.setAttribute("r", loc.type === "project" ? "16" : "12");

            let shape;
            if (loc.type === "project") {
              shape = doc.createElementNS(ns, "rect");
              shape.setAttribute("class", "diamond");
              shape.setAttribute("x", String(x - 6));
              shape.setAttribute("y", String(y - 6));
              shape.setAttribute("width", "12");
              shape.setAttribute("height", "12");
              shape.setAttribute("rx", "3");
              shape.setAttribute("ry", "3");
              shape.setAttribute("transform", `rotate(45 ${x} ${y})`);
            } else {
              shape = doc.createElementNS(ns, "circle");
              shape.setAttribute("class", "dot");
              shape.setAttribute("cx", String(x));
              shape.setAttribute("cy", String(y));
              shape.setAttribute("r", "6");
            }

            g.appendChild(ring);
            g.appendChild(shape);

            const activate = () => {
              qsa(".uae-pin.is-active", doc).forEach((pin) => pin.classList.remove("is-active"));
              g.classList.add("is-active");
              // Move active pin to end of location layer for higher z-index
              locationLayer.appendChild(g);
              openDropdown({
                title: loc.title || "",
                meta: loc.city || (loc.type === "office" ? "Office" : ""),
                body: loc.description || "",
                type: loc.type,
                id: loc.id,
                slug: loc.slug || loc.id,
                page: loc.page || 1,
                moreUrl: loc.moreUrl || "",
              });

              const regionId = loc.region || (loc.city ? regionIdsByCity[loc.city.toLowerCase().replace(/ /g, "-")] : null);
              selectRegion(regionId);

              if (loc.type === "office") {
                setActiveLocation(loc.id);
              }
            };

            g.addEventListener("click", activate);
            g.addEventListener("keydown", (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                activate();
              }
            });

            locationLayer.appendChild(g);

            locationPins[String(loc.id)] = g;
          });
          svg.appendChild(locationLayer);

          window.locationPins = locationPins;
        }
      } catch {
      }

      // Show default project summary card when no pin is active
      const projectCount = window.MAP_PROJECTS_TOTAL || 70;
      openDropdown({
        title: `${projectCount}+ Projects`,
        meta: "",
        body: "Click on any project pin on the map to view details, or browse our full portfolio below.",
        type: "default",
        moreUrl: "/projects/",
      });
      
      // Trigger count-up animation for the project count
      const animateCount = () => {
        const countEl = dropdownTitle;
        if (countEl) {
          const d = { n: window.MAP_PROJECTS_TOTAL || 70, suffix: '+' };
          const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
          
          if (reduceMotion) {
            countEl.textContent = `${d.n}${d.suffix} Projects`;
            return;
          }
          
          const start = performance.now();
          const duration = 2000;
          const tick = (now) => {
            const p = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - p, 3);
            const current = d.n * eased;
            const display = String(Math.round(current));
            countEl.textContent = `${display}${d.suffix} Projects`;
            if (p < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      };
      
      // Run animation on page load and visibility change
      setTimeout(animateCount, 100);
      document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
          dropdownTitle.textContent = `0+ Projects`;
          setTimeout(animateCount, 100);
        }
      });
      window.addEventListener('load', () => {
        dropdownTitle.textContent = `0+ Projects`;
        setTimeout(animateCount, 100);
      });

      officeCards.forEach((card) => {
        card.setAttribute("tabindex", "0");
        card.setAttribute("role", "button");
        const locationId = card.getAttribute("data-location-id");
        const activate = () => {
          const pin = locationId ? locationPins[locationId] : null;
          if (pin) {
            qsa(".uae-pin.is-active", doc).forEach((p) => p.classList.remove("is-active"));
            pin.classList.add("is-active");
          }
          setActiveLocation(locationId);

          const title = card.querySelector(".presence-card-title, .h3")?.textContent?.trim() || "";
          const meta = card.querySelector(".presence-tag")?.textContent?.trim() || "Office";
          const body = card.querySelector("p")?.textContent?.trim() || "";
          openDropdown({
            title,
            meta,
            body,
            type: "office",
            id: locationId,
            slug: locationId,
            moreUrl: card.getAttribute("data-more-url") || "",
          });

          selectRegion(card.getAttribute("data-region"));
        };

        card.addEventListener("click", activate);
        card.addEventListener("keydown", (e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            activate();
          }
        });
      });
    };

    if (obj.contentDocument?.readyState === "complete") onSvgReady();
    obj.addEventListener("load", onSvgReady);
  };

  const initFeaturedProjects = async () => {
    // Disabled - projects now rendered from database
    return;
  };

  const initTestimonials = async () => {
    const quoteEl = qs("#testimonial-quote");
    const nameEl = qs("#testimonial-name");
    const roleTitleEl = qs("#testimonial-role-title");
    const roleCompanyEl = qs("#testimonial-role-company");
    const progressEl = qs("#testimonial-progress");
    const testimonialsEl = qs(".testimonials");
    const cardEl = qs("#testimonial-card");
    const prevBtn = qs('[data-testimonial="prev"]');
    const nextBtn = qs('[data-testimonial="next"]');

    if (!quoteEl || !roleTitleEl || !roleCompanyEl || !prevBtn || !nextBtn) return;

    let idx = 0;
    let data = null;
    let timer = null;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const intervalMs = 6500;
    if (cardEl) cardEl.style.setProperty("--testimonial-interval", `${intervalMs}ms`);

    const restartProgress = () => {
      if (!progressEl || reduceMotion) return;
      progressEl.classList.remove("is-progressing");
      void progressEl.offsetHeight;
      progressEl.classList.add("is-progressing");
    };

    const render = () => {
      if (!data || data.length === 0) return;
      const t = data[idx];
      quoteEl.textContent = `“${t.quote}”`;
      if (nameEl) {
        nameEl.textContent = "";
        nameEl.hidden = true;
      }
      // Split role into title and company
      const roleParts = (t.role || "").split("\n");
      roleTitleEl.textContent = roleParts[0] || "";
      roleCompanyEl.textContent = roleParts[1] || "";
      restartProgress();
    };

    const move = (dir) => {
      if (!data || data.length === 0) return;
      idx = (idx + dir + data.length) % data.length;
      render();
    };

    const stop = () => {
      if (timer) window.clearInterval(timer);
      timer = null;
      if (testimonialsEl) testimonialsEl.classList.add("is-paused");
    };

    const start = () => {
      if (reduceMotion || !data || data.length < 2) return;
      stop();
      if (testimonialsEl) testimonialsEl.classList.remove("is-paused");
      restartProgress();
      timer = window.setInterval(() => move(1), intervalMs);
    };

    prevBtn.addEventListener("click", () => {
      stop();
      move(-1);
      start();
    });

    nextBtn.addEventListener("click", () => {
      stop();
      move(1);
      start();
    });

    if (cardEl) {
      cardEl.addEventListener("mouseenter", stop);
      cardEl.addEventListener("mouseleave", start);
      cardEl.addEventListener("focusin", stop);
      cardEl.addEventListener("focusout", (e) => {
        if (!cardEl.contains(e.relatedTarget)) start();
      });
    }

    try {
      if (window.TESTIMONIALS_DATA) {
        data = window.TESTIMONIALS_DATA;
      } else {
        const dataUrl = window.TESTIMONIALS_DATA_URL || "data/testimonials.json";
        const res = await fetch(dataUrl, { cache: "no-store" });
        if (!res.ok) return;
        const json = await res.json();
        if (!Array.isArray(json) || json.length === 0) return;
        data = json;
      }
      if (data && data.length > 0) {
        render();
        start();
      }
    } catch {
      return;
    }
  };

  const initYear = () => {
    const year = qs("#year");
    if (year) year.textContent = String(new Date().getFullYear());
  };

  const initMobileNavToggle = () => {
    const toggles = qsa(".mobile-nav-toggle");
    toggles.forEach((toggle) => {
      toggle.addEventListener("click", () => {
        const isExpanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!isExpanded));
      });
    });
  };

  const initCleanHashOnLoad = () => {
    if (!window.location.hash || !window.history.replaceState) return;
    window.addEventListener("load", () => {
      const cleanUrl = window.location.pathname + window.location.search;
      window.history.replaceState(null, document.title, cleanUrl);
    });
  };

  const initProjectSearch = () => {
    const searchInput = qs("#search-filter");
    const categoryFilter = qs("#category-filter");
    const companyFilter = qs("#company-filter");
    const statusFilter = qs("#status-filter");
    const cityFilter = qs("#city-filter");
    const resetBtn = qs("#reset-filters");
    const projectsList = qs("#projects-list");
    const projectsCount = qs("#projects-count");

    if (!searchInput || !projectsList) return;

    const filterProjects = () => {
      const searchTerm = searchInput.value.toLowerCase().trim();
      const category = categoryFilter ? categoryFilter.value : "";
      const company = companyFilter ? companyFilter.value : "";
      const status = statusFilter ? statusFilter.value : "";
      const city = cityFilter ? cityFilter.value : "";

      const projectRows = qsa(".project-row", projectsList);
      let visibleCount = 0;

      projectRows.forEach(row => {
        const title = row.querySelector(".project-row-title")?.textContent.toLowerCase() || "";
        const summary = row.querySelector(".project-row-summary")?.textContent.toLowerCase() || "";
        const rowCategory = row.dataset.category || "";
        const rowStatus = row.dataset.status || "";
        const rowCity = row.dataset.city || "";
        const rowCompany = row.dataset.company || "";

        const matchesSearch = !searchTerm || title.includes(searchTerm) || summary.includes(searchTerm);
        const matchesCategory = !category || rowCategory === category;
        const matchesCompany = !company || rowCompany === company;
        const matchesStatus = !status || rowStatus === status;
        const matchesCity = !city || rowCity === city;

        const isVisible = matchesSearch && matchesCategory && matchesCompany && matchesStatus && matchesCity;
        row.hidden = !isVisible;

        if (isVisible) visibleCount++;
      });

      if (projectsCount) {
        projectsCount.textContent = visibleCount;
      }
    };

    searchInput.addEventListener("input", filterProjects);

    if (categoryFilter) categoryFilter.addEventListener("change", filterProjects);
    if (companyFilter) companyFilter.addEventListener("change", filterProjects);
    if (statusFilter) statusFilter.addEventListener("change", filterProjects);
    if (cityFilter) cityFilter.addEventListener("change", filterProjects);

    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        searchInput.value = "";
        if (categoryFilter) categoryFilter.value = "";
        if (companyFilter) companyFilter.value = "";
        if (statusFilter) statusFilter.value = "";
        if (cityFilter) cityFilter.value = "";
        filterProjects();
      });
    }
  };

  const initRowLightbox = () => {
    const lb = qs("#lb");
    if (!lb) return;
    const lbImg = qs("#lb-img", lb);
    const lbCount = qs("#lb-count", lb);
    const lbClose = qs("#lb-close", lb);
    if (!lbImg || !lbCount || !lbClose) return;

    let photos = [];
    let li = 0;
    let isOpen = false;
    let lastFocus = null;

    const show = (i) => {
      if (!photos.length) return;
      li = (i + photos.length) % photos.length;
      lbImg.src = photos[li];
      lbCount.textContent = (li + 1) + " / " + photos.length;
    };

    const openLb = (list, i, full) => {
      photos = list;
      if (!photos.length) return;
      lastFocus = document.activeElement;
      show(i);
      lb.classList.add("open");
      lb.removeAttribute("inert");
      lockScroll(true);
      isOpen = true;
      lbClose.focus();
      if (full && lb.requestFullscreen) lb.requestFullscreen().catch(() => {});
    };

    const closeLb = () => {
      lb.classList.remove("open");
      lb.setAttribute("inert", "");
      lockScroll(false);
      isOpen = false;
      if (document.fullscreenElement) document.exitFullscreen();
      if (lastFocus) lastFocus.focus();
    };

    qsa(".project-row-media[data-photos]").forEach(media => {
      let list = [];
      try { list = JSON.parse(media.dataset.photos || "[]"); } catch (e) { list = []; }
      if (!list.length) return;
      media.addEventListener("click", e => {
        if (e.target.closest(".pma-btn")) return;
        openLb(list, 0, false);
      });
      media.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openLb(list, 0, false); }
      });
      const gBtn = qs("[data-open-gallery]", media);
      const fBtn = qs("[data-open-full]", media);
      if (gBtn) gBtn.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); openLb(list, 0, false); });
      if (fBtn) fBtn.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); openLb(list, 0, true); });
    });

    lbClose.addEventListener("click", closeLb);
    const lbPrev = qs("#lb-prev", lb);
    const lbNext = qs("#lb-next", lb);
    if (lbPrev) lbPrev.addEventListener("click", e => { e.stopPropagation(); show(li - 1); });
    if (lbNext) lbNext.addEventListener("click", e => { e.stopPropagation(); show(li + 1); });
    lb.addEventListener("click", e => { if (e.target === lb) closeLb(); });
    window.addEventListener("keydown", e => {
      if (!isOpen) return;
      if (e.key === "Escape") closeLb();
      if (e.key === "ArrowLeft") show(li - 1);
      if (e.key === "ArrowRight") show(li + 1);
    });
    let tx = 0;
    lb.addEventListener("touchstart", e => { tx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", e => {
      const dx = e.changedTouches[0].clientX - tx;
      if (Math.abs(dx) > 50) show(li + (dx < 0 ? 1 : -1));
    }, { passive: true });
  };

  const initNavActive = () => {
    let path = location.pathname.replace(/\/index\.html$/, "").replace(/\/+$/, "");
    if (path === "") path = "/";
    qsa(".nav-link[href], .mobile-nav-link[href]").forEach(a => {
      let href = (a.getAttribute("href") || "").replace(/^\.\.\//, "").replace(/^\.\//, "");
      href = "/" + href.replace(/\/+$/, "");
      if (href === "/") href = "/";
      const isHome = ["./", "../", "#top", "index.html"].includes(a.getAttribute("href")) || /index\.html$/.test(a.getAttribute("href") || "");
      if ((isHome && path === "/") || (!isHome && href === path)) {
        a.classList.add("is-active");
        a.setAttribute("aria-current", "page");
      }
    });
    if (path === "/services") {
      qsa(".nav-dropdown-toggle").forEach(b => b.classList.add("is-active"));
    }
  };

  const initApp = () => {
    initYear();
    initHeader();
    initNavDropdown();
    initMenu();
    initScrollProgress();
    initScrollSpy();
    initHeroSlider();
    initReveal();
    initUaeMap();
    initFeaturedProjectsSlider();
    initTestimonials();
    initCountUp();
    initMobileNavToggle();
    initProjectSearch();
    initRowLightbox();
    initNavActive();

  };

  const onPageReady = () => {
    document.documentElement.classList.add("page-ready");
    
    // Hide page loader quickly for fast loading
    const pageLoader = document.getElementById("page-loader");
    if (pageLoader) {
      pageLoader.classList.add("is-hidden");
      setTimeout(() => {
        pageLoader.style.display = "none";
      }, 300);
    }
    
    initApp();
  };

  if (document.readyState !== "loading") {
    onPageReady();
  } else {
    window.addEventListener("DOMContentLoaded", onPageReady);
  }
})();
