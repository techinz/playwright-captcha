// load and execute all scripts from registry
async function loadScripts() {
  try {
    const registryResponse = await fetch(chrome.runtime.getURL('scripts/registry.json'));
    const registry = await registryResponse.json();

    for (const scriptFile of registry) {
      try {
        const scriptResponse = await fetch(chrome.runtime.getURL(`scripts/${scriptFile}`));
        const scriptContent = await scriptResponse.text();

        const script = document.createElement('script');
        script.textContent = scriptContent;
        document.documentElement.appendChild(script);
        script.remove();

        console.log(`Loaded script: ${scriptFile}`);
      } catch (error) {
        console.error(`Failed to load script ${scriptFile}:`, error);
      }
    }
  } catch (error) {
    console.error('Failed to load scripts registry:', error);
  }
}

// execute scripts
loadScripts();