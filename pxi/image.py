
import os
from os import PathLike
from PIL import Image
import requests
from requests.exceptions import ConnectionError
import sys
from typing import Dict, List, TypedDict
from urllib.parse import urlparse
from pxi.data import InventoryItemImageFile

from pxi.models import InventoryItem


# Maximum acceptable dimensions for web product images.
MAX_IMAGE_WIDTH = 1000
MAX_IMAGE_HEIGHT = 1000


# Known URL patterns, keyed by supplier code.
URL_TEMPLATES = {
    "ACO": "https://www.accobrands.com.au/pa_images/Detail/{item_code}.jpg",
    "BAN": "https://hamelinbrands.com.au/products/images/{item_code}.jpg",
    "CSS": "https://dc1240h7n7gpb.cloudfront.net/resources/static/main/image/{item_code_lowercase}.jpg",
    "DYN": "https://www.ds.net.au/assets/full/{item_code}.jpg",
    "ELA": "https://eliteagencies.com.au/wp-content/uploads/{item_code}.jpg",
    "JSH": "https://www.jshayes.com.au/productimages/{item_code}.jpg",
    "LEA": "https://www.leadersystems.com.au/Images/{item_code}.jpg",
    "GNS": "http://webconnect.groupnews.com.au/prodlarge/{item_code}.jpg",
    "RAS": "http://www.razorstat.com.au/images/{item_code}.jpg",
}


def fetch_images(dirpath: PathLike, inv_items: List[InventoryItem]):
    fetched_images: List[InventoryItemImageFile] = []

    # Make sure the images dir exists.
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

    # Try to fetch an image for each InventoryItem.
    for inv_item in inv_items:
        filename = f"{inv_item.code}.jpg"
        filepath = os.path.join(dirpath, filename)
        image = fetch_image(inv_item)
        if image:
            with open(filepath, "wb") as file:
                file.write(image)
            resize_image(filepath, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT)
            fetched_images.append(
                InventoryItemImageFile(inv_item, filename))

    return fetched_images


def fetch_image(inv_item: InventoryItem):
    urls = get_image_urls(inv_item)
    for url in urls:
        image = download_image(url)
        if image:
            return image
    return None


def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
    except ConnectionError:
        pass


def get_image_urls(inv_item: InventoryItem):
    urls: List[str] = []
    for supp_item in inv_item.supplier_items:
        supp_code = supp_item.code
        if supp_code in URL_TEMPLATES:
            urls.append(URL_TEMPLATES[supp_code].format(
                item_code=supp_item.item_code,
                item_code_lowercase=supp_item.item_code.lower()))
    return urls


def resize_image(filepath, target_width, target_height):
    # Open the image and get its dimensions.
    image = Image.open(filepath)
    orig_width, orig_height = image.size

    # Shrink the image to fit within the target bounds if it is too big.
    is_too_big = orig_width > target_width or orig_height > target_height
    if is_too_big:
        shrink_image_to_target(image, target_width, target_height)

    # Shrink the target box (while maintaining aspect ration) if the image
    # is smaller than the target box along both axes.
    is_too_small = orig_width < target_width and orig_height < target_height
    if is_too_small:
        target_width, target_height = shrink_target_to_image(
            image, target_width, target_height)

    # Resize a blank white image to the target size to create a white canvas.
    canvas_image = Image.open('pxi/blank.jpg')
    target_size = (target_width, target_height)
    canvas_image = canvas_image.resize(target_size)

    # Place the image in the centre of the blank canvas.
    width, height = image.size
    xPos = int((target_width - width) / 2)
    yPos = int((target_height - height) / 2)
    canvas_image.paste(image, (xPos, yPos))

    # Write the file as a JPEG.
    if canvas_image.mode == 'P':
        canvas_image = canvas_image.convert('RGB')
    canvas_image.save(filepath, 'JPEG')


def shrink_image_to_target(image, target_width, target_height):
    """
    Shrink image until it fits within the given target dimensions.
    """
    orig_width, orig_height = image.size
    orig_aspect_ratio = orig_width / orig_height
    target_aspect_ratio = target_width / target_height
    if orig_aspect_ratio >= target_aspect_ratio:
        # Resize image to target width.
        new_width = target_width
        new_height = int(target_width / orig_aspect_ratio)
    else:
        # Resize image to target height.
        new_width = int(target_height * orig_aspect_ratio)
        new_height = target_height


def shrink_target_to_image(image, target_width, target_height):
    """
    Shrink target dimension until they fit the image dimensions.
    """
    orig_width, orig_height = image.size
    orig_aspect_ratio = orig_width / orig_height
    target_aspect_ratio = target_width / target_height
    if orig_aspect_ratio >= target_aspect_ratio:
        # Resize target size to image width.
        target_width = orig_width
        target_height = int(orig_width / target_aspect_ratio)
    else:
        # Resize target size to image height.
        target_height = orig_height
        target_width = int(orig_height * target_aspect_ratio)
    return target_width, target_height
