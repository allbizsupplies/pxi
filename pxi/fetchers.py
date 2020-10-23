from abc import ABC, abstractmethod
from requests import Session
import os
import shutil
import sys
from urllib.parse import urlparse


def get_fetcher(fetcher_classname):
    fetcher_class = getattr(sys.modules[__name__], fetcher_classname)
    fetcher = fetcher_class()
    return fetcher


def get_fetchers(inventory_item):
    fetchers = []
    for supplier_item in inventory_item.supplier_items:
        fetcher = get_fetcher(supplier_item.code)
        if fetcher:
            fetchers.append(fetcher)
    return fetchers


class BaseImageFetcher(ABC):

    def __init__(self, supplier_code):
        self.supplier_code = supplier_code
        self.session = Session()

    def get_supplier_item(self, inventory_item):
        for supplier_item in inventory_item.supplier_items:
            if supplier_item.code == self.supplier_code:
                return supplier_item

    def download_image(self, inventory_item, images_dir="data/images"):
        """Save image to file and return boolean value indicating success."""
        url = self.get_image_url(inventory_item)
        path = urlparse(url).path
        extension = path.split(".")[-1]
        filename = "{}.{}".format(inventory_item.code, extension)
        filepath = os.path.join(images_dir, filename)
        res = self.session.get(url)
        if res.status_code == 200:
            with open(filepath, "wb") as imgfile:
                imgfile.write(res.content)
            # Close requests session to avoid unclosed socket warning.
            self.session.close()
            return filepath

    @ abstractmethod
    def get_image_url(self, inventory_item):
        pass


class SimpleImageFetcher(BaseImageFetcher):
    """Fetches images using a known image URL pattern."""

    def __init__(self, supplier_code, template):
        super().__init__(supplier_code)
        self.template = template

    def get_image_url(self, inventory_item):
        supplier_item = self.get_supplier_item(inventory_item)
        if supplier_item is None:
            return
        url = self.template.format(
            item_code=supplier_item.item_code,
            item_code_lowercase=supplier_item.item_code.lower()
        )
        return url


class ACO(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "ACO",
            "https://www.accobrands.com.au/pa_images/Detail/{item_code}.jpg")


class CSS(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "CSS",
            "https://dc1240h7n7gpb.cloudfront.net/resources/static/main/image/{item_code_lowercase}.jpg")


class GNS(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "GNS",
            "http://webconnect.groupnews.com.au/prodlarge/{item_code}.jpg")


class SAT(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "SAT",
            "http://webconnect.groupnews.com.au/prodlarge/{item_code}.jpg")
