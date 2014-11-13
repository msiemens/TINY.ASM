###############################################################################
# IMPORTS
###############################################################################

from io import StringIO
from timeit import default_timer as timer

import colorama

import assembler
from exc import VirtualRuntimeError, MissingHaltError
from opcodes import *
from config import MEMORY_SIZE, MAX_INT, DEBUG, TESTING
from helpers import get_ordered_annotations, fatal_error


colorama.init()


###############################################################################
# SMALL HELPERS
###############################################################################

# Convert an int to uint8, ensuring it's not larger than WORD_SIZE
to_uint = lambda i: i % MAX_INT

# Check, if the given string represents an address
is_address = lambda s: hasattr(s, '__getitem__') and s[0] == '['

# Check, if the given string represents an integer literal
is_literal = lambda s: not is_address(s)

# Get an argument's type
get_arg_type = lambda t: ADDRESS if is_address(t) else LITERAL


def get_annotations(instance):
    try:
        func = instance.__call__
    except AttributeError:
        return {}
    return get_ordered_annotations(func)


###############################################################################
# THE VIRTUALMACHINE CLASS
###############################################################################

class VirtualMachine(object):
    def __init__(self):
        self.testing = TESTING
        self.debug = DEBUG

        self.tokens = None

        self.memory = [0] * MEMORY_SIZE
        self.running = True
        self.instr_pointer = 0
        self.prev_instr_pointer = 0
        self.ticks = 0
        self.jumping = False
        self.output = StringIO()

    #: :type: dict[str, Instruction]
    instructions = {
        'AND': AndInstruction,
        'OR': OrInstruction,
        'XOR': XorInstruction,
        'NOT': NotInstruction,
        'MOV': MovInstruction,
        'RANDOM': RandomInstruction,
        'ADD': AddInstruction,
        'SUB': SubInstruction,
        'JMP': JmpInstruction,
        'JZ': JzInstruction,
        'JEQ': JeqInstruction,
        'JLS': JlsInstruction,
        'JGT': JgtInstruction,
        'HALT': HaltInstruction,
        'APRINT': AprintInstruction,
        'DPRINT': DprintInstruction,
        'AREAD': lambda m: (m, ord(sys.stdin.read(1)))
    }

    ###########################################################################
    # SMALL HELPERS
    ###########################################################################

    def debug(self, msg):
        if self.debug:
            print(msg)

    def mem_store(self, dest, arg):
        """ Store arg in dest. """
        self.memory[dest] = to_uint(arg)

    def mem_read(self, m):
        """ Read from a memory address. """
        return self.memory[m]

    def instr_jump(self, dest):
        """ Move the instruction pointer to dest. """
        assert dest is not None, 'Tried to jump to None'

        if self.prev_instr_pointer == dest:
            fatal_error('Stuck in infinite loop!', VirtualRuntimeError)

        self.prev_instr_pointer = self.instr_pointer

        self.instr_pointer = dest
        self.jumping = True

    def halt(self):
        """ Stop the execution. """
        if self.testing:
            self.running = False
        else:
            sys.exit(1)

    ###########################################################################
    # PROCESSING HELPERS
    ###########################################################################

    def process_arg(self, i, annotations, opcode):
        """
        Process an instruction's argument.
        """
        mnem = opcodes[opcode]
        arg_type = instructions[mnem][opcode][i]
        arg = self.tokens[self.instr_pointer + i + 1]

        # Transform literals to ints
        arg = int(arg, 0)

        # Some instructions allow a parameter to be an address OR an literal
        # but the implementation requires a literal. In this case, we need
        # to pass the memory content instead of the address.
        required_arg_type = list(annotations.values())[i]

        if arg_type == ADDRESS and required_arg_type == LITERAL:
            arg = self.mem_read(arg)

        return arg

    def process_return_value(self, return_type, return_value):
        """
        Process the return value of an instruction.
        """
        if return_value is not None:

            # Interpret return value as jump destination
            if return_type == ReturnValue.JUMP:
                self.instr_jump(return_value)

            # Interpret as memory pointer and content
            elif return_type == ReturnValue.DATA:
                dest, value = return_value
                self.mem_store(dest, value)

    ###########################################################################
    # THE RUN METHOD
    ###########################################################################

    def run(self, asm, filename=None, preprocess=True):
        start = timer()

        # Tokenize code
        if preprocess:
            self.tokens = assembler.assembler_to_hex(asm, filename)

        self.tokens = self.tokens.split()

        # Main loop
        while self.running:
            self.jumping = False

            # Check bounds of instr_pointer
            if self.instr_pointer >= len(self.tokens):
                fatal_error('Reached end of code without seeing HALT',
                            MissingHaltError, exit_func=self.halt)

            # Get current opcode
            opcode = self.tokens[self.instr_pointer]
            mnem = opcodes[opcode].upper()

            if self.debug:
                print('Instruction: {} ({})'.format(mnem, opcode))

            # Look up instruction
            instruction_class = self.instructions[mnem]
            instruction = instruction_class(self)
            instruction_spec = instructions[mnem]
            annotations = get_annotations(instruction)

            # Look up number of arguments
            num_args = len(list(instruction_spec.values())[0])

            if self.debug:
                print('Number of args:', num_args)
                print('Argument spec:', instruction_spec[opcode])

            # Collect arguments
            if num_args:
                try:
                    args = [self.process_arg(i, annotations, opcode)
                            for i in range(num_args)]
                except IndexError:
                    msg = 'Unexpectedly reached EOF. Maybe an argument is ' \
                          'missing or a messed up jump occured'
                    fatal_error(msg, VirtualRuntimeError, exit_func=self.halt)
            else:
                args = []

            if self.debug:
                print('Arguments:', args)

            # Run instruction
            return_value = instruction(*args)

            # Process return value
            try:
                return_type = annotations['return']
            except KeyError:
                return_type = None
            self.process_return_value(return_type, return_value)

            # Increase counters
            self.ticks += 1
            if not self.jumping:
                self.prev_instr_pointer = self.instr_pointer
                self.instr_pointer += 1  # Skip current opcode
                self.instr_pointer += num_args  # Skip arguments

            if self.debug:
                print('Memory:', self.memory)
                print()
                print()

        if self.debug:
            print()
            print('Exited after {} ticks in {:.5}s'.format(self.ticks,
                                                           timer() - start))

        return self.output.getvalue()


def main():
    filename = sys.argv[1]
    VirtualMachine().run(open(filename).read(), filename)

if __name__ == '__main__':
    main()
