from datetime import datetime


class LogEntryModel:
    when = datetime
    whom: str
    what: str
    why: str
    method: str
    using: str
    result: str
    module: str
    resultType: str

    def __init__(self):
        self.when = datetime.now()
        self.whom = ""
        self.what = ""
        self.why = ""
        self.method = ""
        self.using = ""
        self.result = ""
        self.module = ""
        self.resultType: self.ResultType.informative

    class ResultType:
        positive = "[+]"
        negative = "[-]"
        error = "[!]"
        informative = "[i]"

    def get_display_message(self):
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
        return "{0} - {1: %d:%m:%Y %H:%M:%S} ".format(
            self.resultType, self.when
        )


if __name__ == '__main__':
    log1 = LogEntryModel()

    log1.resultType = LogEntryModel.ResultType.informative

    log1.whom = "Mies"
    log1.what = "Log testing"
    log1.method = "Testing"
    log1.module = LogEntryModel.__class__.__name__
    log1.using = "Logger"
    log1.result = "Log tested succesfully"

    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.negative
    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.error
    print(log1.get_display_message())

    log1.resultType = LogEntryModel.ResultType.positive
    print(log1.get_display_message())
