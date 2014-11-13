from collections import namedtuple

Line = namedtuple('Line', ['lineno', 'filename', 'original_contents',
                           'contents'])
set_contents = lambda line, contents: Line(line.lineno, line.filename,
                                           line.original_contents, contents)

from . chars import preprocessor_chars
from . comments import preprocessor_comments
from . constants import preprocessor_constants
from . imports import preprocessor_import
from . labels import preprocessor_labels
from . subroutine import preprocessor_subroutine


def prepare_source_code(filename, source_code):
    code = []

    for lineno, line in enumerate(source_code.splitlines()):
        code.append(Line(lineno, filename, line, line))

    return code


def preprocess(source_code, filename):
    """
    :type source_code: str
    """
    # Prepare source code for processing
    code = prepare_source_code(filename, source_code)

    # Run preprocessors
    preprocessors = (preprocessor_import, preprocessor_comments,
                     preprocessor_subroutine, preprocessor_constants,
                     preprocessor_labels, preprocessor_chars)

    for preprocessor in preprocessors:
        code = list(preprocessor(code))

    return code
