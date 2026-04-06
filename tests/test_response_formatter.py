from response_formatter import format_answer_markdown


def test_format_answer_markdown_wraps_answer_in_heading():
    markdown = format_answer_markdown("TRL 4 is laboratory validation.")

    assert markdown.startswith("## คำตอบ TRL")
    assert "TRL 4 is laboratory validation." in markdown


def test_format_answer_markdown_supports_assessment_title():
    markdown = format_answer_markdown("สรุประดับความพร้อมอยู่ที่ TRL 4", title="ผลการประเมิน TRL")

    assert markdown.startswith("## ผลการประเมิน TRL")
    assert "สรุประดับความพร้อมอยู่ที่ TRL 4" in markdown
