import curses

from os import sep

from FilePicker import filepicker_main as image_filepicker
from Store import Store
from Menu import Menu

from Modules.EmailModule import EmailModule
from Modules.HackedModule import HackedModule
from Modules.PhotoModule import PhotoModule
from Modules.FileModule import FileModule

global_stores = Store()


class MainApp(object):
    def __init__(self, stdscreen):
        global global_stores
        self.stores = global_stores
        self.image_picker = None
        self.image = None
        self.screen = stdscreen
        curses.curs_set(0)

        submenu_email = Menu(EmailModule.menu(), self.screen)
        submenu_hacked = Menu(HackedModule.menu(), self.screen)
        submenu_photos = Menu(PhotoModule.menu(), self.screen)
        submenu_files = Menu(FileModule.menu(), self.screen)

        if self.stores.image_store.get_state() == 'initial' or self.stores.image_store.get_state() is None:
            main_menu_items = [
                ('Load image', self.filepicker)
            ]
        else:
            main_menu_items = [
                ('Load image (Selected image: {})'.format(self.stores.image_store.get_state().split(sep)[-1]), self.filepicker),
                ('Emails', submenu_email.display),
                ('Hacked', submenu_hacked.display),
                ('Pictures', submenu_photos.display),
                ('Files', submenu_files.display)
            ]
        main_menu = Menu(main_menu_items, self.screen, sub=False)
        main_menu.display()

    def filepicker(self):
        image_filepicker(self.stores.image_store)
        curses.wrapper(MainApp)


if __name__ == '__main__':
    curses.wrapper(MainApp)
