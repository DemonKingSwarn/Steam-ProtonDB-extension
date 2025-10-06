import Millennium
import PluginUtils  # type: ignore

import json
import os
import shutil
import requests

logger = PluginUtils.Logger()

WEBKIT_CSS_FILE = "protondb-webkit.css"

PROTONDB_API_URL = "https://www.protondb.com/api/v1/reports/summaries/"

DEFAULT_HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'Steam-ProtonDB-Millennium-Plugin'
}

def GetPluginDir():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))

def Request(url: str) -> str:
    response = None
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        return response.text
    except Exception as error:
        return json.dumps({
            'success': False,
            'error': str(error) + ' ' + (response.text if response else 'No response')
        })

def GetProtonDBSummary(appid: int) -> str:
    logger.log(f"Getting ProtonDB summary for {appid}")
    return Request(f"{PROTONDB_API_URL}{appid}.json")

class Plugin:
    def copy_webkit_files(self):
        webkitCssFilePath = os.path.join(GetPluginDir(), "public", WEBKIT_CSS_FILE)
        steamUIPath = os.path.join(Millennium.steam_path(), "steamui", "ProtonDB", WEBKIT_CSS_FILE)

        logger.log(f"Copying css webkit file from {webkitCssFilePath} to {steamUIPath}")
        try:
            os.makedirs(os.path.dirname(steamUIPath), exist_ok=True)
            shutil.copy(webkitCssFilePath, steamUIPath)
        except Exception as e:
            logger.error(f"Failed to copy webkit file, {e}")

        Millennium.add_browser_css(os.path.join("ProtonDB", WEBKIT_CSS_FILE))

    def _front_end_loaded(self):
        self.copy_webkit_files()

    def _load(self):
        logger.log(f"bootstrapping ProtonDB plugin, millennium {Millennium.version()}")
        self.copy_webkit_files()
        Millennium.ready()

    def _unload(self):
        logger.log("unloading")
