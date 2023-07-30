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

from soniccontrol.interfaces.rootchild import RootChild
from soniccontrol.interfaces.rootnotebook import RootNotebook

RootComponent = Union[RootChild, RootNotebook]
