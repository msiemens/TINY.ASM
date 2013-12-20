import os
import assembler


def test_trivial():
    assert assembler.assembler_to_hex('') == ''


def test_demo_input():
    assembler_code = """Mov [2] 0
Mov [3] 0
Jeq 6 [3] [1]
Add [3] 1
Add [2] [0]
Jmp 2
Mov [0] [2]
Halt"""
    expected_output = "0x08 0x2 0x0 0x08 0x3 0x0 0x15 0x6 0x3 0x1 0x0B 0x3 " \
                      "0x1 0x0A 0x2 0x0 0x0F 0x2 0x07 0x0 0x2 0xFF"

    assert assembler.assembler_to_hex(assembler_code) == expected_output


def test_preprocessor_comments():
    pp = assembler.preprocessor_comments

    assert list(pp(['; comment'])) == []
    assert list(pp(['MOV a b; comment'])) == ['MOV a b']


def test_preprocessor_variables():
    pp = assembler.preprocessor_constants

    assert list(pp(['$a = 5', 'MOV $a 3'])) == ['MOV 5 3']
    assert list(pp(['$a = 5', 'MOV 3 $a'])) == ['MOV 3 5']
    assert list(pp(['$a = [5]', 'Jeq 6 $a [1]'])) == ['Jeq 6 [5] [1]']

    # Auto-increment memory slots
    assert list(pp(['$a = [_]', 'MOV $a 1'])) == ['MOV [0] 1']


def test_preprocessor_labels():
    pp = assembler.preprocessor_labels

    assert list(pp(['label:', 'JMP :label'])) == ['JMP 0']


def test_preprocessor_chars():
    pp = assembler.preprocessor_chars

    assert list(pp([r"APRINT 'A'"])) == ['APRINT 65']
    assert list(pp([r"APRINT '\n'"])) == ['APRINT 10']
    assert list(pp([r"APRINT ' '"])) == ['APRINT 32']


def test_preprocessor_include(tmpdir):
    pp = assembler.preprocessor_include
    tmpdir.join('include.asm').write('MOV [1] 1\n#include include2.asm\nMOV '
                                     '[3] 1')
    tmpdir.join('include2.asm').write('MOV [2] 1')

    orig_wd = os.getcwd()
    tmpdir.chdir()

    assert list(pp(['MOV [0] 1', '#include include.asm'])) == ['MOV [0] 1',
                                                               'MOV [1] 1',
                                                               'MOV [2] 1',
                                                               'MOV [3] 1']
    os.chdir(orig_wd)
