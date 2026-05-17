from __future__ import annotations

"""Compatibility wrapper for older imports.

New code should use adm_harness.service_modifiers. Absorber/control laws are now
modeled as carrying-flow service modifiers rather than a separate center of the
harness.
"""

from .service_modifiers import FieldDeltaResult, compute_service_field_delta

__all__ = ["FieldDeltaResult", "compute_service_field_delta"]
