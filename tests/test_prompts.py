import pytest
from langchain_core.prompts import ChatPromptTemplate

# ---------------------------------------------------------------
# RED PHASE: Tests for System Prompt Engineering (Ticket 3.2)
# ---------------------------------------------------------------

def test_prompt_has_required_sections():
    """
    The TRL prompt must contain system, context, and human blocks.
    """
    from rag_prompts import get_trl_prompt
    prompt = get_trl_prompt()
    
    # Check if it's a ChatPromptTemplate
    assert isinstance(prompt, ChatPromptTemplate)
    
    # Check for core sections
    messages = prompt.format_messages(context="Test Context", question="Test Question")
    # Should have at least a system message and a human message
    role_types = [m.type for m in messages]
    assert "system" in role_types
    assert "human" in role_types

def test_prompt_enforces_politeness_and_tone():
    """
    The prompt must contain specific instructions for the healthcare/education 
    empathetic and professional tone.
    """
    from rag_prompts import get_trl_prompt
    prompt = get_trl_prompt()
    
    # Convert to string to check for keywords in the system message
    prompt_str = str(prompt)
    
    polite_keywords = ["polite", "empathetic", "professional", "healthcare", "education"]
    for word in polite_keywords:
        assert word in prompt_str.lower(), f"Prompt missing tone keyword: {word}"

def test_prompt_has_redirect_instruction_for_off_topic():
    """
    The prompt must explicitly instruct the model to decline off-topic 
    questions not related to TRL.
    """
    from rag_prompts import get_trl_prompt
    prompt = get_trl_prompt()
    
    prompt_str = str(prompt).lower()
    
    # Check for instructions to stay in context or decline
    assert "only" in prompt_str and "context" in prompt_str
    assert "sorry" in prompt_str or "apologize" in prompt_str
    assert "information" in prompt_str


def test_prompt_includes_markdown_safety_rules():
    """
    The prompt should explicitly constrain markdown structure so frontend
    rendering stays predictable.
    """
    from rag_prompts import get_trl_prompt
    prompt_str = str(get_trl_prompt()).lower()

    assert "markdown structure" in prompt_str
    assert "allowed markdown" in prompt_str
    assert "disallowed markdown" in prompt_str
    assert "level-2 heading" in prompt_str
    assert "bullet" in prompt_str
