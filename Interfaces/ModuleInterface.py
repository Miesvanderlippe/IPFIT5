
class ModuleInterface:
    def __init__(self):
        raise NotImplementedError()

    def run(self) -> None:
        """
        Should run the module
        :return: None
        """
        raise NotImplementedError()

    def status(self) -> str:
        """
        Should return the current status using a string (starting, runnning,
        done etc).
        :return: the status
        """
        raise NotImplementedError()

    def progress(self) -> int:
        """
        Progress in percentage.
        :return: Progression
        """
        raise NotImplementedError()
