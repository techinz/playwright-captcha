mw:(() => {{
    // "mw:" runs this in the main world, where the intercepted callback and page callbacks live
    let applied=false;

    // method 0: callback intercepted from turnstile.render() (API solvers block the render call)
    if (typeof window.cfCallback === 'function') {{
        try {{
            window.cfCallback("{token}");
            applied = true;
        }} catch (e) {{
            console.error('Error calling intercepted turnstile callback:', e);
        }}
    }}

    // method 1: try to find callback in data-callback attribute
    const container = document.querySelector('.cf-turnstile, [class*="turnstile"]');
    if (!applied && container && container.hasAttribute('data-callback')) {{
        const callbackName = container.getAttribute('data-callback');
        if (callbackName && window[callbackName] && typeof window[callbackName] === 'function') {{
            try {{
                window[callbackName]("{token}");
                applied= true;
            }} catch (e) {{
                console.error('Error calling turnstile callback:', e);
            }}
        }}
    }}

    // method 2: try global turnstile object
    if (window.turnstile && !applied) {{
        if (typeof window.turnstile.onSuccess === 'function') {{
            try {{
                window.turnstile.onSuccess("{token}");
                applied= true;
            }} catch (e) {{
                console.error('Error calling turnstile.onSuccess:', e);
            }}
        }}

        if (!applied){{
            // try to find widget ids and use explicit render
            try {{
                const widgets = document.querySelectorAll('.cf-turnstile, [class*="turnstile"]');
                for (const widget of widgets) {{
                    const widgetId = widget.getAttribute('data-widget-id') ||
                        widget.id ||
                        widget.getAttribute('data-sitekey');
                    if (widgetId) {{
                        console.log("Found turnstile widget:", widgetId);
                        // if reset exists, call it first
                        if (typeof window.turnstile.reset === 'function') {{
                            window.turnstile.execute(widget, "{token}");
                        }}
                        applied = true;
                    }}
                }}
            }} catch (e) {{
                console.error('Error with turnstile widget:', e);
            }}
        }}
    }}

    return applied;
}})()
