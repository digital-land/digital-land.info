import os
import logging
from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from application.core.templates import templates
from application.core.utils import get
from application.settings import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
file_extension = ".html"
settings = get_settings()

# This is a mapping of URL paths to CMS guidance pages.
cms_guidance_mapping = {
    "index": "/collections/guidance_pages/index",
    "publish-data-on-your-website": "/collections/guidance_pages/publish-data-on-your-website",
    "how-to-provide-data": "/collections/guidance_pages/how-to-provide-data",
    "open-digital-planning-community": "/collections/guidance_pages/open-digital-planning-community",
    "get-help": "/collections/guidance_pages/get-help",
    "specifications/index": "/collections/guidance_pages/specifications-index",
    "specifications/article-4-direction": "/collections/guidance_pages/specifications-article-4-direction",
    "specifications/conservation-area": "/collections/guidance_pages/specifications-conservation-area",
    "specifications/design-code": "/collections/guidance_pages/specifications-design-code",
    "specifications/listed-building": "/collections/guidance_pages/specifications-listed-building",
    "specifications/local-plan": "/collections/guidance_pages/specifications-local-plan",
    "specifications/tree-preservation-order": "/collections/guidance_pages/specifications-tree-preservation-order",
}

# get the 'page name' for use in tracking current page in
# navigation
def get_pagename(path):
    split_path = path.split("/")
    page_name = split_path[-1]
    if len(split_path) >= 2:
        if split_path[-1] == "index" or split_path[-1] == "":
            page_name = split_path[-2]
    if page_name == "" or page_name == "index" or page_name == f"index{file_extension}":
        page_name = "home"
    return page_name.replace(file_extension, "")


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

        if text == "index":
            if index == 1:
                text = split_path[-1]
                href = split_path[-1]
            if index >= 2:
                text = split_path[-2]
                href = split_path[i]

        # if it is not an index page
        if text != "index":
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
                    "text": text.replace(file_extension, "").replace("-", " "),
                    "href": href.replace(file_extension, ""),
                }
            )

    return crumb_dict


def handleGuidanceRedirects(url_path, redirects):
    for redirect in redirects:
        url_path_copy = url_path
        if len(url_path_copy) > 0 and url_path_copy[-1] == "/":
            url_path_copy = url_path_copy[:-1]
        if redirect["from"] == url_path_copy:
            return RedirectResponse(url=redirect["to"], status_code=301)
    return False

def get_cms_content_item(url_path):
    """
    This function retrieves the CMS content item path for a given URL path.
    It checks if the URL path exists in the cms_guidance_mapping dictionary.
    If it does, it returns the corresponding CMS content item path.
    """

    try:
        # Check if the URL path exists in the cms_guidance_mapping
        if url_path in cms_guidance_mapping:
            # Fetch the CMS content item from the CMS API
            return get(f"{settings.MINI_CMS_URL}/api/v1{cms_guidance_mapping[url_path]}").json()
        else:
            # If the URL path does not exist in the mapping, return None
            return None
    except Exception as e:
        logger.error(f"Error fetching CMS content item for {url_path} / {settings.MINI_CMS_URL}/api/v1{cms_guidance_mapping[url_path]}: {e}")
        return None


@router.get("/{url_path:path}")
async def catch_all(request: Request, url_path: str):
    index_file = "index"

    # Some redirects from old guidance

    # introduction
    shouldRedirect = handleGuidanceRedirects(
        url_path,
        [
            {"from": "introduction", "to": "/guidance"},
            {"from": "how-to-provide-data", "to": "/guidance"},
            {"from": "try-check-publish-service", "to": "/guidance"},
            {
                "from": "keep-your-data-up-to-date",
                "to": "/guidance/publish-data-on-your-website",
            },
        ],
    )

    if shouldRedirect:
        return shouldRedirect

    # if URL path in this route is empty
    if url_path == "":
        url_path += index_file
    # if URL path in this route ends with /
    elif url_path[-1] == "/":
        url_path += index_file

    # build string of the URL path and then the system path to the template file
    root_url_path = "pages/guidance/"
    url_path_to_file = root_url_path + url_path
    sys_path_to_file = f"application/templates/{url_path_to_file}{file_extension}"
    sys_path_directory = sys_path_to_file.replace(".html", "")

    # if the URL path is in the mapping, redirect to the CMS guidance page
    cms_content_item = get_cms_content_item(url_path) if url_path in cms_guidance_mapping else None

    if cms_content_item:
        return templates.TemplateResponse(
            f"/pages/guidance/cms-content-template.html",
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
                **cms_content_item["data"]
            },
        )


    # if matched path is to a directory assume looking for index file
    if os.path.isdir(sys_path_directory):
        if url_path_to_file[-1] != "/":
            url_path_to_file += f"/{index_file}"
            sys_path_to_file = sys_path_directory + f"/{index_file}.html"

    # if template file exists use it to render the page based
    # on the corresponding URL Path
    if os.path.exists(sys_path_to_file) and os.path.isfile(sys_path_to_file):
        return templates.TemplateResponse(
            f"{url_path_to_file}{file_extension}",  # path to the template file we wish to render
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
