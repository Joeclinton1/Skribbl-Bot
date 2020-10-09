import json
import win32api
import win32con
import time
import PIL.ImageGrab
from Scrible_bot.tkinter_gui import askyesno

def change_str_data_type(s, data_type):
    if data_type in (float, int):
        return float(s)
    if data_type in (dict, set, list):
        return json.loads(s)
    else:
        return s


def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


class Settings:
    def __init__(self, data_file_name='data.json', ):
        self.data_fn = data_file_name
        # init settings
        self.data = None
        self.current = None
        self.c_coords = None
        self.xy_size = None
        self.xpad = None
        self.ypad = None
        self.pixel_size = None
        self.delay = None
        self.res_scale = None
        self.percent_of_canvas = None

        self.load_settings()

    def save_settings_json(self):
        with open('data.json', 'w') as outfile:
            json.dump(self.data, outfile)

    def load_settings(self):
        with open(self.data_fn) as json_file:
            self.data = json.load(json_file)
            self.current = self.data['current_profile']

            if self.current not in self.data['profiles']:
                print("Profile does not exist")
                return

            p = self.data['profiles'][self.current]  # current profile
            bbox = p['bbox']  # top-left corner x, y then bottom-right corner x,y
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

            self.c_coords = p['c_coords']
            self.percent_of_canvas = p["percent_of_canvas"]  # percentage of the canvas width.
            s = self.percent_of_canvas/100

            self.pixel_size = p['pixel_size']
            self.xy_size = (int(w*s/self.pixel_size),int(h*s/self.pixel_size))  # size in pixels
            self.xpad = int(bbox[0] + w * (1-s)/2)
            self.ypad = int(bbox[1] + h * (1-s)/2)
            print(self.xpad,self.ypad)

            self.delay = p['delay']
            self.res_scale = p["resolution_scale"]


    def change_setting_profile(self, entry):
        current_profile = str(entry.get())
        if current_profile not in self.data['profiles']:
            response = askyesno(
                "Create Profile",
                '"%s" does not exist. Create new profile with this name?' % current_profile
            )
            if response:
                self.data['profiles'][current_profile] = self.data['profiles']['default']
            else:
                print("profile creation aborted")
                return
        self.data['current_profile'] = current_profile
        print("Current profile is now: ", current_profile)
        self.save_settings_json()
        self.load_settings()

    def update_settings(self, setting_entries):
        for setting_name, data_type, entry in setting_entries:
            setting_val = entry.get()

            if setting_name == 'Profile name':
                if setting_val != self.current:
                    if self.current != "default":
                        self.data['profiles'][setting_val] = self.data['profiles'][self.current]
                        del self.data['profiles'][self.current]
                        self.data['current_profile'] = setting_val
                        self.current = setting_val
                    else:
                        print("Default profile's name cannot be changed")
            else:
                setting_val = change_str_data_type(setting_val, data_type)
                self.data['profiles'][self.current][setting_name] = setting_val
        self.save_settings_json()
        print("Applied settings")
        self.load_settings()

    def delete_settings_profile(self):
        if self.current != 'default':
            del self.data['profiles'][self.current]
            self.data['current_profile'] = 'default'
            self.current = 'default'
            self.save_settings_json()
            self.load_settings()
            print("Profile deleted")
        else:
            print("Default profile cannot be deleted")

    def setup_canvas_coords(self):
        # Find the canvas padding
        # Find the coords of the colour pallete

        print(
            '''Shift-Click the top-left canvas corner and then the bottom right. This will change your pad_x, pad_y and size settings.''')

        win32api.GetAsyncKeyState(win32con.VK_LBUTTON)
        bbox = []
        for i in range(2):
            while 1:
                time.sleep(0.1)
                if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) and win32api.GetAsyncKeyState(win32con.VK_SHIFT):
                    while win32api.GetAsyncKeyState(win32con.VK_LBUTTON) and win32api.GetAsyncKeyState(win32con.VK_SHIFT):
                        time.sleep(0.05)
                    break
            cursor_pos = win32api.GetCursorPos()
            print("Clicked at", cursor_pos)
            bbox.extend(cursor_pos)
        self.data['profiles'][self.current]['bbox'] = bbox
        self.save_settings_json()
        print("Settings profile updated")

    def setup_pallete_coords(self):
        def get_pixel_colour(i_x, i_y):
            img = PIL.ImageGrab.grab()
            r, g, b = img.load()[i_x * self.res_scale, i_y * self.res_scale]
            return rgb_to_hex(r, g, b)  # :02x converts num to 2 digit hex

        # Find the coords of the colour pallete
        print('''
Shift-click one by one on each colour in the Skribbl colour pallete, starting with white.
After clicking 22 times (the number of colours) the settings for the colour pallette coords will be automatically updated.
You will need a private Skribbl room to do this.
        ''')
        c_coords = {}
        win32api.GetAsyncKeyState(win32con.VK_LBUTTON)
        for i in range(22):
            while 1:
                time.sleep(0.1)
                if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) and win32api.GetAsyncKeyState(win32con.VK_SHIFT):
                    print("click")
                    break
            cursor_pos = win32api.GetCursorPos()
            pixel_colour = get_pixel_colour(cursor_pos[0], cursor_pos[1])
            print(pixel_colour, cursor_pos)
            c_coords[pixel_colour] = cursor_pos
        self.data['profiles'][self.current]['c_coords'] = c_coords
        self.c_coords = c_coords

        self.save_settings_json()

        print("Settings profile updated")
