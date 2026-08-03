// Known-bad fixture behavior. Planted violations are intentional.

// VIOLATION Postel's Law: over-strict email regex rejects valid addresses (plus-addressing,
// long TLDs) and there is no trim()/normalization of user input.
const STRICT_EMAIL = /^[a-z]+@[a-z]+\.(com|net|org)$/;

const form = document.getElementById('signup');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = form.email.value; // no .trim(), no .toLowerCase()
  if (!STRICT_EMAIL.test(email)) {
    alert('Invalid email'); // submit-only, blocking validation
    return;
  }

  // VIOLATION Doherty Threshold: async fetch with no loading/pending UI, no optimistic update.
  const res = await fetch('/api/signup', { method: 'POST', body: JSON.stringify({ email }) });
  const data = await res.json();
  document.getElementById('results').textContent = 'Done: ' + data.id;
});
