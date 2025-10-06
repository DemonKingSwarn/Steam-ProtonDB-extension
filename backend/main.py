import Millennium
import PluginUtils  # type: ignore

logger = PluginUtils.Logger()

import json
import os
import shutil
import requests

WEBKIT_CSS_FILE = "protondb-webkit.css"
CSS_ID = None
DEFAULT_HEADERS = {
    'Accept': 'application/json',
    'X-Requested-With': 'ProtonDB',
    'User-Agent': 'https://github.com/Trsnaqe/ProtonDB-Community-Extension',
    'Origin': 'https://github.com/Trsnaqe/ProtonDB-Community-Extension',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
}

API_URL = 'https://protondb-community-api-04f42bc1742f.herokuapp.com/api'

class Logger:
    @staticmethod
    def warn(message: str) -> None:
        logger.warn(message)

    @staticmethod
    def error(message: str) -> None:
        logger.error(message)

def GetPluginDir():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))

def Request(path: str, params: dict = None) -> str:
    url = f"{API_URL.rstrip('/')}/{path.lstrip('/')}"
    response = None
    try:
        response = requests.get(url, params=params or {}, headers=DEFAULT_HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as error:
        return json.dumps({
            'success': False,
            'error': str(error) + ' ' + (response.text if response is not None else 'No response')
        })

def GetGameSummary(appid: int, contentScriptQuery: str) -> str:
    logger.log(f"Getting ProtonDB summary for app {appid}")
    return Request(f"games/{int(appid)}/summary")

def GetGameReports(appid: int, contentScriptQuery: str, versioned: bool = False) -> str:
    logger.log(f"Getting ProtonDB reports for app {appid} (versioned={versioned})")
    res = Request(f"reports/{int(appid)}", {'versioned': 'true' if versioned else 'false'})
    try:
        parsed = json.loads(res)
        if isinstance(parsed, dict) and parsed.get('success') is False:
            return Request(f"games/{int(appid)}/reports", {'versioned': 'true' if versioned else 'false'})
    except Exception:
        pass
    return res

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

        global CSS_ID
        try:
            CSS_ID = Millennium.add_browser_css(os.path.join("ProtonDB", WEBKIT_CSS_FILE))
        except Exception as e:
            logger.error(f"Failed to register browser css: {e}")

    def _front_end_loaded(self):
        self.copy_webkit_files()

    def _load(self):
        logger.log(f"bootstrapping ProtonDB plugin, millennium {Millennium.version()}")
        self.copy_webkit_files()
        Millennium.ready()

    def _unload(self):
        logger.log("unloading ProtonDB plugin")
        try:
            if CSS_ID:
                Millennium.remove_browser_css(CSS_ID)
        except Exception:
            pass

