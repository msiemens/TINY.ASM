from os.path import dirname, join
import virtualmachine

template = """
$jump_back = [_]
$return = [_]
$arg0 = [_]
$arg1 = [_]

MOV $arg0 {arg0}
MOV $arg1 {arg1}
MOV $jump_back :return
JMP :{call}

return:
    DPRINT $return
    HALT
"""


def test_multiply():
    asm_path = join(dirname(dirname(__file__)), 'lib', 'math', 'multiply.asm')
    asm = template.format(arg0='{arg0}', arg1='{arg1}', call='math_multiply')
    asm += open(asm_path).read()

    assert virtualmachine.run(asm.format(arg0=10, arg1=2)) == '20'
    assert virtualmachine.run(asm.format(arg0=5, arg1=7)) == '35'
    assert virtualmachine.run(asm.format(arg0=25, arg1=10)) == '250'
    assert virtualmachine.run(asm.format(arg0=10, arg1=25)) == '250'


def test_divide():
    asm_path = join(dirname(dirname(__file__)), 'lib', 'math', 'divide.asm')
    asm = template.format(arg0='{arg0}', arg1='{arg1}', call='math_divide')
    asm += open(asm_path).read()

    assert virtualmachine.run(asm.format(arg0=10, arg1=2)) == '5'
    assert virtualmachine.run(asm.format(arg0=5, arg1=7)) == '0'
    assert virtualmachine.run(asm.format(arg0=25, arg1=25)) == '1'
    assert virtualmachine.run(asm.format(arg0=10, arg1=1)) == '10'
