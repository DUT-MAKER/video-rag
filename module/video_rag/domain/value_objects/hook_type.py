"""HookType enumeration."""

from enum import Enum


class HookType(str, Enum):
    """Categorization of viral video hook formats."""

    QUESTION = "question"
    CURIOSITY_GAP = "curiosity_gap"
    CONTRARIAN = "contrarian"
    STATISTIC = "statistic"
    STORY_IN_MEDIAS_RES = "story_in_medias_res"
    NEGATIVE_WARNING = "negative_warning"
    BOLD_CLAIM = "bold_claim"
    VISUAL_INTERRUPT = "visual_interrupt"
    SECRET_REVEAL = "secret_reveal"
    # Legacy & domain benchmark hook formulas
    SHOCKING_FACT = "shocking_fact"
    PROBLEM_AGITATE = "problem_agitate"
    STORY_ORIGIN = "story_origin"
    SECRET_HACK = "secret_hack"


    @classmethod
    def from_str(cls, value: str) -> "HookType":
        try:
            return cls(value.lower().strip())
        except ValueError:
            return cls.CURIOSITY_GAP
