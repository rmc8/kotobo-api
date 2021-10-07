class KotoboConnectionError(Exception):
    pass


class KotoboTooManyRequestsError(Exception):
    pass


class KotoboNotLoginException(Exception):
    pass


class KotoboUndefinedCategoryException(Exception):
    pass