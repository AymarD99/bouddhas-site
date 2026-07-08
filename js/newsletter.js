// Newsletter — stockage + envoi
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('newsletter-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('newsletter-email').value.trim();
    if (!email) return;

    // Stocker
    const subs = JSON.parse(localStorage.getItem('bouddhas_newsletter') || '[]');
    if (!subs.includes(email)) {
      subs.push(email);
      localStorage.setItem('bouddhas_newsletter', JSON.stringify(subs));
    }

    // Feedback
    form.innerHTML = `
      <div style="text-align:center;padding:1rem;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">✨</div>
        <p style="font-weight:600;color:var(--gold);">Merci ! Vous êtes inscrit(e) à notre newsletter.</p>
        <p style="color:rgba(255,255,255,0.5);font-size:0.9rem;">Vous recevrez nos offres exclusives et nouveautés.</p>
      </div>
    `;
  });

  // Popup différé
  const popup = document.getElementById('newsletter-popup');
  if (!popup) return;

  // Vérifier si déjà inscrit
  const subs = JSON.parse(localStorage.getItem('bouddhas_newsletter') || '[]');
  if (subs.length > 0) return;

  // Afficher après 10 secondes (une seule fois)
  const shown = sessionStorage.getItem('newsletter-shown');
  if (!shown) {
    setTimeout(() => {
      popup.classList.add('active');
      sessionStorage.setItem('newsletter-shown', 'true');
    }, 10000);
  }

  // Fermer
  document.querySelectorAll('.popup-close').forEach(btn => {
    btn.addEventListener('click', () => popup.classList.remove('active'));
  });
  popup.addEventListener('click', (e) => {
    if (e.target === popup) popup.classList.remove('active');
  });
});