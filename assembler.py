"""
Tiny-ASM preprocessor and assembler.

Supported instructions described at http://redd.it/1kqxz9.
"""
from exc import *
from helpers import debug, fatal_error
from opcodes import instructions, ADDRESS, LITERAL
from preprocessor import Line, preprocess


###############################################################################
# SMALL HELPERS
###############################################################################

def to_hex(s):
    try:
        return '0x%02x' % (int(s),)
    except ValueError:
        raise InvalidArgumentError('Not an hex integer: {}'.format(s))


def is_address(s):
    """ Check, wether the given argument represents an address """
    return s[0] == '['


def get_arg_type(t):
    """ Get the argument's type (ADDRESS or LITEAL) """
    return ADDRESS if is_address(t) else LITERAL


###############################################################################
# ASSEMBLER
###############################################################################

def assemble(code):
    """
    :type code: list[Line]
    """
    assert isinstance(code, list)

    hexcode = []

    for line in code:
        iterator = iter(line.contents.split())

        for mnem in iterator:
            debug('Processing token:', mnem)

            # Look up token in instructions list
            try:
                instruction = instructions[mnem.upper()]
            except KeyError:
                fatal_error('Unknown mnemonic: {}'.format(mnem),
                            UnknownMnemonicError, line)
            debug('Instruction:', instruction)

            # Get arguments, look up arg count from first opcode
            opcode_def = list(instruction.values())[0]
            num_args = len(opcode_def)
            debug('Expected number of arguments:', num_args)

            arg_list = [next(iterator) for _ in range(num_args)]
            arg_types = [get_arg_type(arg) for arg in arg_list]

            debug('Arguments:', arg_list)
            debug('Argument types:', arg_types)

            # Find matching instruction
            opcode = None
            for op in instruction:
                # Check if the list of type arguments matches
                opcode_args = instruction[op]
                if opcode_args == tuple(arg_types):
                    opcode = op

            if opcode is None:
                arg_str = ', '.join(t.name for t in arg_types)
                msg = 'Unknown argument types for mnemonic {} and ' \
                      'given arguments: {}'.format(mnem, arg_str)
                fatal_error(msg, AssemblerSyntaxError, line)

            # Convert arguments to hex
            # 1. Strip '[ ]'
            arg_list = [arg.strip('[]') for arg in arg_list]

            # 2. Convert to hex
            arg_list = [to_hex(arg) for arg in arg_list]
            debug('Arguments (hex):', arg_list)

            # Finally, create the opcode/hex string
            hexcode.append('{} {}'.format(opcode, ' '.join(arg_list)).strip())
            debug('')

    return ' '.join(hexcode)


def assembler_to_hex(source_code, filename=None, preprocessor_only=False):
    """
    Convert a assembler program to `Tiny` machine code.

    Opcodes described at http://redd.it/1kqxz9
    """

    code = preprocess(source_code, filename or '<input>')

    if preprocessor_only:
        return '\n'.join(c.contents for c in code)

    return assemble(code)


def main():
    import sys

    pp_only = sys.argv[1] == '--pp-only'
    filename = sys.argv[1] if not pp_only else sys.argv[2]

    try:
        print(assembler_to_hex(open(filename).read(), filename=filename,
                               preprocessor_only=pp_only))
    except Warning as w:
        print(w)
    except AssemblerException as e:
        print(e)


if __name__ == '__main__':
    main()
