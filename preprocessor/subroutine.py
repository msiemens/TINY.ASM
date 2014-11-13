from itertools import count
from exc import AssemblerSyntaxError, AssemblerNameError, AssemblerException
from helpers import syntax_error, fatal_error, debug
from preprocessor import Line

line_counter = count()
call_counter = count()


def reset_counters():
    global line_counter, call_counter
    line_counter = count()
    call_counter = count()


def build_line(contents):
    return Line(next(line_counter), '<subroutine>', contents, contents)


def verify_start(parts, line):
    if not parts[-1].endswith(')'):
        syntax_error('Missing closing quote',
                     AssemblerSyntaxError, line)

    if not len(parts) == 2:
        syntax_error('Invalid number of arguments to @start',
                     AssemblerSyntaxError, line)


def collect_definitions(lines):
    subroutines = {}

    for line in lines:
        contents = line.contents.strip()

        if contents.startswith('@start('):
            # : :type: list[str]
            contents = contents.replace('@start(', '')

            parts = contents.split(',')
            verify_start(parts, line)

            name = parts[0].strip()
            if not any(c.isalnum() or c == '_' for c in name):
                syntax_error('Invalid subrountine name: {}'.format(name),
                             AssemblerSyntaxError, line)

            arg_count = parts[1].strip(' )')

            subroutines[name] = int(arg_count)

    return subroutines


def process_call(line, contents, subroutines):
    contents = contents.replace('@call', '')
    contents = contents.strip('()')

    parts = contents.split(',')
    name = parts[0]
    args = [s.strip(' )') for s in parts[1:]]

    if name not in subroutines:
        fatal_error('Unknown subroutine: {}'.format(name),
                    AssemblerNameError, line)

    if len(args) != subroutines[name]:
        msg = 'Wrong number of arguments: Expected {}, got {}'.format(
            subroutines[name], len(args)
        )
        fatal_error(msg, AssemblerException, line)

    debug('@call of {}'.format(name))

    for i, arg in enumerate(args):
        yield build_line('MOV $arg{} {}'.format(i, arg))

    counter = next(call_counter)
    yield build_line('MOV $jump_back :ret{}'.format(counter))
    yield build_line('JMP :{}'.format(name))
    yield build_line('ret{}:'.format(counter))


def _subroutine_process_start(line, contents):
    # : :type: list[str]
    parts = contents.split(',')
    verify_start(parts, line)

    name = parts[0].replace('@start', '').strip('( ')

    debug('@start: {}'.format(name))

    yield build_line('{}:'.format(name))
    yield build_line('MOV $return 0')
    yield build_line('')


def preprocessor_subroutine(lines):
    reset_counters()

    subroutines = collect_definitions(lines)

    if not subroutines:
        # Check, if there are calls w/o definition
        for line in lines:
            if '@call' in line.contents:
                fatal_error('@call without subroutine definition',
                            AssemblerException, line)

        yield from lines
        return

    debug('{} subroutines found: {}'.format(len(subroutines), subroutines))

    # Build preamble
    yield build_line('$return = [_]')
    yield build_line('$jump_back = [_]')

    for i in range(max(subroutines.values())):
        yield build_line('$arg{} = [_]'.format(i))

    # Process start()/end()/call()
    in_subroutine = False
    call_count = 0

    for line in lines:
        #: :type: str
        contents = line.contents.strip()

        if contents.startswith('@call'):
            yield from process_call(line, contents, subroutines)
            call_count += 1

        elif contents.startswith('@start('):
            if in_subroutine:
                assert False

            in_subroutine = True
            yield from _subroutine_process_start(line, contents)

        elif contents.startswith('@end()'):
            if not in_subroutine:
                assert False

            debug('@end')

            in_subroutine = False
            yield Line(0, '<subroutine>', '', 'JMP $jump_back')

        else:
            yield line
