from datetime import datetime
from Models.LogEntryModel import LogEntryModel
from Utils.XlsxWriter import XlsxWriter
from pathlib import Path

import logging


class ExtendedLogger:

    instances = {}

    def __init__(self, name):
        log_folder = Path(Path(__file__).parent.parent.joinpath("Logs"))
        Path.mkdir(log_folder, exist_ok=True)
        logging.basicConfig(filename=log_folder.joinpath("IPFIT5.log"),
                            format='%(asctime)s - %(name)s - %(levelname)s - '
                                   '%(message)s',
                            level=logging.DEBUG)
        self.Logger = logging.getLogger(name)
        self.name = name
        self.entries = []
        ExtendedLogger.instances[name] = self

    @staticmethod
    def get_instance(name):
        if name not in ExtendedLogger.instances:
            ExtendedLogger(name)
        return ExtendedLogger.instances[name]

    def write_log(self, log_entry: LogEntryModel) -> None:
        log_entry.module = self.name
        self.entries.append(log_entry)

        if log_entry.resultType == LogEntryModel.ResultType.positive:
            self.Logger.info(log_entry.get_message())
        elif log_entry.resultType == LogEntryModel.ResultType.negative:
            self.Logger.warning(log_entry.get_message())
        elif log_entry.resultType == LogEntryModel.ResultType.informative:
            self.Logger.info(log_entry.get_message())
        elif log_entry.resultType == LogEntryModel.ResultType.error:
            self.Logger.error(log_entry.get_message())

    def export_logs(self) -> None:
        name = "Logs: {0}".format(self.name)
        xlsx_writer = XlsxWriter(name)
        xlsx_writer.add_worksheet("Logs")
        xlsx_writer.write_headers("Logs", LogEntryModel.workbook_headers)

        xlsx_writer.write_items("Logs",
                                [x.worksheet_items for x in self.entries])
        self.entries = []
        xlsx_writer.close()

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
    logger = ExtendedLogger("Test")

    log1 = LogEntryModel()

    log1.resultType = LogEntryModel.ResultType.informative

    log1.who = "Mies"
    log1.what = "Log testing"
    log1.method = "Testing"
    log1.using = "Logger"
    log1.result = "Log tested succesfully"

    logger.write_log(log1)
    logger.quit_all_instances()
