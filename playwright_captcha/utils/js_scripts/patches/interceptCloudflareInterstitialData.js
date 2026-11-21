// script from https://2captcha.com/demo/cloudflare-turnstile-challenge

console.clear = () => console.log('Console was cleared');

// a blocked render leaves the container without the hidden response input the widget normally creates,
// add it so the token can be applied for forms reading it
function addResponseInput(container) {
  const element = typeof container === 'string' ? document.querySelector(container) : container;
  if (element && !element.querySelector('input[name="cf-turnstile-response"]')) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'cf-turnstile-response';
    element.appendChild(input);
  }
}

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
      addResponseInput(a);
      return;
    };
  }
}

const interval = setInterval(() => {
  setupIntercept()
}, 50);

setupIntercept();

// sites often call render() from the api.js script onload handler, before the next poll.
// a capturing load listener on document runs before the handler on the script element
document.addEventListener('load', () => setupIntercept(), true);
