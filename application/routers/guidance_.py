import os
import logging
from fastapi import APIRouter, Request
from application.core.templates import templates

router = APIRouter()
logger = logging.getLogger(__name__)


# get the 'page name' for use in tracking current page in
# navigation
def get_pagename(path):
    splitPath = path.split("/")
    pageName = splitPath[-1]
    if len(splitPath) >= 2:
        if splitPath[-1] == "index.html" or splitPath[-1] == "":
            pageName = splitPath[-2]
    if pageName == "" or pageName == "index.html":
        pageName = "home"
    return pageName.replace(".html", "")


# using the url path construct a breadcrumb dictionary for use in the view
def get_breadcrumb(path):
    splitPath = path.split("/")
    splitPath.reverse()
    totalItems = len(splitPath)
    crumbDict = [{"href": "/guidance/", "text": "Guidance"}]
    # loop for the number of times there are items in the splitPath list
    for i in range(totalItems):

        # instantiate some variables
        index = i + 1
        text = splitPath[-index]
        href = splitPath[-index]

        if text == "index.html":
            if index == 1:
                text = splitPath[-1]
                href = splitPath[-1]
            if index >= 2:
                text = splitPath[-2]
                href = splitPath[i]

        # if it is not an index page
        if text != "index.html":
            if index == 1:
                if index < totalItems:
                    href = "../" + splitPath[-1] + "/"
                else:
                    href = splitPath[-1]
            if index >= 2:
                href = splitPath[-2]

            # finally add the link if it is not an index page
            crumbDict.append(
                {
                    "text": text.replace(".html", "").replace("-", " "),
                    "href": href,
                }
            )

    return crumbDict


@router.get("/{url_path:path}")
async def catch_all(request: Request, url_path: str):

    indexFile = "index.html"

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
            urlPathTofile,
            {
                "request": request,
                "pageData": {
                    "url_path": url_path,
                    "url_path_page": urlPathTofile,
                    "name": get_pagename(url_path),
                    "breadcrumb": get_breadcrumb(url_path),
                },
            },
        )
    else:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )
