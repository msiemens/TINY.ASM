from itertools import count

from config import MEMORY_SIZE
from exc import AssemblerException, RedefinitionWarning, NoSuchConstantError
from helpers import fatal_error, neighborhood, warn, debug
from preprocessor import set_contents


automem_counter = count()


def automem(line):
    counter = next(automem_counter)

    if counter >= MEMORY_SIZE:
        fatal_error('[_]: No more memory slots left!',
                    AssemblerException, line)

    return '[{}]'.format(counter)


def preprocessor_constants(lines):
    """
    Replaces constants usage with the defined vaule.

    Example:

        $const = 5
        MOV [2] $const

    Results in:

        MOV [2] 5

    :type lines: list[Line]
    """
    global automem_counter
    automem_counter = count()
    constants = {}

    for lineno, line in enumerate(lines):
        tokens = []
        iterator = iter(line.contents.split())
        is_assignment_line = False

        # Process all tokens in this line
        for token, next_token in neighborhood(iterator):
            if token[0] == '$':
                const_name = token[1:]

                if next_token == '=':
                    # Found assignment, store the associated value
                    is_assignment_line = True
                    value = next(iterator)

                    if const_name in constants:
                        warn('Redefined ${}'.format(const_name),
                             RedefinitionWarning, line)

                    if value == '[_]':
                        # Process auto increment memory
                        value = automem(line)

                    constants[const_name] = value

                else:
                    # Found usage of constant, replace with stored value
                    try:
                        tokens.append(constants[const_name])
                    except KeyError:
                        fatal_error('No such constant: ${}'.format(const_name),
                                    NoSuchConstantError, line)

            else:
                # Uninteresting token
                tokens.append(token)

        # Skip assignment lines
        if not is_assignment_line:
            debug('Constants:', constants)
            yield set_contents(line, ' '.join(tokens))
