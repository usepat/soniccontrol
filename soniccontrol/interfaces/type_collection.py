from typing import (
    List,
    Tuple,
    Dict,
    Set,
    Optional,
    Union,
    Callable,
    TYPE_CHECKING,
    Iterable,
    Any,
)

from soniccontrol.interfaces.rootchild import RootChild, RootChildFrame
from soniccontrol.interfaces.rootnotebook import RootNotebook

RootComponent = Union[RootChild, RootNotebook, RootChildFrame]
