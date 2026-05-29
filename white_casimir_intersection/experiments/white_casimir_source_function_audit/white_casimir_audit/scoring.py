"""Conservative interpretation labels for audit scores."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreRecord:
    morphology_score: float = 0.0
    has_stress_proxy: bool = False
    has_tensor_channels: bool = False
    source_demand_ratio: float = 0.0
    transit_channel_coupled: bool = False
    observable_ratio: float = 0.0
    ordinary_em_dominant: bool = False
    model_limitations: bool = False
    morphology_threshold: float = 0.5
    partial_source_ratio_threshold: float = 1.0e-6
    relevance_source_ratio_threshold: float = 1.0e-2
    transport_observable_ratio_threshold: float = 1.0e-2


def classify(record: ScoreRecord) -> set[str]:
    labels: set[str] = set()
    if record.morphology_score >= record.morphology_threshold:
        labels.add("casimir_morphology_supported")
    if "casimir_morphology_supported" in labels and record.has_stress_proxy and not record.has_tensor_channels:
        labels.add("source_function_proxy_supported")
    if record.has_tensor_channels and record.source_demand_ratio >= record.partial_source_ratio_threshold:
        labels.add("source_function_partially_supported")
    if (
        "source_function_partially_supported" in labels
        and record.morphology_score >= max(record.morphology_threshold, 0.7)
        and record.source_demand_ratio >= record.relevance_source_ratio_threshold
    ):
        labels.add("alcubierre_shell_relevance_supported")
    if record.ordinary_em_dominant or (
        record.observable_ratio > 0.0
        and record.observable_ratio < record.transport_observable_ratio_threshold
    ):
        labels.add("ordinary_em_explanation_dominant")
    if (
        "alcubierre_shell_relevance_supported" in labels
        and record.transit_channel_coupled
        and record.observable_ratio >= record.transport_observable_ratio_threshold
        and not record.ordinary_em_dominant
    ):
        labels.add("transport_relevance_supported")
    if record.model_limitations or not labels:
        labels.add("inconclusive_due_to_model_limits")
    return labels
