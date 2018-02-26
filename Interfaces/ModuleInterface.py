import curses
from Utils.Logger import ExtendedLogger


class ModuleInterface:

    logger = ExtendedLogger()

    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def menu():
        menu_items = [
            ('Placeholder', curses.beep)
        ]

        return menu_items

    def run(self):
        """
        Should run the module
        :return: None
        """
        raise NotImplementedError()

    def status(self):
        """
        Should return the current status using a string (starting, runnning,
        done etc).
        :return: the status
        """
        raise NotImplementedError()

    def progress(self):
        """
        Progress in percentage.
        :return: Progression
        """
        raise NotImplementedError()
