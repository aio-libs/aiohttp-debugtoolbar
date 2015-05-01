# TODO: remove somehow
def text_(s, encoding='latin-1', errors='strict'):
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    return s  # pragma: no cover
