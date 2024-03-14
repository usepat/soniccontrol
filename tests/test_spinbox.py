from soniccontrol.components.spinbox import Spinbox


def test_spinbox_with_placeholder_initialization(placeholder):
    spinbox = Spinbox(placeholder)
    assert spinbox.placeholder == placeholder


def test_spinbox_focus_out_event(placeholder):
    spinbox = Spinbox(placeholder)
    # TODO: monkey patch spinbox._on_focus_in()
    spinbox.event_generate("<FocusIn>")
    # TODO: assert spinbox._on_focus_in was called
    assert spinbox.get() != placeholder

    spinbox.event_generate("<FocusOut>")
    # TODO: assert spinbox._on_focus_out was called
    assert spinbox.get() == placeholder


def test_spinbox_configuration(placeholder):
    spinbox = Spinbox()
    spinbox.placeholder = placeholder
    spinbox.event_generate("<FocusOut>")
    assert spinbox.get() == placeholder
