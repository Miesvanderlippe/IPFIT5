from Utils.FilePicker import FilepickerFrame
from Utils.Store import Store
from Utils.ImageHandler import ImageHandler
from asciimatics.widgets import Frame, Layout, Label, Text, \
    Button, PopUpDialog, Background, Divider, TextBox
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, \
    StopApplication, InvalidFields
import sys
import logging

from sys import platform
from subprocess import call
from pathlib import Path

logging.basicConfig(filename="forms.log", level=logging.DEBUG)


class MainApp(Frame):
    def __init__(self, screen):
        self.stores = Store()
        self._screen = screen

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
        self.image_label = TextBox(height=2,
                                   as_string=True,
                                   label='Image:',
                                   name='IA')
        self.image_label.disabled = True
        self.image_label.custom_colour = 'label'
        self.image_info_button = Button('Image info', self.file_info)
        self.image_info_button.disabled = True

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

        image_layout = Layout([1, 18, 1])
        self.add_layout(image_layout)

        image_layout.add_widget(Divider(height=3), 1)

        image_layout.add_widget(self.image_label, 1)

        image_buttons_layout = Layout([1, 9, 9, 1])
        self.add_layout(image_buttons_layout)

        image_buttons_layout.add_widget(
            Button('Select image', self.file_picker), 1)
        image_buttons_layout.add_widget(self.image_info_button, 2)

        image_buttons_layout.add_widget(Divider(height=3), 1)
        image_buttons_layout.add_widget(Divider(height=3), 2)

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

    def file_info(self):
        image_handler = ImageHandler()
        metadata = image_handler.encase_metadata()
        volume_information = image_handler.volume_info()

        if len(metadata) > 0:
            metadata.append('')

        self._scene.add_effect(
            PopUpDialog(self._screen,
                        '\n'.join([*metadata, *volume_information]), ['OK']))

    def file_picker(self):
        raise NextScene('FilePicker')

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

    @staticmethod
    def finished(_):
        MainApp.open_file(Path(__file__).joinpath('Output'))
        raise StopApplication('Task done')

    @staticmethod
    def open_file(filename):
        if platform == "win32":
            from os import startfile
            startfile(filename)
        else:
            opener = "open" if platform == "darwin" else "xdg-open"
            call([opener, filename])


def demo(screen, scene):
    screen.play([Scene([
        Background(screen, Screen.COLOUR_WHITE),
        MainApp(screen)
    ], -1, name='Main'),
        Scene([FilepickerFrame(screen)], -1, name='FilePicker')],
        stop_on_resize=True, start_scene=scene)


if __name__ == '__main__':
    last_scene = None
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
