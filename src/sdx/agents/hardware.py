"""Hardware agent for determining device availability."""

from __future__ import annotations

import os

from functools import lru_cache
from typing import Union

try:
    import torch  # optional
except Exception:  # pragma: no cover
    torch = None  # type: ignore[assignment]


@lru_cache(maxsize=1)
def get_device_label() -> str:
    """Return 'cuda:0', 'mps', or 'cpu'. Respects SDX_DEVICE override."""
    override = os.getenv('SDX_DEVICE')
    if override:  # trust explicit user choice
        return override.strip()

    if torch is None:
        return 'cpu'

    if hasattr(torch, 'cuda') and torch.cuda.is_available():
        return 'cuda:0'

    if hasattr(torch, 'backends') and getattr(torch.backends, 'mps', None):
        try:
            if torch.backends.mps.is_available():
                return 'mps'
        except Exception:
            pass

    return 'cpu'


@lru_cache(maxsize=1)
def get_torch_device() -> Union['torch.device', str]:
    """Return a torch.device when torch is present, else 'cpu' string."""
    label = get_device_label()
    if torch is None:
        return 'cpu'
    return torch.device(label)


@lru_cache(maxsize=1)
def _get_device_id() -> int:
    """Return 0 for CUDA if available, else -1 (CPU/MPS/unknown)."""
    label = get_device_label()
    if label.startswith('cuda:'):
        return 0
    return -1


__all__ = [
    '_get_device_id',
    'get_device_label',
    'get_torch_device',
]
