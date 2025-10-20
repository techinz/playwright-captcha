# Playwright Captcha

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/playwright-captcha.svg)](https://pypi.org/project/playwright-captcha/)

A Python library that makes captcha solving simple and automated with Playwright and Playwright-based frameworks. Just a few lines of code, and you're ready to go!

<i>(Need some help with <b>Automation</b>? You can  <a href="https://automation.techinz.dev">hire me</a> for custom development or consulting!)</i>

## ✨ What it does

This framework helps you solve captchas in Playwright or Playwright-based frameworks (like Camoufox or Patchright) automatically. It will:

1. **Detect** the captcha on your page
2. **Solve** it using your preferred method 
3. **Apply** the solution automatically
4. **Submit** the form (when needed & possible)


---

<p align="center">
    <a href="https://www.nstproxy.com/?type=flow&utm_source=techinz" target="_blank">
        <img width="370" height="370" alt="Image" src="https://github.com/user-attachments/assets/1231e2c5-0b50-48d7-aafd-25a8bcebcae5" />
    </a>
</p>

<b>Nstproxy</b> delivers reliable, scalable, and cost-efficient proxies — <b>residential, datacenter, ISP, and IPv6</b> — with rotation, anti-block tech, and pricing from <b>$0.1/GB</b> for maximum uptime and ROI.  
👉 Learn more: <a href="https://www.nstproxy.com/?type=flow&utm_source=techinz">Nstproxy.com</a>: https://www.nstproxy.com/?type=flow&utm_source=techinz  | <a href="https://app.nstproxy.com/?utm_source=techinz">Dashboard</a>  
Telegram: https://t.me/nstproxy Discord: https://discord.gg/5jjWCAmvng   
Use code: <b>TECHINZ get 10% OFF</b>

---


## 📸 Demonstration (recorded in headless mode)

<div align="center">
  <h2>Click Solver</h2>
  <h4>Cloudflare Interstitial</h4>

  https://github.com/user-attachments/assets/06c244ff-ba82-4d8a-9ef8-17ece400716c
    
  <details> 
  <summary><h4>Cloudflare Turnstile</h4></summary>

  https://github.com/user-attachments/assets/52b49abd-5aa4-4262-9cb6-a555a95330c9

  </details>

  <h2>API Solver (Twocaptcha used here but others work similarly)</h2>

  <details> 
  <summary><h4>Cloudflare Interstitial</h4></summary>
    
  https://github.com/user-attachments/assets/25a6233b-43fb-4164-b41c-ea80100b501d

  </details>

  <details> 
  <summary><h4>Cloudflare Turnstile</h4></summary>
    
  https://github.com/user-attachments/assets/0f3f7999-1e0d-437e-9727-36a99a6c5abd

  </details>

  <details> 
  <summary><h4>ReCaptcha V2</h4></summary>
  
  https://github.com/user-attachments/assets/37b5d9b0-7c32-49b3-9c22-ffe0258161d1

  </details>

  <details> 
  <summary><h4>ReCaptcha V3</h4></summary>
  
  https://github.com/user-attachments/assets/7fc7d508-be87-4c60-aaf8-ab445601e69c

  </details>
</div>

## ⚠️ LEGAL DISCLAIMER

**THIS TOOL IS PROVIDED FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY**

This software is designed to demonstrate security concepts and should not be used to bypass protections on websites without explicit permission from the website owner. Using this tool against websites without authorization may violate:

- The Computer Fraud and Abuse Act (CFAA)
- Terms of Service agreements
- Various cybersecurity laws in your jurisdiction

## 🚀 Supported Captcha Types

### Click Solver
Uses the browser's stealthiness to automatically click and solve captchas (works good only with playwright's stealthy patches e.g. camoufox/patchright):
- ✅ Cloudflare Interstitial
- ✅ Cloudflare Turnstile

### API Solver

<details>
  <summary><h4>TwoCaptcha - https://2captcha.com</h4></summary>

 Uses the 2Captcha.com API for solving:
- ✅ Cloudflare Interstitial
- ✅ Cloudflare Turnstile
- ✅ reCAPTCHA v2
- ✅ reCAPTCHA v3

  </details>

<details>
  <summary><h4>TenCaptcha - https://10captcha.com</h4></summary>

 Uses the 10Captcha.com API for solving:
- ✅ reCAPTCHA v2
- ✅ reCAPTCHA v3

  </details>

<details>
  <summary><h4>CaptchaAI - https://captchaai.com</h4></summary>

 Uses the captchaai.com API for solving:
- ✅ reCAPTCHA v2
- ✅ reCAPTCHA v3

  </details>

*More captcha types and solvers coming soon! Contributions welcome.*

## 📦 Installation

```bash
pip install playwright-captcha
```

## 🔧 Quick Start

Check out the [examples](examples/) directory for detailed usage examples:

- **[Cloudflare Examples](examples/cloudflare/)**: Turnstile and Interstitial challenges
- **[reCAPTCHA Examples](examples/recaptcha/)**: v2 and v3 implementations

Each example includes configurations for Playwright, Patchright, and Camoufox.

### Click Solver Example

```python
import asyncio
from playwright.async_api import async_playwright
from playwright_captcha import CaptchaType, ClickSolver, FrameworkType

async def solve_captcha():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        framework = FrameworkType.PLAYWRIGHT
        
        # Create solver before navigating to the page
        async with ClickSolver(framework=framework, page=page) as solver:
            # Navigate to your target page
            await page.goto('https://example.com/with-captcha')
            
            # Solve the captcha
            await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE
            )
        
        # Continue with your automation...

asyncio.run(solve_captcha())
```

### API Solver Example (TwoCaptcha)

```python
import asyncio
import os
from playwright.async_api import async_playwright
from twocaptcha import AsyncTwoCaptcha
from playwright_captcha import CaptchaType, TwoCaptchaSolver, FrameworkType

async def solve_with_2captcha():
    # Initialize 2Captcha client
    captcha_client = AsyncTwoCaptcha(os.getenv('TWO_CAPTCHA_API_KEY'))
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
                
        framework = FrameworkType.PLAYWRIGHT
        
        # Create solver before navigating to the page
        # Available API Solvers:
        # TwoCaptchaSolver
        # TenCaptchaSolver
        # CaptchaAISolver
        
        async with TwoCaptchaSolver(framework=framework, 
                                    page=page, 
                                    async_two_captcha_client=captcha_client) as solver:
            # Navigate to your target page
            await page.goto('https://example.com/with-recaptcha')
        
            # Solve reCAPTCHA v2
            await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.RECAPTCHA_V2
            )
        
        # Continue with your automation...

asyncio.run(solve_with_2captcha())
```

## 🎯 How It Works

### Click Solver Process:
1. **Find** the captcha element on the page
2. **Click** on it using browser automation
3. **Wait** for successful completion

### External Solver Process (e.g., TwoCaptcha, TenCaptcha, CaptchaAI):
1. **Find** the captcha element
2. **Extract** required data (site key, URL, etc.)
3. **Send** to external solving service
4. **Apply** the returned solution
5. **Submit** the form (when applicable)

## 🗺️ TODO

### 🎯 Next Captcha Types
- [ ] **hCaptcha**

### 🔧 New Solver Types
- [ ] **CapSolver**
- [ ] **AI Solver**

### Other
- [ ] **Unit & Integration Tests**

## 🌐 Browser Compatibility

### Standard Playwright
Works with all standard Playwright browsers (Chrome, Firefox, Safari).

### Stealth Browsers
For better success rates, especially with click-based solving:

#### Patchright
```python
from patchright.async_api import async_playwright
from playwright_captcha import FrameworkType

async with async_playwright() as playwright:
    browser = await playwright.chromium.launch(channel="chrome", headless=False)
    
    framework = FrameworkType.PATCHRIGHT
    
    # ... rest of your code
```

#### Camoufox
```python
from camoufox import AsyncCamoufox
from playwright_captcha.utils.camoufox_add_init_script.add_init_script import get_addon_path
from playwright_captcha import FrameworkType
import os

ADDON_PATH = get_addon_path()

async with AsyncCamoufox(
    headless=False,
    geoip=True,
    humanize=True,
    main_world_eval=True, # add this
    addons=[os.path.abspath(ADDON_PATH)] # add this
) as browser:
    context = await browser.new_context()
    page = await context.new_page()
    
    framework = FrameworkType.CAMOUFOX
    
    # ... rest of your code
```

> **Note**: Camoufox currently has an issue with the `add_init_script` method. I've included a temporary workaround that's automatically used in the package. See the [examples](examples/) folder for details.

## 📁 Project Structure

```
playwright-captcha/
├── examples/                   # Usage examples
│   ├── cloudflare/             # Cloudflare captcha examples
│   └── recaptcha/              # reCAPTCHA examples
└── playwright_captcha/         # Main package
    ├── captchas/               # Captcha type implementations
    ├── solvers/                # Solver implementations
    ├── types/                  # Type definitions
    └── utils/                  # Utility functions
```

## 🔧 Configuration

### Environment Variables

(Optional) Create a `.env` file for your API keys:

```env
TWO_CAPTCHA_API_KEY=your_2captcha_api_key_here
TEN_CAPTCHA_API_KEY=your_10captcha_api_key_here
CAPTCHA_AI_API_KEY=your_captchaai_api_key_here
```

### Solver Options

```python
# Click solver with custom settings
solver = ClickSolver(
    framework=framework, # Framework type (PLAYWRIGHT, PATCHRIGHT, CAMOUFOX)
    page=page,
    max_attempts=5,      # Number of solving attempts
    attempt_delay=3      # Delay between attempts (seconds)
)

# API solver with custom settings (TwoCaptcha)
solver = TwoCaptchaSolver(
    framework=framework, # Framework type (PLAYWRIGHT, PATCHRIGHT, CAMOUFOX)
    page=page,
    async_two_captcha_client=captcha_client,
    max_attempts=3,
    attempt_delay=10,
    
    # also you can specify the captcha data like sitekey manually if it fails to detect automatically
    sitekey='sitekey'
    # ...
)
```

## 🆘 Support

- 📖 Check the [examples](examples/) folder for usage patterns
- 🐛 Report issues or request features on [GitHub Issues](https://github.com/techinz/playwright-captcha/issues)

