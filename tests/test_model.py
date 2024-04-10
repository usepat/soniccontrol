import pytest

from soniccontrol.sonicpackage.amp_data import ObservableVar


class ObservableVarTester:
    def __init__(self):
        self.write_reference_count = 0
        self.read_reference_count = 0

    def write_func(self, value):
        self.write_reference_count += 1

    def read_func(self, value):
        self.read_reference_count += 1

    def write_func_2(self, value):
        self.write_reference_count += 1

    def read_func_2(self, value):
        self.read_reference_count += 1


@pytest.mark.parametrize(
    "test_input",
    [
        ((1, 2, 3, 4)),
        (("", "test", "test2", "string_test3")),
        ((1.123, 2.231, 3.12345, 4.9827)),
    ],
)
def test_observable_var(test_input):
    counter = ObservableVarTester()
    var = ObservableVar(test_input[0])
    assert var.get() == test_input[0]
    var.set(test_input[1])
    assert var.get() == test_input[1]

    var.add_write_callback(counter.write_func)
    var.add_write_callback(counter.read_func)
    var.set(test_input[2])
    assert counter.write_reference_count == 1
    assert var.get() == test_input[2]
    assert counter.read_reference_count == 1

    var.add_write_callback(counter.write_func_2)
    var.add_read_callback(counter.read_func_2)
    var.set(test_input[3])
    assert counter.write_reference_count == 3
    assert var.get() == test_input[3]
    assert counter.read_reference_count == 3
