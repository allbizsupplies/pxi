from abc import ABC, abstractmethod
from requests.exceptions import ConnectionError
from requests import Session
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import sys
from urllib.parse import urlparse


def get_fetcher(fetcher_classname):
    try:
        fetcher_class = getattr(sys.modules[__name__], fetcher_classname)
        fetcher = fetcher_class()
        return fetcher
    except AttributeError:
        pass


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
        if not os.path.exists(images_dir):
            os.mkdir(images_dir)
        url = self.get_image_url(inventory_item)
        path = urlparse(url).path
        extension = path.split(".")[-1]
        filename = "{}.{}".format(inventory_item.code, extension)
        filepath = os.path.join(images_dir, filename)
        try:
            res = self.session.get(url)
            if res.status_code == 200:
                with open(filepath, "wb") as imgfile:
                    imgfile.write(res.content)
                # Close requests session to avoid unclosed socket warning.
                self.session.close()
                return filepath
        except ConnectionError:
            pass

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


class BrowserImageFetcher(BaseImageFetcher):
    """Fetches images using a web browser to collect URLs."""

    def __init__(self, supplier_code):
        super().__init__(supplier_code)

    def get_webdriver(self):
        profile_path = os.path.join("chromedriver", "profile")
        options = Options()
        options.add_argument('user-data-dir={}'.format(profile_path))
        options.headless = True
        return webdriver.Chrome(
            options=options,
            service_log_path="/dev/null")


class ACO(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "ACO",
            "https://www.accobrands.com.au/pa_images/Detail/{item_code}.jpg")


class BAN(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "BAN",
            "https://hamelinbrands.com.au/products/images/{item_code}.jpg")


class CSS(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "CSS",
            "https://dc1240h7n7gpb.cloudfront.net/resources/static/main/image/{item_code_lowercase}.jpg")


class ELA(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "ELA",
            "https://eliteagencies.com.au/wp-content/uploads/{item_code}.jpg")


class JSH(SimpleImageFetcher):

    def __init__(self):
        super().__init__(
            "JSH",
            "https://www.jshayes.com.au/productimages/{item_code}.jpg")


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


class AVD(BrowserImageFetcher):

    def __init__(self):
        super().__init__("AVD")

    def get_image_url(self, inventory_item):
        supplier_item = self.get_supplier_item(inventory_item)
        driver = self.get_webdriver()
        search_url = "https://www.averyproducts.com.au/search?term={item_code}&content_group=product".format(
            item_code=supplier_item.item_code)
        driver.get(search_url)
        url = None
        page_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1"))
        )
        if "Search results" in page_title.text:
            # Get image url from search result with matching SKU.
            results = driver.find_elements_by_class_name("content-search__result-item")
            for result in results:
                sku_wrapper_element = result.find_element_by_class_name("field-prod-sku-num")
                sku = sku_wrapper_element.text
                if sku == supplier_item.item_code:
                    image_wrapper_element = result.find_element_by_class_name("field-image-file")
                    image_element = image_wrapper_element.find_element_by_tag_name("img")
                    url = image_element.get_attribute("src")
        driver.close()
        return url
