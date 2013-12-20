from itertools import chain

def neighborhood(iterable):
    """
    Yield the list as (item, next item).
    """
    iterator = iter(iterable)
    item = iterator.next()  # throws StopIteration if empty.

    for _next in iterator:
        yield (item, _next)
        item = _next

    yield (item, None)


def flatten(l):
    return list(chain.from_iterable(l))

