
from random import randint
from requests.exceptions import ConnectionError
from unittest.mock import MagicMock, mock_open, patch
from pxi import image

from pxi.image import (
    CANVAS_IMAGE_FILEPATH,
    MAX_IMAGE_HEIGHT,
    MAX_IMAGE_WIDTH,
    URL_TEMPLATES,
    convert_image_to_rgb,
    download_image,
    fetch_image,
    fetch_images,
    format_image,
    get_image_urls,
    place_image_centred_on_canvas,
    shrink_image_to_target,
    shrink_target_to_image)
from tests import DatabaseTestCase
from tests.fakes import (
    fake_image,
    fake_inventory_item,
    fake_supplier_item,
    random_string)


class ImageFetchingTests(DatabaseTestCase):

    def test_get_image_urls(self):
        inv_item = fake_inventory_item()
        supp_items = []
        for supp_code in URL_TEMPLATES:
            supp_items.append(fake_supplier_item(inv_item, {
                "code": supp_code,
            }))
        inv_item.supplier_items = supp_items

        urls = get_image_urls(inv_item)

        for supp_item in inv_item.supplier_items:
            self.assertIn(
                URL_TEMPLATES[supp_item.code].format(
                    item_code=supp_item.item_code,
                    item_code_lowercase=supp_item.item_code.lower()),
                urls)

    def test_get_image_urls_ignores_missing_supp_item_code(self):
        inv_item = fake_inventory_item()
        supp_items = []
        for supp_code in URL_TEMPLATES:
            supp_items.append(
                fake_supplier_item(inv_item, {
                    "code": supp_code,
                    "item_code": None,
                }))
        inv_item.supplier_items = supp_items

        urls = get_image_urls(inv_item)

        self.assertEqual(len(urls), 0)

    @patch("requests.get")
    def test_get_image_data_from_url(self, mock_get):
        url = random_string(20)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        content = download_image(url)

        mock_get.assert_called_with(url)
        self.assertEqual(content, mock_response.content)

    @patch("requests.get")
    def test_return_no_image_when_response_404(self, mock_get):
        url = random_string(20)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        content = download_image(url)

        mock_get.assert_called_with(url)
        self.assertEqual(content, None)

    @patch("requests.get")
    def test_return_no_image_when_conn_error(self, mock_get):
        url = random_string(20)
        mock_get.side_effect = ConnectionError()

        content = download_image(url)

        mock_get.assert_called_with(url)
        self.assertEqual(content, None)

    @patch("pxi.image.download_image")
    @patch("pxi.image.get_image_urls")
    def test_fetch_image(self, mock_get_image_urls, mock_download_image):
        inv_item = fake_inventory_item()
        url = random_string(20)
        mock_get_image_urls.return_value = [url]

        result = fetch_image(inv_item)

        mock_get_image_urls.assert_called_with(inv_item)
        mock_download_image.assert_called_with(url)
        self.assertEqual(result, mock_download_image.return_value)

    @patch("pxi.image.format_image")
    @patch("pxi.image.fetch_image")
    @patch("os.mkdir")
    @patch("os.path")
    def test_fetch_images(
            self,
            mock_os_path,
            mock_os_mkdir,
            mock_fetch_image,
            mock_format_image):
        dirpath = random_string(20)
        filepath = random_string(20)
        inv_item = fake_inventory_item()
        inv_item.supplier_items = [fake_supplier_item(inv_item)]
        mock_os_path.exists.return_value = False
        mock_os_path.join.return_value = filepath

        with patch("builtins.open", mock_open()) as get_mock_file:
            images = fetch_images(dirpath, [inv_item])

            mock_file = get_mock_file()
            mock_file.write.assert_called_with(mock_fetch_image.return_value)

        mock_fetch_image.assert_called_with(inv_item)
        mock_format_image.assert_called_with(
            filepath, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT)
        mock_os_path.exists.assert_called_with(dirpath)
        mock_os_mkdir.assert_called_with(dirpath)
        self.assertEqual(len(images), 1)
        image = images[0]
        self.assertEqual(image.inventory_item, inv_item)
        self.assertEqual(image.filename, f"{inv_item.code}.jpg")


class ImageFormattingTests(DatabaseTestCase):

    def test_shrink_image_to_target(self):
        sizes = [
            # No change if same size as target.
            ((100, 100), (100, 100), (100, 100)),
            # Shrink image to fit width.
            ((200, 100), (100, 100), (100, 50)),
            # Shrink image to fit height.
            ((100, 200), (100, 100), (50, 100)),
        ]
        for original_size, target_size, output_size in sizes:
            resized_image = shrink_image_to_target(
                fake_image(original_size), target_size[0], target_size[1])

            self.assertEqual(resized_image.size, output_size)

    def test_shrink_target_to_image(self):
        sizes = [
            # No change if same size as image.
            ((100, 100), (100, 100), (100, 100)),
            # Shrink target width to fit image width.
            ((100, 100), (80, 60), (80, 80)),
            # Shrink target height to fit image height.
            ((100, 100), (50, 70), (70, 70)),
        ]
        for original_size, image_size, output_size in sizes:
            new_target_size = shrink_target_to_image(
                fake_image(image_size), original_size[0], original_size[1])

            self.assertEqual(new_target_size, output_size)

    @patch("pxi.image.get_canvas_image")
    def test_place_image_centered_on_canvas(
            self,
            mock_get_canvas_image):
        filepath = random_string(20)
        target_width = randint(100, 200) * 4
        target_height = randint(100, 200) * 4
        # Image dimensions half those of canvas image.
        image = fake_image((int(target_width / 2), int(target_height / 2)))
        canvas_image = MagicMock()
        canvas_image.size = (target_width, target_height)
        mock_get_canvas_image.return_value = canvas_image

        place_image_centred_on_canvas(
            image, filepath, target_width, target_height)

        mock_get_canvas_image.assert_called_with(
            filepath, target_width, target_height)
        canvas_image.paste.assert_called_with(
            image, (int(target_width / 4), int(target_height / 4)))

    def test_convert_nonrgb_image_to_rgb(self):
        image = MagicMock()
        image.mode = "P"  # Any mode other than RGB.
        convert_image_to_rgb(image)
        image.convert.assert_called_with("RGB")

    def test_return_unchanged_rgb_image(self):
        image = MagicMock()
        image.mode = "RGB"
        convert_image_to_rgb(image)
        image.convert.assert_not_called()

    @patch("pxi.image.convert_image_to_rgb")
    @patch("pxi.image.place_image_centred_on_canvas")
    @patch("pxi.image.shrink_image_to_target")
    @patch("pxi.image.Image")
    def test_format_large_image(
            self,
            mock_image_module,
            mock_shrink_image_to_target,
            mock_place_image_centred_on_canvas,
            mock_convert_image_to_rgb):
        filepath = random_string(20)
        target_width = randint(100, 200)
        target_height = randint(100, 200)
        image = fake_image((target_width + randint(100, 200),
                           target_height + randint(100, 200)))
        mock_image_module.open.return_value = image

        format_image(filepath, target_width, target_height)

        mock_image_module.open.assert_called_with(filepath)
        mock_shrink_image_to_target.assert_called_with(
            image, target_width, target_height)
        mock_place_image_centred_on_canvas.assert_called_with(
            image, CANVAS_IMAGE_FILEPATH, target_width, target_height)
        mock_convert_image_to_rgb.assert_called_with(
            mock_place_image_centred_on_canvas.return_value)

    @patch("pxi.image.convert_image_to_rgb")
    @patch("pxi.image.place_image_centred_on_canvas")
    @patch("pxi.image.shrink_target_to_image")
    @patch("pxi.image.Image")
    def test_format_small_image(
            self,
            mock_image_module,
            mock_shrink_target_to_image,
            mock_place_image_centred_on_canvas,
            mock_convert_image_to_rgb):
        filepath = random_string(20)
        target_width = randint(100, 200)
        target_height = randint(100, 200)
        image_width = int(target_width / 2)
        image_height = int(target_height / 2)
        image = fake_image((image_width, image_height))
        mock_image_module.open.return_value = image
        mock_shrink_target_to_image.return_value = (image_width, image_height)

        format_image(filepath, target_width, target_height)

        mock_image_module.open.assert_called_with(filepath)
        mock_shrink_target_to_image.assert_called_with(
            image, target_width, target_height)
        mock_place_image_centred_on_canvas.assert_called_with(
            image, CANVAS_IMAGE_FILEPATH, image_width, image_height)
        mock_convert_image_to_rgb.assert_called_with(
            mock_place_image_centred_on_canvas.return_value)
