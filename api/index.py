

import os
import sys
import urllib.parse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from DineFlow.wsgi import application as _django_app  # noqa: E402


def handler(environ, start_response):
 
    query_string = environ.get("QUERY_STRING", "")
    params = urllib.parse.parse_qs(query_string)

    if "path" in params and params["path"]:
        captured = params["path"][0]
        if not captured.startswith("/"):
            captured = f"/{captured}"
        environ["PATH_INFO"] = captured
        environ["SCRIPT_NAME"] = ""

    return _django_app(environ, start_response)



app = handler
application = handler