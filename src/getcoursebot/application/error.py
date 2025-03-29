class ApplicationError(Exception):
    pass


class AlreadyExists(ApplicationError):
    pass


class AlreadyProcessMailing(ApplicationError):
    pass