from soniccontrol_gui.constants import ui_labels
import attrs

labels = attrs.asdict(ui_labels)
# Dynamically create variables with the prefix "LABEL_" in the module's namespace
for k, v in labels.items():
    globals()["LABEL_" + k] = v 