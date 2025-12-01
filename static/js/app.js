document.addEventListener('DOMContentLoaded', () => {
  initCarousel();
  initMobileNav();
  initGameSelections();
  initRailControls();
});

/* -------------------- CAROUSEL -------------------- */
function initCarousel() {
  const carousel = document.querySelector('[data-carousel]');
  if (!carousel) return;

  const slides = carousel.querySelectorAll('[data-slide]');
  const buttons = carousel.querySelectorAll('[data-slide-nav]');
  let index = 0;

  const showSlide = (i) => {
    index = (i + slides.length) % slides.length;
    slides.forEach((slide, idx) => {
      slide.classList.toggle('opacity-100', idx === index);
      slide.classList.toggle('pointer-events-auto', idx === index);
      slide.classList.toggle('translate-x-0', idx === index);
      slide.classList.toggle('opacity-0', idx !== index);
      slide.classList.toggle('-translate-x-4', idx !== index);
    });
    buttons.forEach((btn, idx) => {
      btn.setAttribute('aria-current', idx === index);
    });
  };

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      showSlide(Number(btn.dataset.slideNav));
    });
  });

  let autoPlay = setInterval(() => showSlide(index + 1), 6000);
  carousel.addEventListener('mouseenter', () => clearInterval(autoPlay));
  carousel.addEventListener('mouseleave', () => {
    autoPlay = setInterval(() => showSlide(index + 1), 6000);
  });

  const prevBtn = carousel.querySelector('[data-carousel-prev]');
  const nextBtn = carousel.querySelector('[data-carousel-next]');
  if (prevBtn) prevBtn.addEventListener('click', () => showSlide(index - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => showSlide(index + 1));

  showSlide(0);
}

/* -------------------- MOBILE NAV -------------------- */
function initMobileNav() {
  const toggle = document.querySelector('[data-mobile-toggle]');
  const menu = document.querySelector('[data-mobile-menu]');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    menu.classList.toggle('hidden');
  });
}

/* -------------------- GAME SELECTION -------------------- */
function initGameSelections() {
  const compareForm = document.querySelector('[data-game-form]');
  if (!compareForm) return;

  const buttons = compareForm.querySelectorAll('[data-choice]');
  const feedback = compareForm.querySelector('[data-feedback]');

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      buttons.forEach((b) => b.classList.remove('ring-2', 'ring-brand-400', 'bg-brand-600/20'));
      btn.classList.add('ring-2', 'ring-brand-400', 'bg-brand-600/20');
      feedback.textContent = `You picked ${btn.dataset.choiceLabel}. Submit to confirm!`;
      feedback.classList.remove('hidden');
    });
  });
}

/* -------------------- RAIL CONTROLS -------------------- */
function initRailControls() {
  document.querySelectorAll('[data-rail-nav]').forEach((button) => {
    const direction = button.dataset.direction === 'next' ? 1 : -1;
    const target = button.dataset.railTarget;

    button.addEventListener('click', () => {
      const rail = document.querySelector(`[data-rail="${target}"]`);
      if (!rail) return;

      // Look for article elements (movie cards) or fall back to rail-card
      const card = rail.querySelector('article') || rail.querySelector('.rail-card');
      if (!card) return;

      // Calculate one card width + gap (1.5rem = 24px)
      const cardWidth = card.getBoundingClientRect().width;
      const gap = 24; // 1.5rem gap
      const scrollAmount = cardWidth + gap;

      rail.scrollBy({ left: direction * scrollAmount, behavior: 'smooth' });
    });
  });
}