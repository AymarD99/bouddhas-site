// Annonce défilante + accordéon
document.addEventListener('DOMContentLoaded', () => {
  const slider = document.getElementById('announce-slider');
  if (!slider) return;
  const slides = slider.querySelectorAll('.swiper-slide');
  if (slides.length < 2) return;
  let current = 0;
  setInterval(() => {
    current = (current + 1) % slides.length;
    slider.style.transform = `translateX(-${current * 100}%)`;
  }, 4000);
});