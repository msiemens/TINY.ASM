"""
Tiny-ASM preprocessor and assembler.

Supported instructions described at http://redd.it/1kqxz9.
"""

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

def neighborhood(iterable):
    """
    Yield the list as (item, next item).
    """
    iterator = iter(iterable)
    item = iterator.next()  # throws StopIteration if empty.

    for _next in iterator:
        yield (item, _next)
        item = _next

    yield (item, None)


def preprocessor_include(lines):
    """
    Process include directives.
    """
    lines = list(lines)
    included = set()

    while lines:
        line = lines.pop(0).strip()

        if line.startswith('#include'):
            path = line.split('#include')[1].strip()
            if not path in included:
                lines[0:0] = open(path).readlines()
                included.add(path)
        else:
            yield line


def preprocessor_comments(lines, separator=';'):
    """
    Remove all comments from the source code.
    """
    for line in lines:
        line = line.strip()
        if line and line[0] == ';':
            continue

        line = line.split(separator)[0].strip()
        if line:
            yield line


def preprocessor_constants(lines):
    """
    Replaces constants usage with the defined vaule.
    """
    constants = {}
    auto_mem = 0

    for lineno, line in enumerate(lines):
        tokens = []
        iterator = iter(line.split())
        assignment_line = False

        # Process all tokens in this line
        for token, next_token in neighborhood(iterator):
            if token[0] == '$':
                const_name = token[1:]

                if next_token == '=':
                    # Found assignment, store the associated value
                    assignment_line = True
                    value = iterator.next()

                    if value == '[_]':
                        if auto_mem >= MEMORY_SIZE:
                            raise AssemblerException(
                                'FATAL ERROR - [_]: No memory left!'
                            )

                        constants[const_name] = '[' + str(auto_mem) + ']'
                        auto_mem += 1
                    else:
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

        # Skip assignment lines, yield other lines
        if not assignment_line:
            # print 'Constants:', constants
            yield ' '.join(tokens)


def preprocessor_labels(lines):
    """
    Replace labels with the referenced instruction number.
    """
    lines = list(lines)
    tokens = []
    labels = {}

    # Split up lines to one big list of tokens
    for line in lines:
        tokens.extend(line.split())

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
            if token[0] == ':':
                label_name = token[1:]
                try:
                    instruction_no = labels[label_name]
                except KeyError:
                    raise RedefinitionError('No such label: ' + label_name)
                tokens.append(str(instruction_no))
            elif token[-1] == ':':
                # Remove label definitions
                continue
            else:
                tokens.append(token)

        if tokens:
            # print 'Labels:', labels
            yield ' '.join(tokens)


def preprocessor_chars(lines):
    def char_to_int(c):
        if len(c) == 4 and c[1] == '\\':
            # Special character. Use eval to transform '\\n' to '\n'
            return str(ord(eval(c)))
        else:
            # Other character
            return str(ord(c[1:-1]))

    is_char = lambda c: tok[0] == "'" and tok[-1] == "'"

    for line in lines:
        # Replace spaces before splitting
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
    # print 'Tokenized input:', tokens

    # Run preprocessors
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
            # print 'Processing token:', token

            # Lookup token in instructions list
            instruction = instructions[token.upper()]
            # print 'Instruction:', instruction

            # Get arguments, look up arg count from first instruction
            num_args = len(instruction.values()[0])
            # print 'Expected number of arguments:', num_args

            arg_list = [iterator.next() for _ in range(num_args)]
            arg_types = [get_arg_type(arg[0]) for arg in arg_list]

            # print 'Arguments:', arg_list
            # print 'Argument types:', arg_types

            # Find matching instruction
            opcode = None
            for _opcode in instruction:
                # Check if the list of type arguments matches
                opcode_args = instruction[_opcode]
                if opcode_args == tuple(arg_types):
                    opcode = _opcode

            if opcode is None:
                raise AssemblerSyntaxError(
                    'Unknown argument types for instruction {} and '
                    'given arguments {}'.format(instruction, arg_types)
                )

            # Convert arguments to hex
            # 1. Strip '[ ]'
            arg_list = [arg.strip('[]') for arg in arg_list]
            # 3. Make ints
            arg_list = [int(arg) for arg in arg_list]
            # 4. Make hex
            # Use % operator, because using hex() would result in 0x1 instead
            # of 0x01
            arg_list = ['0x' + ('%02X' % arg).upper() for arg in arg_list]

            # Create opcode string and store it
            opcode += ' ' + ' '.join(arg_list)
            opcode = opcode.strip()

            hexcode.append(opcode)

    return '\n'.join(hexcode)

if __name__ == '__main__':
    import sys
    pp_only = sys.argv[1] == '--pp-only'
    filename = sys.argv[1] if not pp_only else sys.argv[2]

    try:
        print assembler_to_hex(open(filename).read(), preprocessor_only=pp_only)
    except Warning as w:
        print w
    except AssemblerException as e:
        print e
