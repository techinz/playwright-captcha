def split_kwargs(prefix: str, kwargs: dict) -> tuple:
    """
    Splits the kwargs into two dictionaries based on a given prefix

    :param prefix: The prefix to look for in the keys of kwargs
    :param kwargs: The keyword arguments to split

    :return: A tuple containing two dictionaries: the first with keys starting with the prefix, and the second with the remaining keys
    """

    separated_kwargs = {}

    for key in list(kwargs.keys()):
        if not key.startswith(prefix):
            continue

        separated_kwargs[key] = kwargs[key]
        del kwargs[key]

    return separated_kwargs, kwargs
