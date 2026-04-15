import pytest

from assessment.source_audit import (
    AUTHORITATIVE_THAI_PHRASES,
    get_authoritative_source_manifest,
    load_registered_source_text,
    load_authoritative_source_text,
    verify_source_text_integrity,
)


def test_authoritative_source_manifest_declares_trl_file():
    manifest = get_authoritative_source_manifest()
    paths = {entry["path"]: entry for entry in manifest}

    assert manifest
    assert "source/Technology_Readiness_Level_Definition.txt" in paths
    assert "source/compare_each_level_of_trl.txt" in paths
    assert "source/helper_classification_domain_of_research.txt" in paths
    assert "source/helper_classification_level_trl.txt" in paths
    assert paths["source/Technology_Readiness_Level_Definition.txt"]["purpose"] == "trl_definition_authoritative_source"


def test_authoritative_source_file_loads_as_utf8_without_mojibake():
    text = load_authoritative_source_text()

    assert "TRL 1" in text
    assert "Technology_Readiness_Level_Definition" not in text
    for phrase in AUTHORITATIVE_THAI_PHRASES:
        assert phrase in text


def test_authoritative_source_integrity_verification_detects_mojibake():
    report = verify_source_text_integrity("à¸„à¸³à¸­à¸˜à¸´à¸šà¸²à¸¢ TRL")

    assert report["is_valid"] is False
    assert "mojibake" in report["issues"]


def test_registered_source_loader_rejects_unknown_source_with_actionable_message():
    with pytest.raises(ValueError, match="Register it in assessment/source_audit.py SOURCE_REGISTRY"):
        load_registered_source_text("source/missing_trl_source.txt")
