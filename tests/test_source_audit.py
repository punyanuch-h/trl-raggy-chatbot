from assessment.source_audit import (
    AUTHORITATIVE_THAI_PHRASES,
    get_authoritative_source_manifest,
    load_authoritative_source_text,
    verify_source_text_integrity,
)


def test_authoritative_source_manifest_declares_trl_file():
    manifest = get_authoritative_source_manifest()

    assert manifest
    assert manifest[0]["path"].endswith("source/04_Technology Readiness Level-TRL.txt")
    assert manifest[0]["purpose"] == "trl_assessment_rule_base"


def test_authoritative_source_file_loads_as_utf8_without_mojibake():
    text = load_authoritative_source_text()

    assert "TRL 1" in text
    for phrase in AUTHORITATIVE_THAI_PHRASES:
        assert phrase in text


def test_authoritative_source_integrity_verification_detects_mojibake():
    report = verify_source_text_integrity("à¸„à¸³à¸­à¸˜à¸´à¸šà¸²à¸¢ TRL")

    assert report["is_valid"] is False
    assert "mojibake" in report["issues"]
