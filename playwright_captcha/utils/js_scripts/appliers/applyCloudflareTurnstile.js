(token) => {
    let applied = false;

    const turnstileInput = document.querySelector('input[name="cf-turnstile-response"]');
    if (turnstileInput) {
        turnstileInput.value = token;
        turnstileInput.dispatchEvent(new Event('change'));
        applied = true;
    }

    return applied;
}