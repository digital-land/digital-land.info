import os
import logging

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from application.core.templates import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{url_path:path}")
async def catch_all(request: Request, url_path: str):

    indexFile = "/index.html"

    # if URL path in this route is empty
    if url_path == "":
        url_path += indexFile
    # if URL path in this route ends with /
    elif url_path[-1] == "/":
        url_path += indexFile

    # build string of the URL path and then the system path to the template file
    urlPathTofile = "pages/guidance/" + url_path
    sysPathToFile = "application/templates/" + urlPathTofile

    # if matched path is to a directory assume looking for index file
    if os.path.isdir(sysPathToFile):
        urlPathTofile += indexFile
        sysPathToFile += indexFile

    # if template file exists use it to render the page based
    # on the corresponding URL Path
    if os.path.exists(sysPathToFile) and os.path.isfile(sysPathToFile):
        return templates.TemplateResponse(
            urlPathTofile, {"request": request, "awww": url_path}
        )
    else:
        return RedirectResponse(url="/404")
