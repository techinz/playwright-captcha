(token) => {
    let applied = false;

    for (const widget of document.querySelectorAll('.cutcaptcha')) {
        // the widget reads the token from this hidden input on a plain form post
        const input = widget.querySelector('input[name="cutcaptcha-response"]');
        if (!input) continue;

        input.value = token;
        input.dispatchEvent(new Event('change', {bubbles: true}));
        applied = true;

        const callbackName = widget.getAttribute('data-callback');
        if (callbackName && typeof window[callbackName] === 'function') {
            try {
                window[callbackName](token);
            } catch (e) {
                console.error('Error calling cutcaptcha callback:', e);
            }
        }
    }

    // single page apps read the token through the widget API instead of the input
    if (applied && window.cutcaptcha) {
        window.cutcaptcha.getResponse = () => token;
    }

    return applied;
}
