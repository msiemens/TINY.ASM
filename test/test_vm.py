import pytest

import config
from exc import VirtualRuntimeError, MissingHaltError

config.TESTING = True

from virtualmachine import (VirtualMachine)

@pytest.fixture
def vm():
    return VirtualMachine()


def test_trivial(vm):
    vm.run('HALT')
    assert vm.running is False


def test_no_halt(vm):
    with pytest.raises(MissingHaltError):
        vm.run('')


def test_invalid_jump(vm):
    with pytest.raises(VirtualRuntimeError):
        vm.run('JMP 1')


def test_infinite_loop(vm):
    with pytest.raises(VirtualRuntimeError):
        vm.run('JMP 0')
