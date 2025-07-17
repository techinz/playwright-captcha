import hashlib
import json
import os
from pathlib import Path

import aiofiles


def get_addon_path() -> str:
    """
    Get the absolute path to the addon's directory

    :return: Absolute path to the addon's directory
    """

    current_dir = Path(__file__).parent

    addon_path = current_dir / "addon"

    return str(addon_path.resolve())


async def add_init_script(js_script_string: str, addon_path: str = 'addon') -> str:
    """
    Save JavaScript code to addon's scripts directory with hash filename

    :param js_script_string: JavaScript code to be saved
    :param addon_path: Path to the addon's directory

    :return: The filename of the saved script
    """

    # create the scripts directory if it doesn't exist
    scripts_dir = os.path.join(addon_path, 'scripts')
    os.makedirs(scripts_dir, exist_ok=True)

    # generate hash for the script
    script_hash = hashlib.md5(js_script_string.encode('utf-8')).hexdigest()
    script_filename = f"script_{script_hash}.js"
    script_path = os.path.join(scripts_dir, script_filename)

    # write the script file
    async with aiofiles.open(script_path, 'w', encoding='utf-8') as f:
        await f.write(js_script_string)

    # update the scripts registry
    registry_path = os.path.join(scripts_dir, 'registry.json')
    registry = []

    if os.path.exists(registry_path):
        async with aiofiles.open(registry_path, 'r', encoding='utf-8') as f:
            registry = await f.read()
            registry = json.loads(registry) if registry else []

    # add script to registry if not already there
    if script_filename not in registry:
        registry.append(script_filename)

    # write updated registry
    async with aiofiles.open(registry_path, 'w', encoding='utf-8') as f:
        registry_json = json.dumps(registry, indent=2)
        await f.write(registry_json)

    return script_filename


def clean_scripts(addon_path: str = 'addon') -> None:
    """
    Clean the scripts directory by removing all script files and the registry.

    :param addon_path: Path to the addon's directory
    """

    scripts_dir = os.path.join(addon_path, 'scripts')
    if os.path.exists(scripts_dir):
        for filename in os.listdir(scripts_dir):
            file_path = os.path.join(scripts_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        registry_path = os.path.join(scripts_dir, 'registry.json')
        if os.path.exists(registry_path):
            os.remove(registry_path)


add_init_script.is_camoufox_workaround = True
