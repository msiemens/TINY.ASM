from exc import NoSuchLabelError, RedefinitionError
from helpers import debug, fatal_error
from preprocessor import set_contents


def collect_labels(lines):
    labels = {}

    token_count = 0

    # Pass 1: Collect labels
    for line in lines:
        tokens = line.contents.split()

        for index, token in enumerate(tokens):
            if token[-1] == ':':
                # Label definition
                label = token[:-1]

                if label in labels:
                    fatal_error('Redefinition of label: ' + label,
                                RedefinitionError, line)

                labels[label] = token_count + index - len(labels)

        token_count += len(tokens)

    return labels


def preprocessor_labels(lines):
    """
    Replace labels with the referenced instruction number.

    Example:

        label:
        GOTO :label

    Results in:

        GOTO 0

    :type lines: list[Line]
    """
    labels = collect_labels(lines)

    # Update references
    for line in lines:
        tokens = []

        for token in line.contents.split():

            # Label usage
            if token[0] == ':':
                label_name = token[1:]

                try:
                    instruction_no = labels[label_name]
                except KeyError:
                    fatal_error('No such label: {}'.format(label_name),
                                NoSuchLabelError, line)
                else:
                    tokens.append(str(instruction_no))

            # Label definitions
            elif token[-1] == ':':
                # Skip
                continue

            else:
                tokens.append(token)

        # If there any tokens left, yield them
        if tokens:
            debug('Labels:', labels)
            yield set_contents(line, ' '.join(tokens))
