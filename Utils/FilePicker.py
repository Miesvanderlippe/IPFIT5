from os import path
from asciimatics.event import KeyboardEvent, Event
from asciimatics.widgets import Frame, Layout, FileBrowser, Widget, Label, \
    Text, Divider
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication, \
    NextScene
from Utils.Store import Store


class FilepickerFrame(Frame):
    def __init__(self, screen: Screen) -> None:
        super(FilepickerFrame, self).__init__(
            screen, screen.height, screen.width, has_border=False,
            name="Filepicker")

        self.store = Store().image_store

        # Create the form layout...
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        # Now populate it with the widgets we want to use.
        self._details = Text()
        self._details.disabled = True
        self._details.custom_colour = "field"
        self._list = FileBrowser(Widget.FILL_FRAME,
                                 path.abspath("."),
                                 name="mc_list",
                                 on_select=self.selected)
        layout.add_widget(Label("Image file picker"))
        layout.add_widget(Divider())
        layout.add_widget(self._list)
        layout.add_widget(Divider())
        layout.add_widget(self._details)
        layout.add_widget(Label("Press Enter to select or `q` to return."))

        # Prepare the Frame for use.
        self.fix()

    def selected(self) -> None:
        # Just confirm whenever the user actually selects something.
        self.store.dispatch({'type': 'set_image', 'image': self._list.value})
        raise NextScene

    def process_event(self, event: Event) -> Event:
        # Do the key handling for this Frame.
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
                raise StopApplication("User quit")

        # Now pass on to lower levels for normal handling of the event.
        return super(FilepickerFrame, self).process_event(event)


def filepicker(screen: Screen, old_scene: Scene) -> None:
    screen.play([Scene([FilepickerFrame(screen)], -1)],
                stop_on_resize=True, start_scene=old_scene)


def filepicker_main() -> None:
    last_scene = None
    while True:
        try:
            Screen.wrapper(filepicker, catch_interrupt=False,
                           arguments=[last_scene])
            break
        except ResizeScreenError as e:
            last_scene = e.scene
