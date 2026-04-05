from response_formatter import format_answer_markdown


def test_format_answer_markdown_wraps_answer_in_heading():
    markdown = format_answer_markdown("TRL 4 is laboratory validation.")

    assert markdown.startswith("## TRL Response")
    assert "TRL 4 is laboratory validation." in markdown
