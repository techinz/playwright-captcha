// script from https://2captcha.com/demo/cloudflare-turnstile-challenge

console.clear = () => console.log('Console was cleared');

function setupIntercept() {
  if (window.turnstile) {
    console.log('intercepting turnstile.render');
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

      return;
    };
  }
}

const interval = setInterval(() => {
  setupIntercept()
}, 50);

setupIntercept();
