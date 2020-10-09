from tkinter import *
from tkinter import messagebox
from PIL import ImageTk
import json


def askyesno(title, msg):
    return messagebox.askyesno(
        title=title,
        message=msg,
        icon='warning'
    )

class TkinterGui:
    def __init__(self, settings, bot):
        self.root = Tk()
        self.root.title("Skribbl Bot")
        self.settings = settings
        self.bot = bot

        # initialize empty attributes
        self.popup = None
        self.thumbnail = None
        self.canvas = None
        self.img_placeholder = None

        self.show_main_gui()
        self.run()

    def show_main_gui(self):
        # Create menubar
        menubar = Menu(self.root)
        menubar.add_command(label='Settings', command=self.show_settings)

        # Create canvas
        self.canvas = Canvas(self.root, width=200, height=200)
        self.canvas.pack()
        self.img_placeholder = PhotoImage(file="icons/picture.png")
        self.thumbnail = self.canvas.create_image((0, 0), image=self.img_placeholder, anchor=NW)

        frame = Frame(self.root)

        # Create buttons on left of entry
        self.add_tk_icon_btn('pencil', frame, "drawIm")
        self.add_tk_icon_btn('lArrow', frame, "prevIm")

        # Create frame number input
        image_name = Entry(frame, justify='center')
        image_name.bind("<Return>", lambda e: self.cmd_ctrl("getIms", image_name))
        image_name.pack(side=LEFT, padx=10)

        # Create buttons to right of entry
        self.add_tk_icon_btn('rArrow', frame, "nextIm")

        frame.pack()

        # Add menubar to root
        self.root.config(menu=menubar)

    def withdraw(self):
        self.root.withdraw()

    def deiconify(self):
        self.root.deiconify()

    def showImage(self, img):
        img_tk = ImageTk.PhotoImage(img)

        self.root.img_tk = img_tk
        self.canvas.itemconfig(self.thumbnail, image=img_tk)

    def changeImage(self, incr):
        if len(self.bot.imgs) > 0:
            self.bot.imgNum = (self.bot.imgNum + incr) % len(self.bot.imgs)
            self.showImage(self.bot.imgs[self.bot.imgNum])

    def cmd_ctrl(self, cmd, *args):
        print(cmd)
        if cmd in ['drawIm', 'setCoordsC', 'setCoordsP']:
            self.withdraw()
        if cmd in ['setCoordsC', 'setCoordsP']:
            self.popup.destroy()
        cmds = {
            "updateSettings": lambda: self.settings.update_settings(args[0]),
            "deleteProfile": lambda: self.settings.delete_settings_profile(),
            "changeProfile": lambda: self.settings.change_setting_profile(args[0]),
            "setCoordsC": lambda: self.settings.setup_canvas_coords(),
            "setCoordsP": lambda: self.settings.setup_pallete_coords(),
            "prevIm": lambda: self.changeImage(-1),
            "nextIm": lambda: self.changeImage(1),
            "drawIm": self.bot.drawImage,
            "getIms": lambda: self.bot.getImages(args[0])
        }
        # execute command from cmds dict
        cmds[cmd]()
        if cmd in ["updateSettings", "deleteProfile", "changeProfile", "setCoordsC", "setCoordsP"]:
            if self.popup:
                self.popup.destroy()
            self.show_settings()
        elif cmd in ['drawIm', 'setCoordsC', 'setCoordsP']:
            self.deiconify()
        elif cmd == "getIms":
            self.showImage(self.bot.imgs[0])

    def add_tk_icon_btn(self, img_name, frame, cmd):
        img = PhotoImage(file="icons/%s.png" % img_name)
        btn = Button(frame, image=img, command=lambda: self.cmd_ctrl(cmd))
        btn.pack(side=LEFT)
        btn.image = img  # keep a reference!
        return btn

    def add_tk_btn(self, frame, text, cmd, *args):
        btn = Button(frame, text=text, command=lambda: self.cmd_ctrl(cmd, *args))
        btn.pack(side=LEFT)
        return btn

    def add_tk_entry(self, name, frame, default_txt=None, btn=None):
        # create entry
        f = Frame(frame)
        f.pack()

        Label(f, text=name).pack(side=LEFT)
        e = Entry(f, width=50)
        if default_txt:
            if type(default_txt) in [dict,set,list]:
                e.insert(END, json.dumps(default_txt))
            else:
                e.insert(END, default_txt)
        e.pack(side=LEFT)
        if btn:
            Button(f, text=btn['text'],
                   command=lambda: self.cmd_ctrl(btn['cmd'],e)).pack(
                side=LEFT)
        return name, type(default_txt), e

    def show_settings(self):
        profile_name = self.settings.current
        popup = Toplevel(master=self.root, padx=50, pady=10)
        popup.title = "Settings"
        self.popup = popup  # reference to popup for use in cmd_ctrl

        self.add_tk_entry("Current Profile", popup, default_txt=profile_name,
                     btn={'text': 'change', 'cmd': 'changeProfile'})

        Message(popup, text="Settings for current profile:", width=300).pack()

        # create entries for every setting
        entries = []
        settings = [('Profile name', profile_name)] + list(self.settings.data['profiles'][profile_name].items())
        for setting_name, setting_val in settings:
            entries.append(self.add_tk_entry(setting_name, popup, default_txt=setting_val))

        # add twom rows of buttons
        frame = Frame(popup)
        self.add_tk_btn(frame, "Set colour palette coordinates", "setCoordsP")
        self.add_tk_btn(frame, "Set canvas coordinates", "setCoordsC")
        frame.pack()

        frame = Frame(popup)
        self.add_tk_btn(frame, "Apply Settings", "updateSettings", entries)
        self.add_tk_btn(frame, "Delete profile", "deleteProfile")
        frame.pack()

    def run(self):
        # Start Tkinter main loop
        self.root.mainloop()
