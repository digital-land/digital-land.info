import os
import logging
from fastapi import APIRouter, Request
from application.core.templates import templates

router = APIRouter()
logger = logging.getLogger(__name__)


# get the 'page name' for use in tracking current page in
# navigation
def get_pagename(path):
    split_path = path.split("/")
    page_name = split_path[-1]
    if len(split_path) >= 2:
        if split_path[-1] == "index.html" or split_path[-1] == "":
            page_name = split_path[-2]
    if page_name == "" or page_name == "index.html":
        page_name = "home"
    return page_name.replace(".html", "")


# using the url path construct a breadcrumb dictionary for use in the view
def get_breadcrumbs(path):
    split_path = path.split("/")
    split_path.reverse()
    total_items = len(split_path)
    crumb_dict = [{"href": "/guidance/", "text": "Guidance"}]
    # loop for the number of times there are items in the split_path list
    for i in range(total_items):

        # instantiate some variables
        index = i + 1
        text = split_path[-index]
        href = split_path[-index]

        if text == "index.html":
            if index == 1:
                text = split_path[-1]
                href = split_path[-1]
            if index >= 2:
                text = split_path[-2]
                href = split_path[i]

        # if it is not an index page
        if text != "index.html":
            if index == 1:
                # if to a subsection index page
                # (because less that total items in list of split
                # url which has been reversed)
                if index < total_items:
                    href = f"../{split_path[-1]}/"
                else:
                    href = split_path[-1]
            if index >= 2:
                href = split_path[-2]

            # finally add the link if it is not an index page
            crumb_dict.append(
                {
                    "text": text.replace(".html", "").replace("-", " "),
                    "href": href,
                }
            )

    return crumb_dict


@router.get("/{url_path:path}")
async def catch_all(request: Request, url_path: str):

    index_file = "index.html"

    # if URL path in this route is empty
    if url_path == "":
        url_path += index_file
    # if URL path in this route ends with /
    elif url_path[-1] == "/":
        url_path += index_file

    # build string of the URL path and then the system path to the template file
    root_url_path = "pages/guidance/"
    url_path_to_file = root_url_path + url_path
    sys_path_to_file = f"application/templates/{url_path_to_file}"

    # if matched path is to a directory assume looking for index file
    if os.path.isdir(sys_path_to_file):
        url_path_to_file += index_file
        sys_path_to_file += index_file

    # if template file exists use it to render the page based
    # on the corresponding URL Path
    if os.path.exists(sys_path_to_file) and os.path.isfile(sys_path_to_file):

        return templates.TemplateResponse(
            url_path_to_file,  # path to the template file we wish to render
            {
                "request": request,
                # a dictionary of useful data used by the tempaltes and layouts
                "pageData": {
                    "root_url": root_url_path,
                    "url_path": url_path,
                    "url_path_page": url_path_to_file,
                    "name": get_pagename(url_path),
                    "breadcrumbs": get_breadcrumbs(url_path),
                },
            },
        )
    else:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )
