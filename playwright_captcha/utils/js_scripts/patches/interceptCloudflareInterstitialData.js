// script from https://2captcha.com/demo/cloudflare-turnstile-challenge

console.clear = () => console.log('Console was cleared');

function setupIntercept() {
  if (window.turnstile && !window._turnstileIntercepted) {
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

      if (interval) {
        clearInterval(interval);
      }

      console.log('blocking render for API solver');
      return;
    };
  }
}

const interval = setInterval(() => {
  setupIntercept()
}, 50);

setupIntercept();
