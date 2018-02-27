from Interfaces.ModuleInterface import ModuleInterface


class PhotoModule(ModuleInterface):

    def __init__(self) -> str:
        super().__init__()


if __name__ == '__main__':
    module = PhotoModule()
    print(module.logger.name)  # PhotoModule
