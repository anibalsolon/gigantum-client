
# TODO: Finish exception implementation, with single exception used to manage hiding error details from user in UI
class GigantumException(Exception):
    """Any Exception arising from inside the Labbook class will be cast as a LabbookException.

    This is to avoid having "except Exception" clauses in the client code, and to avoid
    having to be aware of every sub-library that is used by the Labbook and the exceptions that those raise.
    The principle idea behind this is to have a single catch for all Labbook-related errors. In the stack trace you
    can still observe the origin of the problem."""
    pass


class GigantumLockedException(GigantumException):
    """ Raised when trying to acquire a Labbook lock when lock
    is already acquired by another process and failfast flag is set to
    True"""
    pass
