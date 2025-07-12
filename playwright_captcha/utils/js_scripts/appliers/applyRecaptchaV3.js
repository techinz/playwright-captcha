(token) => {
    const input = document.querySelector('textarea[name="g-recaptcha-response"]');
    if (input) {
        input.value = token;
        input.dispatchEvent(new Event('change'));
        return true;
    }
    return false;
}