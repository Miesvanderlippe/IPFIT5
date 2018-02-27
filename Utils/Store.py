import pydux
from Utils.Singleton import Singleton


class Store(metaclass=Singleton):
    def __init__(self) -> None:
        self.image_store = pydux.create_store(self.image)

    @staticmethod
    def image(state: str, action: [str, str]) -> str:
        if state is None:
            state = 'initial'
        if action is None:
            return state
        elif action['type'] == 'set_image':
            state = action['image']
        return state
