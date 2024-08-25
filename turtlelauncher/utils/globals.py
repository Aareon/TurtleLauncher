from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
ASSETS = ROOT_DIR.parent / "assets"
DATA = ASSETS / "data"
LOCALES = DATA / "locales"
IMAGES = ASSETS / "images"
FONTS = ASSETS / "fonts"

USER_DOCUMENTS = Path.home() / "Documents"
TOOL_FOLDER = USER_DOCUMENTS / "TurtleLauncher"
if not TOOL_FOLDER.exists():
    TOOL_FOLDER.mkdir(parents=True)

DOWNLOAD_URL = "https://turtle-eu.b-cdn.net/twmoa_1171.zip"