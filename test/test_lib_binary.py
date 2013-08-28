from os.path import dirname, join
import virtualmachine

template = """
$jump_back = [_]
$return = [_]
$arg0 = [_]

MOV $arg0 {arg}
MOV $jump_back :return
JMP :{call}

return:
    DPRINT $return
    HALT
"""


def test_shift_left():
    asm_path = join(dirname(dirname(__file__)), 'lib', 'binary', 'shift.asm')
    asm = template.format(arg='{arg}', call='binary_shift_left')
    asm += open(asm_path).read()

    assert virtualmachine.run(asm.format(arg=10)) == '20'
    assert virtualmachine.run(asm.format(arg=1)) == '2'
    assert virtualmachine.run(asm.format(arg=0)) == '0'


def test_shift_right():
    asm_path = join(dirname(dirname(__file__)), 'lib', 'binary', 'shift.asm')
    asm = template.format(arg='{arg}', call='binary_shift_right')
    asm += open(asm_path).read()

    assert virtualmachine.run(asm.format(arg=255)) == '127'
    assert virtualmachine.run(asm.format(arg=2)) == '1'
    assert virtualmachine.run(asm.format(arg=1)) == '0'
    assert virtualmachine.run(asm.format(arg=0)) == '0'