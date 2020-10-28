#!/usr/bin/env python3

import argparse
import os
from PIL import Image     # image manipulation library


def resize_image(filepath, target_width, target_height):
    image_resizer = ImageResizer(filepath, target_width, target_height)
    image_resizer.shrink_to_fit()
    image_resizer.fill_background()
    image_resizer.save(filepath)


class ImageResizer:

    def __init__(self, imagefile, target_width, target_height):
        try:
            self.image = Image.open(imagefile)
        except IOError:
            print('file not found: ' + imagefile)

        self.target_width = target_width
        self.target_height = target_height
        # Convert target dimensions to floats so we can take the quotient.
        self.target_aspect_ratio = float(
            target_width) / float(self.target_height)

    def shrink_to_fit(self):
        # Compute the aspect ratio of the source file
        # and the target size.
        orig_width, orig_height = self.image.size
        orig_aspect_ratio = float(orig_width) / float(orig_height)

        # Shrink the image to fit if it is larger than the target size,
        # or shrink the target size if it is larger than the image.
        if orig_width >= self.target_width or orig_height >= self.target_height:
            if orig_aspect_ratio >= self.target_aspect_ratio:
                # Resize image to target width.
                new_width = self.target_width
                new_height = int(self.target_width / orig_aspect_ratio)
            else:
                # Resize image to target height.
                new_width = int(self.target_height * orig_aspect_ratio)
                new_height = self.target_height

            self.image = self.image.resize((new_width, new_height))

        else:
            if orig_aspect_ratio >= self.target_aspect_ratio:
                # Resize target size to image width.
                self.target_width = orig_width
                self.target_height = int(orig_width / self.target_aspect_ratio)
            else:
                # Resize target size to image height.
                self.target_height = orig_height
                self.target_width = int(orig_height * self.target_aspect_ratio)

    def fill_background(self):
        # Resize a blank white image to the target size to create a white canvas.
        canvas_image = Image.open('pxi/blank.jpg')
        target_size = (self.target_width, self.target_height)
        canvas_image = canvas_image.resize(target_size)

        # Place the image in the centre of the blank canvas.
        width, height = self.image.size
        xPos = int((self.target_width - width) / 2)
        yPos = int((self.target_height - height) / 2)
        canvas_image.paste(self.image, (xPos, yPos))

        # Replace the image with the image-on-canvas.
        self.image = canvas_image

    def save(self, outfile):
        if self.image.mode == 'P':
            self.image = self.image.convert('RGB')
        self.image.save(outfile, 'JPEG')
