from google_images_download import google_images_download
import numpy as np
import win32api
import win32con
import time
from PIL import Image
import json

def hex_to_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


class SkribblBot:
    def __init__(self, settings):
        self.kw = ""
        self.imgNum = 0
        self.imgs = []

        self.palette = []
        self.settings = settings
        for colour in self.settings.c_coords.keys():
            self.palette.extend(hex_to_rgb(colour))
        self.response = google_images_download.googleimagesdownload()

    def quantize_image(self, img):
        palette = self.palette + [0, ] * (256 - len(self.palette)) * 3
        # a palette image to use for quant
        pimage = Image.new("P", (1, 1), 0)
        pimage.putpalette(palette)
        imagep = img.quantize(palette=pimage)
        return imagep, palette

    def getImages(self, image_name):
        self.kw = image_name.get() + " cartoon"
        arguments = {'keywords': self.kw, 'limit': 4,
                     'output_directory': 'C:/Users/Joe/OneDrive/Documents/python/Image_search'}
        img_paths = self.response.download(arguments)[0][self.kw]
        img_paths = [x for x in img_paths if x[-3:] != "svg"]
        self.imgs = []
        for img_path in img_paths:
            img = Image.open(img_path).convert("RGB")
            img.thumbnail(self.settings.xy_size, Image.ANTIALIAS)
            img, new_palette = self.quantize_image(img)
            self.imgs.append(img)
        self.imgNum = 0

    def drawImage(self):
        c_coords, xpad, ypad, pixel_size, delay = [
            getattr(self.settings, attr) for attr in ['c_coords', 'xpad', 'ypad', 'pixel_size', 'delay']
        ]
        # check if image exists
        if len(self.imgs) == 0:
            return
        img = self.imgs[self.imgNum]
        img_np = np.asarray(img)
        max_line_len = 8
        for i in range(1, 22, 1):
            colour_ar = img_np == i
            coord_ar = []
            count = 0
            prev_x = 0
            prev_y = 0
            buffer = []
            for index, x in np.ndenumerate(colour_ar):
                if x:
                    if index[1] == prev_x + 1 and index[0] == prev_y:
                        if count < max_line_len + 1:
                            count += 1
                    else:
                        count = 0
                    if count < max_line_len + 1 and index != (0, 0):
                        coord_ar.append(buffer)
                        buffer = []
                    if count == max_line_len:
                        buffer = [coord_ar[-max_line_len][0]]
                        coord_ar = coord_ar[:-max_line_len]
                    if count == max_line_len + 1:
                        buffer.pop()
                    buffer.append(index)
                    prev_x = index[1]
                    prev_y = index[0]

            win32api.SetCursorPos(list(c_coords.values())[i])
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            for chunk in coord_ar:
                for i, coord in enumerate(chunk):
                    win32api.SetCursorPos(
                        (int(xpad + coord[1] * pixel_size), int(ypad + coord[0] * pixel_size)))
                    if coord[1] - chunk[0][1] > 0:
                        if i == len(chunk) - 1:
                            time.sleep(0.017)
                    if i == 0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                        time.sleep(delay)
                    if i == len(chunk) - 1:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                if win32api.GetAsyncKeyState(win32con.VK_SHIFT):
                    return
if __name__ == '__main__':
    SkribblBot()
