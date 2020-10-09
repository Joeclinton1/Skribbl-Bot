from Scrible_bot.settings import Settings
from Scrible_bot.skribbl_bot import SkribblBot
from Scrible_bot.tkinter_gui import TkinterGui

if __name__ == '__main__':
    settings = Settings()
    bot = SkribblBot(settings)
    TkinterGui(settings,bot)