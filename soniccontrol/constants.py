from typing_extensions import Literal, Union


StatusDict = dict[
    Literal[
        "error",
        "frequency",
        "gain",
        "signal",
        "wipe_mode",
        "protocol",
        "relay_mode",
        "communication_mode",
    ],
    Union[int, float, str, bool],
]
