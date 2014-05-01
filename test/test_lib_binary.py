from os.path import dirname, join

import config
config.TESTING = True

from virtualmachine import VirtualMachine

template = """
$arg = [_]
MOV $arg {arg}
@call({call}, $arg)
DPRINT $return
HALT

#import {path}
"""


def test_shift_left():
    asm_path = join(dirname(dirname(__file__)), 'lib', 'binary', 'shift.asm')
    asm = template.format(arg='{arg}', call='binary_shift_left', path=asm_path)

    assert VirtualMachine().run(asm.format(arg=10)) == '20'
    assert VirtualMachine().run(asm.format(arg=1)) == '2'
    assert VirtualMachine().run(asm.format(arg=0)) == '0'


def test_shift_right():
    asm_path = join(dirname(dirname(__file__)), 'lib', 'binary', 'shift.asm')
    asm = template.format(arg='{arg}', call='binary_shift_right', path=asm_path)

    assert VirtualMachine().run(asm.format(arg=255)) == '127'
    assert VirtualMachine().run(asm.format(arg=2)) == '1'
    assert VirtualMachine().run(asm.format(arg=1)) == '0'
    assert VirtualMachine().run(asm.format(arg=0)) == '0'
