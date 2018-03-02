import pydux
from Utils.Singleton import Singleton
from pathlib import Path
from os import linesep


class Store(metaclass=Singleton):
    def __init__(self) -> None:
        self.image_store = pydux.create_store(self.image)
        self.credential_store = pydux.create_store(self.credential)

    @staticmethod
    def get_config_save_path(type: str) -> Path:
        """
        Generates a path in the root of the project where a config path can be
        saved. It makes the directory if it doesn't exist yet and creates the
        log file when that doesn't exist yet.
        :param type: The config name
        :return: A Path object pointing to the correct log path
        """
        # Make config folder
        config_path = Path(__file__).parent.parent.joinpath('Configs')
        Path.mkdir(Path(config_path), exist_ok=True)

        # Make config file
        config_file_path = Path(config_path.joinpath("{0}.cfg".format(type)))
        Path.touch(config_file_path, exist_ok=True)

        return config_file_path

    @staticmethod
    def write_config_to_disk(path: Path, config: dict) -> None:
        """
        Writes the supplied configuration dictionary to the path on disk.
        NOTE: This doesn't support linebreaks yet.
        :param path: Path to write to (including specific file)
        :param config: Configuration to write to disk (key, value)
        :return: Nothing
        """
        with open(path, 'w') as file:
            file.writelines(
                linesep.join([str(x) + ":" + str(y) for x, y in config.items()])
            )

    @staticmethod
    def read_config_from_disk(path: Path, defaults: dict) -> dict:
        """
        Fills a config using values found on disk. Supply it with a config path
        and a defaults dict. Be warned; the defaults dict dictates the keys to
        be loaded from disk. Any keys not in the defaults dict will NOT be
        added to the config and will be lost.
        :param path: Path to config file
        :param defaults: Dict with keys and defaults for each value
        :return: A filled config
        """
        with open(path, 'r') as file:
            lines = {
                # The first item is the key, the rest is it's value. Join it
                # back with the colon we split on.
                split_line[0]: ":".join(split_line[1::]) for split_line in
                # Strip the linebreak, break on :
                [line.strip().split(':') for line in file.readlines()]
            }

        # Look trough keys in defaults and check if a better value is
        # found on disk.
        for key, value in defaults.items():
            if key in lines:
                defaults[key] = lines[key]

        return defaults

    @staticmethod
    def credential(state: str, action: [str, str]) -> dict:
        """
        DO NOT USE THIS DIRECTLY
        Credential store.
        Save config to disk:
        credential_store.dispatch({'type': 'safe_to_disk'}

        Set a specific value:
        credential_store.dispatch(
        {
            'type': 'set_location',
            'location': 'value'
        }

        Set all values:
        credential_store.dispatch(
        {
            'type': 'set_credentials',
            'credentials': {
                'name': 'value',
                'case': 'value',
                'location': 'value',
            }
        }

        Get all values:
        credential_store.get_state()
        """
        if state is None:
            state = Store.read_config_from_disk(
                Store.get_config_save_path('credentials'),
                {
                    'name': 'Default',
                    'location': 'Default location (None specified)',
                    'case': '001'
                }
            )

        if action is None:
            return state
        elif action['type'] == 'set_credentials':
            state = {
                'name': action['credentials']['name'],
                'location': action['credentials']['location'],
                'case': action['credentials']['case'],
            }
        elif action['type'] == 'set_location':
            state['location'] = action['location']
        elif action['type'] == 'set_name':
            state['location'] = action['name']
        elif action['type'] == 'set_case':
            state['case'] = action['case']
        elif action['type'] == 'safe_to_disk':
            Store.write_config_to_disk(
                Store.get_config_save_path("credentials"),
                state
            )
        return state

    @staticmethod
    def image(state: str, action: [str, str]) -> str:
        """
        DO NOT USE THIS DIRECTLY
        Very simple store for saving the path to the image.
        """
        if state is None:
            state = 'initial'
        if action is None:
            return state
        elif action['type'] == 'set_image':
            state = action['image']
        return state


if __name__ == '__main__':
    stores = Store()

    print(stores.credential_store.get_state())

    stores.credential_store.dispatch({'type': 'safe_to_disk'})
    stores.credential_store.dispatch({'type': 'set_location',
                                      'location': 'value'})

    print(stores.credential_store.get_state())
