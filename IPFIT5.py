# from os import sep

# from Modules.EmailModule import EmailModule
# from Modules.HackedModule import HackedModule
# from Modules.PhotoModule import PhotoModule
# from Modules.FileModule import FileModule

# from Utils.FilePicker import filepicker_main as image_filepicker
from Utils.Store import Store

# from Utils.Menu import Menu

# from asciimatics import screen
# from time import sleep

from asciimatics.widgets import Frame, Layout, Label, Text, \
    Button, PopUpDialog, Background, Divider
# , Divider, TextBox, DropdownList, PopupMenu, CheckBox, RadioButtons,
# TimePicker, DatePicker,
# from asciimatics.event import MouseEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, \
    StopApplication, InvalidFields
import sys
# import re
# import datetime
import logging


logging.basicConfig(filename="forms.log", level=logging.DEBUG)


class MainApp(Frame):
    def __init__(self, screen):
        self.stores = Store()

        credential_state = self.stores.credential_store.get_state()
        current_state = {**credential_state}

        super(MainApp, self).__init__(
            screen,
            int(screen.height * 2 // 3),
            int(screen.width * 2 // 3),
            data=current_state,
            has_shadow=True,
            name="IPFIT5",
            can_scroll=False
        )

        # Store related stuff
        self.image_picker = None
        self.image = None

        # Set up the layout
        layout = Layout([1, 18, 1])
        self.add_layout(layout)
        self._reset_button = Button("Reset", self._reset)
        layout.add_widget(Label("Informatie over onderzoek:", height=2), 1)
        layout.add_widget(
            Text(label="Onderzoeker:",
                 name="name",
                 on_change=self._on_change,
                 ), 1)

        layout.add_widget(
            Text(label="Case:",
                 name="case",
                 on_change=self._on_change,
                 ), 1)

        layout.add_widget(
            Text(label="Locatie:",
                 name="location",
                 on_change=self._on_change,
                 ), 1)

        layout.add_widget(Button("Save to disk", self.save_creds_to_disk), 1)

        layout.add_widget(Divider(height=3), 1)

        # Add some buttons
        layout2 = Layout([1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(self._reset_button, 0)
        layout2.add_widget(Button("View Data", self._view), 1)
        layout2.add_widget(Button("Quit", self._quit), 2)

        self.fix()
        # submenu_email = Menu(EmailModule.menu(), self.screen)
        # submenu_hacked = Menu(HackedModule.menu(), self.screen)
        # submenu_photos = Menu(PhotoModule.menu(), self.screen)
        # submenu_files = Menu(FileModule.menu(), self.screen)

        # if self.stores.image_store.get_state() == 'initial' \
        #        or self.stores.image_store.get_state() is None:
        #     main_menu_items = [
        #        ('Load image', self.filepicker)
        #    ]
        # else:
        #    main_menu_items = [
        #        ('Load image (Selected image: {})'.format(
        #            self.stores.image_store.get_state().split(sep)[-1]),
        #            self.filepicker),
        #        ('Emails', submenu_email.display),
        #        ('Hacked', submenu_hacked.display),
        #        ('Pictures', submenu_photos.display),
        #        ('Files', submenu_files.display)
        #    ]
        # main_menu = Menu(main_menu_items, self.screen, sub=False)
        # main_menu.display()

    def save_creds_to_disk(self) -> None:
        self.stores.credential_store.dispatch({'type': 'save_to_disk'})

    def _view(self):
        # Build result of this form and display it.
        try:
            self.save(validate=True)
            message = "Values entered are:\n\n"
            for key, value in self.data.items():
                message += "- {}: {}\n".format(key, value)
        except InvalidFields as exc:
            message = "The following fields are invalid:\n\n"
            for field in exc.fields:
                message += "- {}\n".format(field)
        self._scene.add_effect(
            PopUpDialog(self._screen, message, ["OK"]))

    def _on_change(self):
        self.save()
        changed = False
        cred_state = self.stores.credential_store.get_state()
        form_state = {x[0]: x[1] for x in self.data.items()}

        if any([
            x for x in ["name", "location", "case"]
            if form_state[x] != cred_state[x]]
        ):
            self.stores.credential_store.dispatch(
                {
                    'type': 'set_credentials',
                    'credentials': {
                        'name': form_state['name'],
                        'case': form_state['case'],
                        'location': form_state['location'],
                    }
                })
            changed = True

        self._reset_button.disabled = not changed

    def _reset(self):
        self.reset()
        raise NextScene()

    def _quit(self):
        self._scene.add_effect(
            PopUpDialog(
                self._screen,
                "Are you sure?",
                ["Yes", "No"],
                on_close=self._quit_on_yes))

    @staticmethod
    def _quit_on_yes(selected):
        # Yes is the first button
        if selected == 0:
            raise StopApplication("User requested exit")

    # def filepicker(self):
    #     image_filepicker()


def demo(screen, scene):
    screen.play([Scene([
        Background(screen, Screen.COLOUR_WHITE),
        MainApp(screen)
    ], -1)], stop_on_resize=True, start_scene=scene)


if __name__ == '__main__':
    last_scene = None
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
