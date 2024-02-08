#!/bin/env python3

#=============================================================================
# Standard Library
#=============================================================================
from pathlib import Path

import auto_venv

__filename__ = str(Path(__file__).resolve())
__requires__ = [
    "beautifulsoup4==4.12.3",
    "requests==2.31.0",
    "pyyaml==6.0.1",
]

auto_venv.init(__filename__, __requires__, True, False)

import bs4       # noqa: E402
import requests  # noqa: E402
import yaml      # noqa: E402

print(f"bs4 version      : {bs4.__version__}")
print(f"requests version : {requests.__version__}")
print(f"yaml version     : {yaml.__version__}\n")

soup = bs4.BeautifulSoup(requests.get("https://pypi.org").content, "html.parser")
print(yaml.dump({"header": soup.find("h1").get_text()}))
