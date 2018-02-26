import logging
from Models.LogEntryModel import LogEntryModel


class ExtendedLogger(logging.Logger):

    def __init__(self, class_name):
        super().__init__(class_name)

    def write_log(self, log_entry):

        if log_entry.resultType == LogEntryModel.ResultType.positive:
            self.info(log_entry.get_message())
        elif log_entry.resultType == LogEntryModel.ResultType.negative:
            self.warning(log_entry.get_message())
        elif log_entry.resultType == LogEntryModel.ResultType.informative:
            self.info(log_entry.get_message())
        elif log_entry.resultType == LogEntryModel.ResultType.error:
            self.error(log_entry.get_message())
