"""HookType value object."""

from enum import StrEnum


class HookType(StrEnum):
    """Categorization of short-form video opening hook formulas."""

    PROBLEM_AGITATE = "problem_agitate"  # Highlight and agitate a painful problem
    CONTRARIAN = "contrarian"  # Challenge common beliefs or practices
    CURIOSITY_GAP = "curiosity_gap"  # Provoke curiosity with an unanswered question
    SHOCKING_FACT = "shocking_fact"  # Jaw-dropping statistics or counterintuitive facts
    STORY_ORIGIN = "story_origin"  # Personal story or relatable scenario setup
    SECRET_HACK = "secret_hack"  # Revealing an unknown shortcut or framework
