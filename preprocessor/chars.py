from preprocessor import set_contents


def is_char(c):
    """
    Wether the given token is a char definition
    """
    return c[0] == "'" and c[-1] == "'"


def char_to_int(c):
    """
    Convert a char constant to the ASCII integer
    """
    if len(c) == 4 and c[1] == '\\':
        # Special character! Use eval to transform '\\n' to '\n'
        # and then ord() to convert it to int
        return str(ord(eval(c)))
    else:
        # Convert to int using ord()
        return str(ord(c[1:-1]))


def preprocessor_chars(lines):
    """
    Preprocess char constants.

    Example:

        APRINT 'A'
        APRINT '!'

    Results in:

        APRINT 65
        APRINT 33

    :type lines: list[Line]
    """

    for line in lines:
        contents = line.contents

        # Convert spaces before splitting!
        # Otherwise line.split() will result in a big mess
        contents = contents.replace("' '", str(ord(' ')))
        tokens = contents.split()

        # Process chars
        tokens = [char_to_int(tok) if is_char(tok) else tok for tok in tokens]
        yield set_contents(line, ' '.join(tokens))
