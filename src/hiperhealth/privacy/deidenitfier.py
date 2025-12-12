"""Deprecated shim: use `hiperhealth.privacy.deidentifier` instead.

This module exists to maintain backward compatibility for any lingering
imports pointing to the misspelled path `hiperhealth.privacy.deidenitfier`.
It re-exports the public API from the corrected module and issues a
`DeprecationWarning`.
"""

import warnings

from .deidentifier import Deidentifier, deidentify_patient_record

warnings.warn(
    "Module 'hiperhealth.privacy.deidenitfier' is deprecated; "
    "use 'hiperhealth.privacy.deidentifier' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["Deidentifier", "deidentify_patient_record"]
