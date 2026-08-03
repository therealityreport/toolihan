// Known-good fixture behavior. Demonstrates adherence signals.

// ADHERENCE Postel's Law: forgiving, normalized input.
function normalizeEmail(v) {
  return v.trim().toLowerCase();
}
function isEmail(v) {
  // A sane, permissive check — not an over-strict regex.
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
}

const form = document.getElementById('signup');
const results = document.getElementById('results');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = normalizeEmail(form.email.value);
  if (!isEmail(email)) {
    // Inline, non-blocking feedback next to the field would go here.
    results.textContent = 'Please enter a valid email.';
    return;
  }

  // ADHERENCE Doherty Threshold: pending UI + optimistic feedback around the async call.
  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  results.textContent = 'Creating your account…'; // loading state
  try {
    const res = await fetch('/api/signup', { method: 'POST', body: JSON.stringify({ email }) });
    const data = await res.json();
    results.textContent = 'Welcome! Account ' + data.id + ' created.'; // ADHERENCE Peak-End: clear success state
  } catch {
    results.textContent = 'Something went wrong — your details are safe, please retry.';
  } finally {
    submitBtn.disabled = false;
  }
});
