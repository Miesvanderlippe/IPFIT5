from Utils.Logger import ExtendedLogger
from Utils.XlsxWriter import XlsxWriter

from Models.LogEntryModel import LogEntryModel


class LoggerFactory:
    instances = {}

    def __init__(self):
        raise Exception("Don't instantiate me.")

    @staticmethod
    def get_instance(name):
        if name not in LoggerFactory.instances:
            instance = ExtendedLogger(name)
            LoggerFactory.instances[name] = instance

        return LoggerFactory.instances[name]

    @staticmethod
    def quit_all_instances(self) -> None:
        xlsx_writer = XlsxWriter("Logs")
        for instance_name, instance in self.instances.items():
            xlsx_writer.add_worksheet(instance_name)
            xlsx_writer.write_headers(instance_name,
                                      LogEntryModel.workbook_headers)
            xlsx_writer.write_items(
                instance_name, [x.worksheet_items for x in instance.entries])

        self.instances = {}


if __name__ == '__main__':
    try:
        LoggerFactory()
    except Exception as e:
        print(e)

    logger1 = LoggerFactory.get_instance("Test")
    logger2 = LoggerFactory.get_instance("Test")

    print("ID1 {0} ID2 {1}".format(id(logger1), id(logger2)))
