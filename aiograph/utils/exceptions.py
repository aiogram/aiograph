# TODO: Find more error types


class TelegraphError(Exception):
    __subclasses = []
    match = None
    text = None

    def __init_subclass__(cls, match=None, **kwargs):
        super(TelegraphError, cls).__init_subclass__(**kwargs)
        if match is not None:
            cls.match = match.upper()
            cls.__subclasses.append(cls)

    @classmethod
    def detect(cls, description):
        """
        Automation detect error type.

        :param description:
        :raise: TelegramError
        """
        match = description.upper()
        for err in cls.__subclasses:
            if err is cls:
                continue
            if err.match in match:
                raise err(err.text or description)
        raise cls(description)


class NoFilesPassed(TelegraphError):
    def __init__(self):
        super(NoFilesPassed, self).__init__('No files has been uploaded.')


class AccessTokenInvalid(TelegraphError, match='ACCESS_TOKEN_INVALID'):
    text = 'Access token invalid!'


class FieldsFormatInvalid(TelegraphError, match='FIELDS_FORMAT_INVALID'):
    text = 'Fields format invalid!'


class UnknownMethod(TelegraphError, match='UNKNOWN_METHOD'):
    text = 'Unknown method!'
