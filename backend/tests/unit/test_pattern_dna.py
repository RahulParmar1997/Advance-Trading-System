from decimal import Decimal

import pytest

from advance_system.research.pattern_dna import PatternDNA, PatternDNAEngine


def test_pattern_dna_normalizes_feature_order() -> None:
    pattern = PatternDNA.from_mapping("p1", {"z": Decimal("2"), "a": Decimal("1")})
    assert pattern.features == (("a", Decimal("1")), ("z", Decimal("2")))


def test_similarity_search_is_deterministic_and_sorted() -> None:
    engine = PatternDNAEngine()
    query = PatternDNA.from_mapping("q", {"trend": Decimal("1"), "vol": Decimal("2")})
    corpus = [
        PatternDNA.from_mapping("far", {"trend": Decimal("4"), "vol": Decimal("5")}, outcome_r=Decimal("-1")),
        PatternDNA.from_mapping("near", {"trend": Decimal("1"), "vol": Decimal("3")}, outcome_r=Decimal("2")),
        PatternDNA.from_mapping("near2", {"trend": Decimal("1"), "vol": Decimal("3")}, outcome_r=Decimal("1")),
    ]
    matches = engine.search(query, corpus, limit=2)
    assert [m.pattern_id for m in matches] == ["near", "near2"]
    assert matches[0].distance == Decimal("1.0")


def test_similarity_requires_matching_feature_schema() -> None:
    engine = PatternDNAEngine()
    a = PatternDNA.from_mapping("a", {"x": Decimal("1")})
    b = PatternDNA.from_mapping("b", {"y": Decimal("1")})
    with pytest.raises(ValueError):
        engine.distance(a, b)


def test_outcome_summary_uses_observed_outcomes_only() -> None:
    matches = [
        type("M", (), {"outcome_r": Decimal("2")})(),
        type("M", (), {"outcome_r": None})(),
        type("M", (), {"outcome_r": Decimal("-1")})(),
    ]
    count, average = PatternDNAEngine().outcome_summary(matches)
    assert count == 2
    assert average == Decimal("0.5")
