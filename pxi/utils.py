
from progressbar import progressbar


def progress(iterable, show=False):
    """
    Optionally wraps iterable in progress bar.

    Args:
        iterable: any iterable.
        show: whether of not to show a progress bar

    Returns:
        the iterable, wrapped in a progress bar if show is True
    """
    return progressbar(iterable) if show else iterable
