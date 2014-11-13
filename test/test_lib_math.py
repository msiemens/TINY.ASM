from os.path import dirname, join

import config
config.TESTING = True

from virtualmachine import VirtualMachine

template = """
MOV $arg0 {arg0}
MOV $arg1 {arg1}
@call({call}, $arg0, $arg1)
DPRINT $return
HALT

#import {path}
"""


def test_multiply():
    asm_path = join(dirname(dirname(__file__)), 'lib', 'math', 'multiply.asm')
    asm = template.format(arg0='{arg0}', arg1='{arg1}', call='math_multiply',
                          path=asm_path)
    # asm += open(asm_path).read()

    print(asm)

    assert VirtualMachine().run(asm.format(arg0=10, arg1=2)) == '20'
    assert VirtualMachine().run(asm.format(arg0=5, arg1=7)) == '35'
    assert VirtualMachine().run(asm.format(arg0=25, arg1=10)) == '250'
    assert VirtualMachine().run(asm.format(arg0=10, arg1=25)) == '250'


def test_divide():
    asm_path = join(dirname(dirname(__file__)), 'lib', 'math', 'divide.asm')
    asm = template.format(arg0='{arg0}', arg1='{arg1}', call='math_divide',
                          path=asm_path)

    assert VirtualMachine().run(asm.format(arg0=10, arg1=2)) == '5'
    assert VirtualMachine().run(asm.format(arg0=5, arg1=7)) == '0'
    assert VirtualMachine().run(asm.format(arg0=25, arg1=25)) == '1'
    assert VirtualMachine().run(asm.format(arg0=10, arg1=1)) == '10'
