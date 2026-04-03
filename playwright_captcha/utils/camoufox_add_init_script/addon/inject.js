if (window._shadowRootPatched !== true) {
  window._shadowRootPatched = true;
  
  const shadowRoots = new WeakMap();
  
  const originalAttachShadow = Element.prototype.attachShadow;
  Element.prototype.attachShadow = function (init) {
    const shadowRoot = originalAttachShadow.call(this, { ...init, mode: 'open' });
    shadowRoots.set(this, shadowRoot);
    return shadowRoot;
  };
  
  const descriptor = Object.getOwnPropertyDescriptor(Element.prototype, 'shadowRoot');
  if (descriptor && descriptor.get) {
    const originalGetter = descriptor.get;
    Object.defineProperty(Element.prototype, 'shadowRoot', {
      get: function() {
        return originalGetter.call(this) || shadowRoots.get(this);
      },
      configurable: true,
      enumerable: descriptor.enumerable
    });
  }
}

console.clear = () => console.log('Console was cleared');

// Intercept Cloudflare turnstile for data extraction
function setupIntercept() {
  if (window.turnstile && !window._turnstileIntercepted) {
    console.log('intercepting turnstile.render (Camoufox)');
    
    const originalRender = window.turnstile.render;
    window._turnstileIntercepted = true;
    
    window.turnstile.render = (a, b) => {
      let params = {
        sitekey: b.sitekey,
        pageurl: window.location.href,
        data: b.cData,
        pagedata: b.chlPageData,
        action: b.action,
        userAgent: navigator.userAgent,
        json: 1,
      };

      console.log('intercepted-params:' + JSON.stringify(params));
      window.cfCallback = b.callback;
      window.cfParams = params;

      if (cfInterval) {
        clearInterval(cfInterval);
      }

      // Check sessionStorage flag (shared between isolated and main worlds)
      // API solvers set this flag to prevent rendering (keeps token valid)
      // Click solvers don't set flag, allowing visual challenge to appear
      const shouldBlock = sessionStorage.getItem('_blockCloudflareRender') === 'true';
      
      if (shouldBlock) {
        console.log('blocking render for API solver');
        return;
      } else {
        console.log('allowing render for click solver');
        return originalRender.call(window.turnstile, a, b);
      }
    };
  }
}

const cfInterval = setInterval(() => {
  setupIntercept()
}, 50);

setupIntercept();