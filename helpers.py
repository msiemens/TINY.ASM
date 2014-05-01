import inspect
import sys
from collections import OrderedDict

from colors import red, yellow, magenta

from config import TESTING, DEBUG


def debug(*args):
    """
    Debug output
    """
    if DEBUG:
        print(magenta(('{} ' * len(args)).format(*args)))


def neighborhood(iterable):
    """
    Yield the list as (item, next item).
    """
    iterator = iter(iterable)
    item = next(iterator)  # throws StopIteration if empty.

    for _next in iterator:
        yield (item, _next)
        item = _next

    yield (item, None)


def get_ordered_annotations(func):
    """
    Get annotations for function as an OrderedDict
    """
    annotations = OrderedDict()
    signature = inspect.signature(func)
    for parameter in signature.parameters.values():
        annotations[parameter.name] = parameter.annotation

    if signature.return_annotation != signature.empty:
        annotations['return'] = signature.return_annotation

    return annotations


###############################################################################
# ERROR HANDLING
###############################################################################

# FIXME: Unify

def fatal_error(msg, exc_class, line=None, exit_func=lambda: sys.exit(1)):
    if TESTING:
        raise exc_class(msg) from None
    else:
        if line:
            msg = line_error(msg, line)

        print(red('FATAL ERROR:'), msg)
        exit_func()


def syntax_error(msg, exc_class, line=None, exit_func=lambda: sys.exit(1)):
    if TESTING:
        raise exc_class(msg) from None
    else:
        if line:
            msg = line_error(msg, line)

        print(red('SYNTAX ERROR:'), msg)
        exit_func()


def warn(msg, exc_class, line=None):
    if TESTING:
        raise exc_class(msg) from None
    else:
        if line:
            msg = line_error(msg, line)
        print(yellow('WARNING:'), msg)


def line_error(msg, line):
    """
    :type line: Line
    """
    return '{}\n\nIn {}\n{:02}  {}'.format(
        msg, line.filename, line.lineno + 1, line.original_contents,
    )
