(() => {
  if (window._shadowRootPatched) return;
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
})();