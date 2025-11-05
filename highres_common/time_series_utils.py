"""
Time-series helper utilities for highres_common.

Provides small utilities such as determining sampling frequency from a
monotonic timestamp array.

Edits made to align with aiweb_common style:
- Added module docstring, typing, and logging.
- Added input validation and clearer return typing.
"""
from typing import Iterable
import logging

import numpy as np

logger = logging.getLogger(__name__)


def determine_fs(data: Iterable[float]) -> float:
    """
    Determine sampling frequency from a 1D numeric sequence of timestamps or sample indices.

    Args:
        data: 1D iterable of monotonically increasing timestamps (seconds) or sample indices.

    Returns:
        Estimated sampling frequency (Hz) as float.

    Raises:
        ValueError: if fewer than two samples are provided or if input cannot be interpreted as numeric.
    """
    arr = np.asarray(list(data), dtype=float)
    if arr.size < 2:
        raise ValueError("At least two samples are required to determine sampling frequency.")
    diffs = np.diff(arr)
    if np.any(diffs <= 0):
        logger.warning("Non-positive differences detected in input timestamps; results may be invalid.")
    fs = 1.0 / float(np.median(diffs))
    logger.info("Determined sampling frequency: %s Hz", fs)
    return float(fs)
