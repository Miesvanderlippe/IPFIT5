from datetime import datetime
from Utils.Store import Store


class LogEntryModel:
    """
    A class to represent log entries in a more flexible way. It displays
    entries using vibrant colours or as a more neutral string. It's primary
    function is to carry the information throughout the program.
    """
    workbook_headers = [
        "type",
        "when",
        "who",
        "what",
        "where",
        "why",
        "method",
        "using",
        "result"
    ]

    def __init__(self) -> None:

        store = Store()

        # When the event happened
        self.when = datetime.now()
        # Who started the event
        self.who = store.credential_store.get_state()["name"]
        # What's happening
        self.what = ""
        # Where it happened
        self.where = store.credential_store.get_state()["location"]
        # Why it's happening
        self.why = ""
        # How we're doing we're doing it
        self.method = ""
        # What we're using to archive the goal
        self.using = ""
        # What the result is
        self.result = ""
        # The module that created the instance.
        self.module = "Logger"
        # Whether the entry is information, an error or a negative or positive
        # result
        self.resultType = LogEntryModel.ResultType.informative

    @property
    def worksheet_items(self) -> []:
        return [
            self.resultType,
            self.when.strftime('%d-%m-%Y %H:%M:%S'),
            self.who,
            self.what,
            self.where,
            self.why,
            self.method,
            self.using,
            self.result
        ]

    @staticmethod
    def create_logentry(result_type, what: str="", why: str="", method: str="",
                        using: str="", result: str=""):
        """
        Creates a logentry using the parameters given. Shorter than creating an
        instance and filling it.
        :param result_type:
        :param what:
        :param why:
        :param method:
        :param using:
        :param result:
        :return: A log entry
        """

        entry = LogEntryModel()

        entry.what = what
        entry.why = why
        entry.method = method
        entry.using = using
        entry.result = result
        entry.resultType = result_type

        return entry

    class ResultType:
        positive = "[+]"
        negative = "[-]"
        error = "[!]"
        informative = "[i]"

    def get_display_message(self) -> str:
        """
        Gets a colorful version of the log entry
        :return: ASCII colored display message
        """
        base_format = "{0} {1: %d:%m:%Y %H:%M:%S} {2} | {3}"
        color_prefix = "\033[1;30;"

        if self.resultType == self.ResultType.informative:
            color_prefix += "44m"
        elif self.resultType == self.ResultType.error:
            color_prefix += "41m"
        elif self.resultType == self.ResultType.negative:
            color_prefix += "43m"
        elif self.resultType == self.ResultType.positive:
            color_prefix += "42m"

        return (color_prefix + base_format + '\x1b[0m').format(
            self.resultType, self.when, self.what, self.result
        )

    def get_message(self) -> str:
        """
        Gets a neutral string representing the log entry
        :return: The log entry as a string
        """
        return "[{0}] {1} {2} {3} {4} {5}".format(
            self.module, self.where, self.who, self.what, self.method,
            self.using
        )

    def __str__(self) -> str:
        """
        Overrides the tostring method
        :return: A displaystring representing the class
        """
        return self.get_message()


if __name__ == '__main__':
    log1 = LogEntryModel()

    log1.resultType = LogEntryModel.ResultType.informative

    log1.who = "Mies"
    log1.what = "Log testing"
    log1.method = "Testing"
    log1.using = "Logger"
    log1.result = "Log tested succesfully"

    print(LogEntryModel.create_logentry(
        LogEntryModel.ResultType.informative,
        "",
        "",
        "Test"
    )
    )

    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.negative
    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.error
    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.positive
    print(log1.get_display_message())
