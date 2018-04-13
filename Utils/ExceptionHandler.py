from Utils.Logger import LogEntryModel
from Utils.Logger import ExtendedLogger
import sys


def exceptionlogger(etype, value, tb):
    try:
        logger = ExtendedLogger.get_instance("Exceptions")
        logger.write_log(LogEntryModel.create_logentry(
            LogEntryModel.ResultType.error,
            "Catching error {0}".format(str(value)),
            "error occured", "sys.excepthook = excepthook",
            "using excepthook and logger", "trace" + str(tb))
        )
        if len(logger.entries) > 1000:
            print("Too many exceptions")
            exit(0)

    except Exception as e:
        print("Exceptionhanlder crashed")
        exit(0)


if __name__ == '__main__':
    sys.excepthook = exceptionlogger

    try:
        raise ValueError
    finally:
        logger = ExtendedLogger("Exceptions")
        logger.quit_all_instances()
