from preprocessor import set_contents


SEPARATOR = ';'


def preprocessor_comments(lines):
    """
    Remove all comments from the source code.

    Example:

        ; Some comment
        HALT  ; Stop the execution

    Results in:

        HALT

    :type lines: list[Line]
    """
    for line in lines:
        contents = line.contents.strip()

        # Line comment, skip to next one
        if contents and contents[0] == ';':
            continue

        # Remove trailing comment
        contents = contents.split(SEPARATOR)[0].strip()

        if contents:
            yield set_contents(line, contents)
