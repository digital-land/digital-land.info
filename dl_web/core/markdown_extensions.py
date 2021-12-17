from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from bs4 import BeautifulSoup


class GovUKStylesPostprocessor(Postprocessor):
    def __init__(self, md):
        super().__init__(md)

    def run(self, text):
        soup = BeautifulSoup(text, "html.parser")
        for p in soup.find_all("p"):
            p["class"] = "govuk-body"
        return str(soup)


class GovUKStylesExtension(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        gov_uk_post_processor = GovUKStylesPostprocessor(md)
        md.postprocessors.register(gov_uk_post_processor, "govukstyles", 200)
