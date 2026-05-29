from white_casimir_audit.scoring import ScoreRecord, classify


def test_stress_proxy_does_not_grant_tensor_partial_label():
    labels = classify(ScoreRecord(morphology_score=0.8, has_stress_proxy=True))
    assert "casimir_morphology_supported" in labels
    assert "source_function_proxy_supported" in labels
    assert "source_function_partially_supported" not in labels


def test_transport_label_requires_non_dominant_em_channel():
    labels = classify(
        ScoreRecord(
            morphology_score=0.9,
            has_tensor_channels=True,
            source_demand_ratio=0.1,
            transit_channel_coupled=True,
            observable_ratio=0.1,
            ordinary_em_dominant=True,
        )
    )
    assert "alcubierre_shell_relevance_supported" in labels
    assert "ordinary_em_explanation_dominant" in labels
    assert "transport_relevance_supported" not in labels
