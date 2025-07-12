(token) => {
    let applied = false;

    // 1. set the value of the hidden input
    const input = document.querySelector('textarea[name="g-recaptcha-response"]');
    if (input) {
        input.value = token;
        input.dispatchEvent(new Event('change'));
        applied = true;
    }

    // 2. try to call callback if present
    const widget = document.querySelector('.g-recaptcha');
    if (widget && widget.hasAttribute('data-callback')) {
        const callbackName = widget.getAttribute('data-callback');
        if (callbackName && typeof window[callbackName] === 'function') {
            try {
                window[callbackName](token);
                applied = true;
            } catch (e) {
                console.error('Error calling reCAPTCHA callback:', e);
            }
        }
    }
    return applied;
}