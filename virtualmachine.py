###############################################################################
# IMPORTS
###############################################################################

import sys
import random
from cStringIO import StringIO
from timeit import default_timer as timer

try:
    from enum import Enum
except ImportError:
    ADDRESS = 0
    LITERAL = 1
else:
    args = Enum('args', 'address literal')
    ADDRESS = args.address
    LITERAL = args.literal

###############################################################################
# CONSTANTS
###############################################################################

WORD_SIZE = 8
MAX_INT = 2 ** WORD_SIZE
MEMORY_SIZE = 2 ** WORD_SIZE
RAND_MAX = 25

# WORD_SIZE = 32
# MAX_INT = 2 ** WORD_SIZE
# MEMORY_SIZE = 256
# RAND_MAX = 255


###############################################################################
# RUNTIME VARIABLES
###############################################################################

def init():
    global memory, running, instr_pointer, ticks, jumping, output
    memory = [0] * MEMORY_SIZE
    running = True
    instr_pointer = 0
    ticks = 0
    jumping = False
    output = StringIO()


###############################################################################
# SMALL HELPERS
###############################################################################

# Convert an int to uint8, ensuring it's not larger than WORD_SIZE
to_uint = lambda i: i % MAX_INT

# Check, if the given string represents an address
is_address = lambda s: hasattr(s, '__getitem__') and s[0] == '['

# Check, if the given string represents an integer literal
is_literal = lambda s: not is_address(s)

# Get the type of the argument
get_arg_type = lambda t: ADDRESS if is_address(t) else LITERAL

# Get the address from an address string
get_address = lambda x: int(x[1:-1])

# Get the value. Addresses will resolve to the memory content.
get_value = lambda m: memory[get_address(m)] if is_address(m) else m


def assert_address(x):
    assert is_address(x), '{} is not an address!'.format(x)


def assert_literal(x):
    assert not is_address(x), '{} is not a literal!'.format(x)


def mem_store(dest, arg):
    """ Store arg in dest. """
    memory[get_address(dest)] = to_uint(get_value(arg))


def instr_jump(dest):
    """ Move the instruction pointer to dest. """
    global instr_pointer, jumping
    # print 'JUMPING from {} to {}'.format(instr_pointer, to)
    instr_pointer = dest
    jumping = True


def halt():
    """ Stop the execution. """
    global running
    # print 'HALTING'
    running = False


###############################################################################
# INSTRUCTION DEFINITIONS
###############################################################################

def instruction_logical(op):
    """ Calculate the new vaule using op and store in dest. """
    def operation(dest, arg):
        assert_address(dest)
        result = op(get_value(dest), get_value(arg))
        mem_store(dest, result)

    return operation

instruction_arithmetical = instruction_logical


def instruction_jump_conditional(cmp):
    """ Jump to x if cmp(a, b) returns True. """
    def operation(x, a, b):
        assert_address(a)
        if cmp(get_value(a), get_value(b)):
            instr_jump(x)

    return operation


def instruction_print(a):
    """ Print to stdout. """
    output.write(str(a))
    sys.stdout.write(str(a))


instructions = {
    'AND': instruction_logical(lambda a, b: a & b),
    'OR': instruction_logical(lambda a, b: a | b),
    'XOR': instruction_logical(lambda a, b: a ^ b),
    'NOT': lambda a: mem_store(a, ~ a),
    'MOV': lambda x, a: mem_store(x, get_value(a)),
    'RANDOM': lambda a: mem_store(a, random.randint(0, RAND_MAX)),
    'ADD': instruction_arithmetical(lambda a, b: a + b),
    'SUB': instruction_arithmetical(lambda a, b: a - b),
    'JMP': lambda a: instr_jump(get_value(a)),
    'JZ': lambda x, a: instr_jump(get_value(x)) if get_value(a) == 0 else None,
    'JEQ': instruction_jump_conditional(lambda a, b: a == b),
    'JLS': instruction_jump_conditional(lambda a, b: a < b),
    'JGT': instruction_jump_conditional(lambda a, b: a > b),
    'HALT': halt,
    'APRINT': lambda a: instruction_print(chr(int(get_value(a)))),
    'DPRINT': lambda a: instruction_print(int(get_value(a))),
    'DEBUG': lambda: None
}


###############################################################################
# MAIN LOOP
###############################################################################

def run(asm):
    init()
    import assembler
    start = timer()

    global ticks, instr_pointer, jumping
    tokens = assembler.assembler_to_hex(asm, preprocessor_only=True)
    tokens = tokens.split()

    while running:
        jumping = False
        # print 'Ticks:', ticks
        # ctx_pre = ' '.join(tokens[instr_pointer - 5:instr_pointer])
        # ctx_post = ' '.join(tokens[instr_pointer + 1:instr_pointer + 6])
        # print 'Ctx:', ctx_pre, ':::', tokens[instr_pointer], ':::', ctx_post
        # print 'Pointer:', instr_pointer
        # print 'Memory:', memory
        opcode = tokens[instr_pointer]
        # print 'Instruction:', opcode

        # Look up number of arguments
        num_args = len(assembler.instructions[opcode].values()[0])
        # print 'Number of args:', num_args

        if num_args:
            # Read arguments
            args = [tokens[instr_pointer + i + 1] for i in range(num_args)]
            # Transform to ints
            args = [int(arg) if is_literal(arg) else arg for arg in args]
            # print 'Arguments:', ' '.join(str(a) for a in args)
        else:
            args = []

        # Run instruction
        instructions[opcode](*args)

        # Increase counters
        ticks += 1
        if not jumping:
            instr_pointer += 1 + num_args

        # print
    # print
    # print 'Exited after {} ticks in {:.5}s'.format(ticks, timer() - start)

    return output.getvalue()

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    run(open(filename).read())