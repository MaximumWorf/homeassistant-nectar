"""OKIN Adjustable Bed Control Library."""

from .bed import OkinBed
from .constants import (
    OKIN_SERVICE_UUID,
    OKIN_TX_CHAR_UUID,
    OKIN_RX_CHAR_UUID,
    NUS_SERVICE_UUID,
    NUS_TX_CHAR_UUID,
    NUS_RX_CHAR_UUID,
    BedPosition,
    MassageWave,
)

__version__ = "0.1.0"
__all__ = [
    "OkinBed",
    "OKIN_SERVICE_UUID",
    "OKIN_TX_CHAR_UUID",
    "OKIN_RX_CHAR_UUID",
    "NUS_SERVICE_UUID",
    "NUS_TX_CHAR_UUID",
    "NUS_RX_CHAR_UUID",
    "BedPosition",
    "MassageWave",
]
