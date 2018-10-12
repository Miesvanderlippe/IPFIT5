from Models.LogEntryModel import LogEntryModel
from Utils.XlsxWriter import XlsxWriter
from pathlib import Path

import logging


class ExtendedLogger:

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
