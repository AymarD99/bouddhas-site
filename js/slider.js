// Slider Hero — carousel automatique (FIX: méthodes renommées correctement)
class HeroSlider {
  constructor(container) {
    this.container = container;
    this.slides = container.querySelectorAll('.hero-slide');
    this.current = 0;
    this.interval = null;
    this.total = this.slides.length;
    if (this.total < 2) return;
    this.init();
  }

  init() {
    // Dots
    const dots = document.createElement('div');
    dots.className = 'slider-dots';
    for (let i = 0; i < this.total; i++) {
      const dot = document.createElement('span');
      dot.className = 'slider-dot' + (i === 0 ? ' active' : '');
      dot.onclick = () => this.goTo(i);
      dots.appendChild(dot);
    }
    this.container.appendChild(dots);

    // Flèches
    const prev = document.createElement('button');
    prev.className = 'slider-arrow slider-prev';
    prev.innerHTML = '‹';
    prev.onclick = () => this.prevSlide();
    
    const next = document.createElement('button');
    next.className = 'slider-arrow slider-next';
    next.innerHTML = '›';
    next.onclick = () => this.nextSlide();

    this.container.appendChild(prev);
    this.container.appendChild(next);

    this.goTo(0);
    this.startAutoPlay();
    
    this.container.addEventListener('mouseenter', () => this.stopAutoPlay());
    this.container.addEventListener('mouseleave', () => this.startAutoPlay());
  }

  goTo(index) {
    this.current = index;
    this.slides.forEach((s, i) => {
      s.classList.toggle('active', i === index);
      s.style.transform = `translateX(${(i - index) * 100}%)`;
    });
    const dots = this.container.querySelectorAll('.slider-dot');
    dots.forEach((d, i) => d.classList.toggle('active', i === index));
  }

  nextSlide() { this.goTo((this.current + 1) % this.total); }
  prevSlide() { this.goTo((this.current - 1 + this.total) % this.total); }
  startAutoPlay() { if (!this.interval) this.interval = setInterval(() => this.nextSlide(), 5000); }
  stopAutoPlay() { clearInterval(this.interval); this.interval = null; }
}

document.addEventListener('DOMContentLoaded', () => {
  const slider = document.querySelector('.hero.carousel');
  if (slider) new HeroSlider(slider);
});