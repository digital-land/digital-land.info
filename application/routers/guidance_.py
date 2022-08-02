import os
import logging

from fastapi import APIRouter, Request

from application.core.templates import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{url_path:path}")
async def catch_all(request: Request, url_path: str):

    indexFile = "index.html"
    splitPath = url_path.split("/")

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

        # get the 'page name' for use in tracking current page in
        # navigation
        pageName = splitPath[-1].replace(".html", "")
        if len(splitPath) >= 2:
            if splitPath[-1] == "index" or splitPath[-1] == "":
                pageName = splitPath[-2]
        if pageName == "" or pageName == "index":
            pageName = "home"

        return templates.TemplateResponse(
            urlPathTofile,
            {"request": request, "pageData": {"url_path": url_path, "name": pageName}},
        )
    else:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )
