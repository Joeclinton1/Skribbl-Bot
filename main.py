from Skribbl-Bot.settings import Settings
from Skribbl-Bot.skribbl_bot import SkribblBot
from Skribbl-Bott.tkinter_gui import TkinterGui

if __name__ == '__main__':
    settings = Settings()
    bot = SkribblBot(settings)
    TkinterGui(settings,bot)
