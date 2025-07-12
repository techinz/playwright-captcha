let applied = false;

const turnstileInput = document.querySelector('input[name="cf-turnstile-response"]');
if (turnstileInput) {{
    mw:turnstileInput.value = "{token}";
    mw:turnstileInput.dispatchEvent(new Event('change'));
    applied = true;
}}
