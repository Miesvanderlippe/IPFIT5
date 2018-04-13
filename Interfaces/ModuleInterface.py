from abc import ABC, abstractmethod
from Utils.Logger import ExtendedLogger


class ModuleInterface(ABC):
    """
    WIP interface for modules to communicate with the framework.
    """

    def __init__(self) -> None:
        self.logger = ExtendedLogger.get_instance(self.__class__.__name__)

    @abstractmethod
    def run(self) -> None:
        """
        Should run the module
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def status(self) -> str:
        """
        Should return the current status using a string (starting, runnning,
        done etc).
        :return: the status
        """
        raise NotImplementedError()

    @abstractmethod
    def progress(self) -> int:
        """
        Progress in percentage.
        :return: Progression
        """
        raise NotImplementedError()
