"""
Tiny-ASM preprocessor and assembler.

Supported instructions described at http://redd.it/1kqxz9.
"""

from helpers import neighborhood, flatten
from virtualmachine import MEMORY_SIZE

# Create type enum, fallback to ints
try:
    from enum import Enum
except ImportError:
    address = 0
    literal = 1
else:
    args = Enum('args', 'address literal')
    address = args.address
    literal = args.literal

DEBUG = False


def debug(*args):
    """
    Debug output
    """
    if DEBUG:
        print ('{} ' * len(args)).format(*args)


###############################################################################
# EXCEPTIONS
###############################################################################

class AssemblerException(Exception):
    pass


class AssemblerSyntaxError(AssemblerException):
    pass


class AssemblerNameError(AssemblerException):
    pass


class NoSuchConstantError(AssemblerException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'FATAL ERROR - No such constant: ' + self.name


class RedefinitionWarning(Warning, AssemblerNameError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'WARNING - Redefinition of $' + self.name


class RedefinitionError(Warning, AssemblerNameError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'FATAL ERROR - Redefinition of $' + self.name


###############################################################################
# THE INSTRUCTION DEFINITIONS
###############################################################################

instructions = {
    'AND': {
        # M[a] = M[a] bit-wise and M[b]
        # opcode | a | b:
        '0x00': (address, address),
        '0x01': (address, literal)
    },
    'OR': {
        # M[a] = M[a] bit-wise or M[b]
        # opcode | a | b:
        '0x02': (address, address),
        '0x03': (address, literal),
    },
    'XOR': {
        # M[a] = M[a] bit-wise xor M[b]
        # opcode | a | b:
        '0x04': (address, address),
        '0x05': (address, literal),
    },
    'NOT': {
        # M[a] = bit-wise not M[a]
        # opcode | a:
        '0x06': (address,),
    },
    'MOV': {
        # M[a] = M[b], or the literal-set M[a] = b
        # opcode | a | b:
        '0x07': (address, address),
        '0x08': (address, literal),
    },
    'RANDOM': {
        # M[a] = random value (0 to 25; equal probability distribution)
        # opcode | a:
        '0x09': (address,)
    },
    'ADD': {
        # M[a] = M[a] + b; no overflow support
        # opcode | a | b:
        '0x0A': (address, address),
        '0x0B': (address, literal),
    },
    'SUB': {
        # M[a] = M[a] - b; no underflow support
        # opcode | a | b:
        '0x0C': (address, address),
        '0x0D': (address, literal),
    },
    'JMP': {
        # Start executing at index of value M[a] or the literal a-value
        # opcode | a:
        '0x0E': (address,),
        '0x0F': (literal,)
    },
    'JZ': {
        # Start executing instructions at index x if M[a] == 0
        # opcode | x | a:
        '0x10': (address, address),
        '0x11': (address, literal),
        '0x12': (literal, address),
        '0x13': (literal, literal),
    },
    'JEQ': {
        # Jump to x or M[x] if M[a] is equal to M[b]
        # or if M[a] is equal to the literal b.
        # opcode | x | a | b:
        '0x14': (address, address, address),
        '0x15': (literal, address, address),
        '0x16': (address, address, literal),
        '0x17': (literal, address, literal),
    },
    'JLS': {
        # Jump to x or M[x] if M[a] is less than M[b]
        # or if M[a] is less than the literal b.
        # opcode | x | a | b:
        # opcode | x | a | b:
        '0x18': (address, address, address),
        '0x19': (literal, address, address),
        '0x1A': (address, address, literal),
        '0x1B': (literal, address, literal),
    },
    'JGT': {
        # Jump to x or M[x] if M[a] is greater than M[b]
        # or if M[a] is greater than the literal b
        # opcode | x | a | b:
        '0x1C': (address, address, address),
        '0x1D': (literal, address, address),
        '0x1E': (address, address, literal),
        '0x1F': (literal, address, literal),
    },
    'HALT': {
        # Halts the program / freeze flow of execution
        '0xFF': tuple()  # No args
    },
    'APRINT': {
        # Print the contents of M[a] in ASCII
        # opcode | a:
        '0x20': (address,),
        '0x21': (literal,)
    },
    'DPRINT': {
        # Print the contents of M[a] as decimal
        # opcode | a:
        '0x22': (address,),
        '0x23': (literal,)
    },
    'AREAD': {
        # Custom opcode:
        # Read one char from stdin and store the ASCII value at M[a]
        # opcode | a
        '0x24': (address,)
    }
}


###############################################################################
# THE PREPROCESSORS
###############################################################################

def preprocessor_include(lines):
    """
    Process include directives.

    Example:

    a.asm:
        APRINT '!'

    b.asm:
        #include a.asm
        HALT

    Results in:

        APRINT '!'
        HALT
    """
    # TODO: What about nested includes?
    # TODO: What about recursive includes?
    lines = list(lines)
    included = set()  # Files we already included

    while lines:
        # Take the first line from the stack
        line = lines.pop(0).strip()

        if line.startswith('#include'):
            path = line.split('#include')[1].strip()

            if not path in included:
                # Put the new contents to the top of the stack
                lines[0:0] = open(path).readlines()
                included.add(path)
        else:
            # No includes to process, yield the line
            yield line


def preprocessor_comments(lines, separator=';'):
    """
    Remove all comments from the source code.

    Example:

        ; Some comment
        HALT  ; Stop the execution

    Results in:

        HALT
    """
    for line in lines:
        line = line.strip()

        # Line comment, skip to next one
        if line and line[0] == ';':
            continue

        # Remove trailing comment
        line = line.split(separator)[0].strip()

        if line:
            yield line


def preprocessor_constants(lines):
    """
    Replaces constants usage with the defined vaule.

    Example:

        $const = 5
        MOV [2] $const

    Results in:

        MOV [2] 5
    """
    # TODO: Simplify

    constants = {}
    auto_mem = 0

    for lineno, line in enumerate(lines):
        tokens = []
        iterator = iter(line.split())
        is_assignment_line = False

        # Process all tokens in this line
        for token, next_token in neighborhood(iterator):
            if token[0] == '$':
                const_name = token[1:]

                if next_token == '=':
                    # Found assignment, store the associated value
                    is_assignment_line = True
                    value = iterator.next()

                    if value == '[_]':
                        # Process auto increment memory
                        if auto_mem >= MEMORY_SIZE:
                            raise AssemblerException(
                                'FATAL ERROR - [_]: No memory left!'
                            )

                        constants[const_name] = '[' + str(auto_mem) + ']'
                        auto_mem += 1

                    else:
                        # Usual constant
                        if const_name in constants:
                            raise RedefinitionWarning(const_name)

                        constants[const_name] = value

                else:
                    # Found usage of constant, replace with stored value
                    try:
                        tokens.append(constants[const_name])
                    except KeyError:
                        raise NoSuchConstantError(const_name)

            else:
                # Uninteresting token
                tokens.append(token)

        # Yield line if it's not an assignment
        if not is_assignment_line:
            debug('Constants:', constants)
            yield ' '.join(tokens)


def preprocessor_labels(lines):
    """
    Replace labels with the referenced instruction number.

    Example:

        label:
        GOTO :label

    Results in:

        GOTO 0

    """
    lines = list(lines)
    # Split lines to one big list of tokens
    tokens = flatten(line.split() for line in lines)
    labels = {}

    # Pass 1: Collect labels
    for index, token in enumerate(tokens):
        if token[-1] == ':':
            # Label definition
            label = token[:-1]

            if label in labels:
                raise NoSuchConstantError('Redefinition of ' + label + ':')

            labels[label] = index - len(labels)

    # Pass 2: Update references
    for line in lines:
        tokens = []

        for token in line.split():

            # Label usage
            if token[0] == ':':
                label_name = token[1:]

                try:
                    instruction_no = labels[label_name]
                except KeyError:
                    raise RedefinitionError('No such label: ' + label_name)

                tokens.append(str(instruction_no))

            # Label definitions
            elif token[-1] == ':':
                # Skip
                continue

            else:
                tokens.append(token)

        # If there any tokens left, yield them
        if tokens:
            debug('Labels:', labels)
            yield ' '.join(tokens)


def preprocessor_chars(lines):
    """
    Preprocess char constants.

    Example:

        APRINT 'A'
        APRINT '!'

    Results in:

        APRINT 65
        APRINT 33
    """

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

    is_char = lambda c: tok[0] == "'" and tok[-1] == "'"

    for line in lines:
        # Convert spaces before splitting!
        # Otherwise line.split() will result in a big mess
        line = line.replace("' '", str(ord(' ')))
        tokens = line.split()

        # Process chars
        tokens = [char_to_int(tok) if is_char(tok) else tok for tok in tokens]
        yield ' '.join(tokens)


###############################################################################
# The main function
###############################################################################

def assembler_to_hex(assembler_code, preprocessor_only=False):
    """
    Convert a assembler program to `Tiny` machine code.

    Opcodes described at http://redd.it/1kqxz9
    """

    # Define small, self-explaining helpers
    is_address = lambda s: s == '['
    get_arg_type = lambda t: address if is_address(t) else literal

    # Prepare token stream
    hexcode = []
    lines = assembler_code.splitlines()

    # Execute preprocessors
    preprocessors = (preprocessor_include, preprocessor_comments,
                     preprocessor_constants, preprocessor_labels,
                     preprocessor_chars)
    for pp in preprocessors:
        lines = list(pp(lines))

    if preprocessor_only:
        return '\n'.join(lines)

    # Process tokens
    for line in lines:
        iterator = iter(line.split())
        for token in iterator:
            debug('Processing token:', token)

            # Lookup token in instructions list
            instruction = instructions[token.upper()]
            debug('Instruction:', instruction)

            # Get arguments, look up arg count from first instruction
            num_args = len(instruction.values()[0])
            debug('Expected number of arguments:', num_args)

            arg_list = [iterator.next() for _ in range(num_args)]
            arg_types = [get_arg_type(arg[0]) for arg in arg_list]

            debug('Arguments:', arg_list)
            debug('Argument types:', arg_types)

            # Find matching instruction
            opcode = None
            for opc in instruction:
                # Check if the list of type arguments matches
                opcode_args = instruction[opc]
                if opcode_args == tuple(arg_types):
                    opcode = opc

            if opcode is None:
                raise AssemblerSyntaxError(
                    'Unknown argument types for instruction {} and '
                    'given arguments {}'.format(instruction, arg_types)
                )

            # Convert arguments to hex
            # 1. Strip '[ ]'
            arg_list = [arg.strip('[]') for arg in arg_list]
            # 3. Make ints
            arg_list = [hex(int(arg)) for arg in arg_list]

            # Create opcode string and store it
            opcode += ' ' + ' '.join(arg_list)
            opcode = opcode.strip()

            hexcode.append(opcode)

    return ' '.join(hexcode)

if __name__ == '__main__':
    import sys
    pp_only = sys.argv[1] == '--pp-only'
    filename = sys.argv[1] if not pp_only else sys.argv[2]

    try:
        print assembler_to_hex(
            open(filename).read(),
            preprocessor_only=pp_only
        )
    except Warning as w:
        print w
    except AssemblerException as e:
        print e
