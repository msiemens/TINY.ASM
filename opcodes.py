import random
import sys
from enum import Enum
from colors import green
from config import RAND_MAX


class ArgTypes(Enum):
    ADDRESS = 0
    LITERAL = 1

ADDRESS = ArgTypes.ADDRESS
LITERAL = ArgTypes.LITERAL


instructions = {
    'AND': {
        # M[a] = M[a] bit-wise and M[b]
        # opcode | a | b:
        '0x00': (ADDRESS, ADDRESS),
        '0x01': (ADDRESS, LITERAL)
    },
    'OR': {
        # M[a] = M[a] bit-wise or M[b]
        # opcode | a | b:
        '0x02': (ADDRESS, ADDRESS),
        '0x03': (ADDRESS, LITERAL),
    },
    'XOR': {
        # M[a] = M[a] bit-wise xor M[b]
        # opcode | a | b:
        '0x04': (ADDRESS, ADDRESS),
        '0x05': (ADDRESS, LITERAL),
    },
    'NOT': {
        # M[a] = bit-wise not M[a]
        # opcode | a:
        '0x06': (ADDRESS,),
    },
    'MOV': {
        # M[a] = M[b], or the LITERAL-set M[a] = b
        # opcode | a | b:
        '0x07': (ADDRESS, ADDRESS),
        '0x08': (ADDRESS, LITERAL),
    },
    'RANDOM': {
        # M[a] = random value (0 to 25; equal probability distribution)
        # opcode | a:
        '0x09': (ADDRESS,)
    },
    'ADD': {
        # M[a] = M[a] + b; no overflow support
        # opcode | a | b:
        '0x0A': (ADDRESS, ADDRESS),
        '0x0B': (ADDRESS, LITERAL),
    },
    'SUB': {
        # M[a] = M[a] - b; no underflow support
        # opcode | a | b:
        '0x0C': (ADDRESS, ADDRESS),
        '0x0D': (ADDRESS, LITERAL),
    },
    'JMP': {
        # Start executing at index of value M[a] or the LITERAL a-value
        # opcode | a:
        '0x0E': (ADDRESS,),
        '0x0F': (LITERAL,)
    },
    'JZ': {
        # Start executing instructions at index x if M[a] == 0
        # opcode | x | a:
        '0x10': (ADDRESS, ADDRESS),
        '0x11': (ADDRESS, LITERAL),
        '0x12': (LITERAL, ADDRESS),
        '0x13': (LITERAL, LITERAL),
    },
    'JEQ': {
        # Jump to x or M[x] if M[a] is equal to M[b]
        # or if M[a] is equal to the LITERAL b.
        # opcode | x | a | b:
        '0x14': (ADDRESS, ADDRESS, ADDRESS),
        '0x15': (LITERAL, ADDRESS, ADDRESS),
        '0x16': (ADDRESS, ADDRESS, LITERAL),
        '0x17': (LITERAL, ADDRESS, LITERAL),
    },
    'JLS': {
        # Jump to x or M[x] if M[a] is less than M[b]
        # or if M[a] is less than the LITERAL b.
        # opcode | x | a | b:
        # opcode | x | a | b:
        '0x18': (ADDRESS, ADDRESS, ADDRESS),
        '0x19': (LITERAL, ADDRESS, ADDRESS),
        '0x1A': (ADDRESS, ADDRESS, LITERAL),
        '0x1B': (LITERAL, ADDRESS, LITERAL),
    },
    'JGT': {
        # Jump to x or M[x] if M[a] is greater than M[b]
        # or if M[a] is greater than the literal b
        # opcode | x | a | b:
        '0x1C': (ADDRESS, ADDRESS, ADDRESS),
        '0x1D': (LITERAL, ADDRESS, ADDRESS),
        '0x1E': (ADDRESS, ADDRESS, LITERAL),
        '0x1F': (LITERAL, ADDRESS, LITERAL),
    },
    'HALT': {
        # Halts the program / freeze flow of execution
        '0xFF': tuple()  # No args
    },
    'APRINT': {
        # Print the contents of M[a] in ASCII
        # opcode | a:
        '0x20': (ADDRESS,),
        '0x21': (LITERAL,)
    },
    'DPRINT': {
        # Print the contents of M[a] as decimal
        # opcode | a:
        '0x22': (ADDRESS,),
        '0x23': (LITERAL,)
    },
    'AREAD': {
        # Custom opcode:
        # Read one char from stdin and store the ASCII value at M[a]
        # opcode | a
        '0x24': (ADDRESS,)
    }
}

opcodes = dict(
    [
        (opcode, mnem)
        for mnem in instructions  # Outer loop
        for opcode in instructions[mnem]  # Inner loop
    ]
)


###############################################################################
# INSTRUCTIONS
###############################################################################
# Every instruction is derivated from the Instruction class. It needs to
# overwrite the __call__ operator. The required argument's types are declared
# using annotations. If the instructions sets memory or does a jump, it's
# return is annotated using the ReturnValue class.

class ReturnValue(Enum):
    DATA = 0  # Returns: register, data
    JUMP = 1  # Returns: destination or None


class Instruction(object):
    def __init__(self, vm):
        #: :type: VirtualMachine
        self.vm = vm

    def __call__(self, *args):
        raise NotImplementedError()


###############################################################################
# Binary operator instructions

class BinaryOpInstruction(Instruction):
    def operator(self, a, b):
        raise NotImplementedError()

    def __call__(self, dest: ADDRESS, arg: LITERAL) -> ReturnValue.DATA:
        # dest = [dest] (op) arg
        result = self.operator(self.vm.mem_read(dest), arg)
        return dest, result


class AndInstruction(BinaryOpInstruction):
    def operator(self, a, b):
        return a & b


class OrInstruction(BinaryOpInstruction):
    def operator(self, a, b):
        return a | b


class XorInstruction(BinaryOpInstruction):
    def operator(self, a, b):
        return a ^ b


class NotInstruction(Instruction):
    def __call__(self, a) -> ReturnValue.DATA:
        return a, ~ a


###############################################################################
# Memory modification

class MovInstruction(Instruction):
    def __call__(self, x: ADDRESS, a: LITERAL) -> ReturnValue.DATA:
        return x, a


class RandomInstruction(Instruction):
    def __call__(self, a: ADDRESS) -> ReturnValue.DATA:
        return a, random.randint(0, RAND_MAX)


###############################################################################
# Arithmetics instructions

class ArithmeticalInstruction(BinaryOpInstruction):
    pass


class AddInstruction(ArithmeticalInstruction):
    def operator(self, a, b):
        return a + b


class SubInstruction(ArithmeticalInstruction):
    def operator(self, a, b):
        return a - b


###############################################################################
# Jump instructions

class JumpInstruction(Instruction):
    pass


class JmpInstruction(JumpInstruction):
    def __call__(self, a: LITERAL) -> ReturnValue.JUMP:
        return a


class JzInstruction(Instruction):
    def __call__(self, x: ADDRESS, a: LITERAL) -> ReturnValue.JUMP:
        return x if a == 0 else None


class ConditionalJumpInstruction(JumpInstruction):
    def test(self, a, b):
        pass

    def __call__(self, x: LITERAL, a: LITERAL, b: LITERAL) -> ReturnValue.JUMP:
        if self.test(a, b):
            return x


class JeqInstruction(ConditionalJumpInstruction):
    def test(self, a, b):
        return a == b


class JlsInstruction(ConditionalJumpInstruction):
    def test(self, a, b):
        return a < b


class JgtInstruction(ConditionalJumpInstruction):
    def test(self, a, b):
        return a > b


###############################################################################
# Other instructions

class HaltInstruction(Instruction):
    def __call__(self):
        self.vm.halt()


class PrintInstruction(Instruction):
    def convert(self, a):
        raise NotImplementedError()

    def __call__(self, a: LITERAL):
        s = str(self.convert(a))

        self.vm.output.write(s)
        sys.stdout.write(green(s))


class AprintInstruction(PrintInstruction):
    def convert(self, a):
        return chr(int(a))


class DprintInstruction(PrintInstruction):
    def convert(self, a):
        return int(a)


__all__ = ['LITERAL', 'ADDRESS', 'instructions', 'opcodes', 'ReturnValue']
__all__ += [m for m in dir() if m.endswith('Instruction')]
