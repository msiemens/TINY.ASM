import os
from pprint import pprint

import pytest

import config
config.TESTING = True

import assembler
import preprocessor
from exc import UnknownMnemonicError, InvalidArgumentError, RedefinitionError,\
    RedefinitionWarning, NoSuchConstantError, NoSuchLabelError,\
    AssemblerException, AssemblerSyntaxError
from preprocessor import prepare_source_code


def prep(func):
    def run(code):
        code = func(prepare_source_code('<test>', '\n'.join(code)))
        return [c.contents for c in code]

    return run


def test_to_hex():
    assert assembler.to_hex(0) == '0x00'
    assert assembler.to_hex(15) == '0x0f'
    assert assembler.to_hex(255) == '0xff'


def test_get_arg_type():
    assert assembler.get_arg_type('[1]') == assembler.ADDRESS
    assert assembler.get_arg_type('1') == assembler.LITERAL


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
    expected_output = "0x08 0x02 0x00 0x08 0x03 0x00 0x15 0x06 0x03 0x01 " \
                      "0x0B 0x03 0x01 0x0A 0x02 0x00 0x0F 0x02 0x07 0x00 " \
                      "0x02 0xFF"
    asm = assembler.assembler_to_hex(assembler_code)

    print(expected_output)
    print(asm)

    assert asm == expected_output


def test_unknown_instruction():
    with pytest.raises(UnknownMnemonicError):
        assembler.assembler_to_hex('HEY')


def test_invalid_argument():
    with pytest.raises(InvalidArgumentError):
        assembler.assembler_to_hex('JMP a')


def test_redefinition_label():
    with pytest.raises(RedefinitionError):
        assembler.assembler_to_hex('lbl:\nlbl:\nHALT')


def test_redefinition_const():
    with pytest.raises(RedefinitionWarning):
        assembler.assembler_to_hex('$a = 1\n$a = 1\nHALT')

    with pytest.raises(RedefinitionWarning):
        assembler.assembler_to_hex('$a = [_]\n$a = [_]\nHALT')


def test_no_such_const():
    with pytest.raises(NoSuchConstantError):
        assembler.assembler_to_hex('MOV $a 1')


def test_no_such_label():
    with pytest.raises(NoSuchLabelError):
        assembler.assembler_to_hex('JMP :lbl')


def test_no_memory_left():
    with pytest.raises(AssemblerException):
        s = ['${} = [_]'.format(i) for i in range(config.MEMORY_SIZE + 1)]
        assembler.assembler_to_hex('\n'.join(s))


def test_invalid_args():
    with pytest.raises(AssemblerSyntaxError):
        assembler.assembler_to_hex('MOV 0 0')


def test_preprocessor_comments():
    pp = prep(preprocessor.preprocessor_comments)

    assert list(pp(['; comment'])) == []
    assert list(pp(['MOV a b; comment'])) == ['MOV a b']


def test_preprocessor_variables():
    pp = prep(preprocessor.preprocessor_constants)

    assert list(pp(['$a = 5', 'MOV $a 3'])) == ['MOV 5 3']
    assert list(pp(['$a = 5', 'MOV 3 $a'])) == ['MOV 3 5']
    assert list(pp(['$a = [5]', 'Jeq 6 $a [1]'])) == ['Jeq 6 [5] [1]']

    # Auto-increment memory slots
    assert list(pp(['$a = [_]', 'MOV $a 1'])) == ['MOV [0] 1']


def test_preprocessor_labels():
    pp = prep(preprocessor.preprocessor_labels)

    assert list(pp(['label:', 'JMP :label'])) == ['JMP 0']


def test_preprocessor_chars():
    pp = prep(preprocessor.preprocessor_chars)

    assert list(pp(["APRINT '\\n'"])) == ['APRINT 10']
    assert list(pp(["APRINT 'A'"])) == ['APRINT 65']
    assert list(pp(["APRINT ' '"])) == ['APRINT 32']


def test_preprocessor_import_nested(tmpdir):
    pp = prep(preprocessor.preprocessor_import)
    tmpdir.join('import.asm').write('MOV [1] 1\n#import import2.asm\nMOV '
                                    '[3] 1')
    tmpdir.join('import2.asm').write('MOV [2] 1\n#import import.asm')

    orig_wd = os.getcwd()
    tmpdir.chdir()

    code = ['MOV [0] 1', '#import import.asm']
    expected = ['MOV [0] 1', 'MOV [1] 1', 'MOV [2] 1', 'MOV [3] 1']
    assert list(pp(code)) == expected

    os.chdir(orig_wd)


def test_preprocessor_import_recursive(tmpdir):
    pp = prep(preprocessor.preprocessor_import)
    tmpdir.join('import.asm').write('MOV [1] 1\n#import import2.asm\nMOV '
                                    '[3] 1')
    tmpdir.join('import2.asm').write('#import import.asm\nMOV [2] 1')

    orig_wd = os.getcwd()
    tmpdir.chdir()

    code = ['MOV [0] 1', '#import import.asm']
    expected = ['MOV [0] 1', 'MOV [1] 1', 'MOV [2] 1', 'MOV [3] 1']
    assert list(pp(code)) == expected

    os.chdir(orig_wd)


def test_preprocessor_import_nonexistend():
    pp = prep(preprocessor.preprocessor_import)

    code = ['MOV [0] 1', '#import import.asm']
    with pytest.raises(FileNotFoundError):
        pp(code)


def test_preprocessor_subroutine():
    pp = prep(preprocessor.preprocessor_subroutine)

    code = ['@start(math_divide, 2)',
            '    math_div_loop:',
            '    JLS     :math_div_done      $arg0       $arg1',
            '    ADD                         $return     1',
            '    SUB                         $arg0       $arg1',
            '    JMP     :math_div_loop',
            '',
            '    math_div_done:',
            '@end()',
            '',
            '$pi_rand0 = [_]',
            '$pi_rand1 = [_]',
            '',
            '    MOV                         $pi_rand0   15',
            '    MOV                         $pi_rand1   2',
            '',
            '    @call(math_divide, $pi_rand0, $pi_rand1)',
            'HALT']

    expected = ['$return = [_]',
                '$jump_back = [_]',
                '$arg0 = [_]',
                '$arg1 = [_]',
                'math_divide:',
                'MOV $return 0',
                '',
                '    math_div_loop:',
                '    JLS     :math_div_done      $arg0       $arg1',
                '    ADD                         $return     1',
                '    SUB                         $arg0       $arg1',
                '    JMP     :math_div_loop',
                '',
                '    math_div_done:',
                'JMP $jump_back',
                '',
                '$pi_rand0 = [_]',
                '$pi_rand1 = [_]',
                '',
                '    MOV                         $pi_rand0   15',
                '    MOV                         $pi_rand1   2',
                '',
                'MOV $arg0 $pi_rand0',
                'MOV $arg1 $pi_rand1',
                'MOV $jump_back :ret0',
                'JMP :math_divide',
                'ret0:',
                'HALT']

    result = list(pp(code))

    pprint(expected, open('expected.asm', 'w'))
    pprint(result, open('result.asm', 'w'))

    assert result == expected
