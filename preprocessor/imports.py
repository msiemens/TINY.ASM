from helpers import fatal_error
from preprocessor import Line


def read_file(path):
    try:
        return open(path).readlines()
    except UnicodeDecodeError:
        return open(path, encoding='utf-8').readlines()


def preprocessor_import(lines):
    """
    Process import directives.

    Example:

    a.asm:
        APRINT '!'

    b.asm:
        #include a.asm
        HALT

    Results in:

        APRINT '!'
        HALT

    Note: A file will be imported only once. A file cannot import the importing
    file.

    :type lines: list[Line]
    """
    lines = list(lines)
    included = set()  # Files we already included

    while lines:
        # Take the first line from the stack
        line = lines.pop(0)
        contents = line.contents.strip()

        if contents.startswith('#import'):
            path = contents.split('#import')[1].strip()

            if path not in included:
                # Put the new contents to the top of the stack
                to_include = None
                try:
                    to_include = read_file(path)
                except FileNotFoundError:
                    fatal_error('File not found: {}'.format(path),
                                FileNotFoundError, line)

                # Insert lines into the current position
                lines[0:0] = [Line(i, path, l.strip(), l.strip())
                              for i, l in enumerate(to_include)]
                included.add(path)
        else:
            # No includes to process, yield the line
            yield line
