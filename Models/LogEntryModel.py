from datetime import datetime


class LogEntryModel:
    """
    A class to represent log entries in a more flexible way. It displays entries
    using vibrant colours or as a more neutral string. It's primary function is
    to carry the information throughout the program.
    """
    # When the event happened
    when = datetime
    # Who started the event
    who: str
    # What's happening
    what: str
    # Why it's happening
    why: str
    # Where it happened
    where: str
    # What we're doing
    method: str
    # What we're using to archive the goal
    using: str
    # What the result is
    result: str
    # The module that created the instance.
    module: str
    # Whether the entry is information, an error or a negative or positive
    # result
    resultType: str

    def __init__(self):
        self.who = ""
        self.what = ""
        self.where = ""
        self.when = datetime.now()
        self.why = ""
        self.method = ""
        self.using = ""
        self.result = ""
        self.module = __class__.__name__
        self.resultType: LogEntryModel.ResultType.informative

    class ResultType:
        positive = "[+]"
        negative = "[-]"
        error = "[!]"
        informative = "[i]"

    def get_display_message(self):
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

        return (color_prefix + base_format).format(self.resultType, self.when,
                                                   self.what, self.result)

    def get_message(self):
        """
        Gets a neutral string representing the log entry
        :return: The log entry as a string
        """
        return "{0} - {1: %d:%m:%Y %H:%M:%S} {2} {3} {4} {5} {6} {7}".format(
            self.resultType, self.when, self.where, self.who, self.what,
            self.method, self.using, self.module
        )

    def __str__(self):
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

    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.negative
    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.error
    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.positive
    print(log1.get_display_message())
