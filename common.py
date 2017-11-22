def list_part(lst, split_parts, *, start=None, end=None):
    """
    Return a part of list or tuple
    :param lst: list
    :param split_parts: number of parts for dividing lst
    :param start:
    :param end:
    :return: list
    """
    if start is not None:
        if start < 0 or start > split_parts:
            raise Warning('start should be between 0 and split_parts')
    if end is not None:
        if end < 0 or end > split_parts:
            raise Warning('end should be between 0 and split_parts')
    chunk = int(len(lst) / split_parts)
    return lst[start * chunk if start is not None else None:end * chunk if end is not None else None]
