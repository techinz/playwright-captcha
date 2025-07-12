(() => {
  const originalAttachShadow = Element.prototype.attachShadow;
  Element.prototype.attachShadow = function (init) {
    const shadowRoot = originalAttachShadow.call(this, init);

    // expose shadowRoot for later use
    this.shadowRootUnl = shadowRoot;

    return shadowRoot;
  };
})();