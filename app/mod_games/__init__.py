from enum import Enum

from .models import Attempt, GameResult
from .mod_compound import CompoundQuestion, CompoundResult
from .mod_expressions import ExpressionsQuestion, ExpressionsResult
from .mod_mad_minute import MadMinuteResult
from .mod_narrative import NarrativeQuestion, NarrativeResult
from .mod_scribe import ScribeQuestion, ScribeResult

class Game(Enum):
    MAD_MINUTE = 1
    SCRIBE = 2
    COMPOUND = 3
    COPY_EDIT = 4
    SPEAKER = 5
    NARRATIVE = 6
    EXPRESSIONS = 7

    @property
    def question(self):
        if self == Game.MAD_MINUTE:
            return None
        elif self == Game.SCRIBE:
            return ScribeQuestion
        elif self == Game.COMPOUND:
            return CompoundQuestion
        elif self == Game.COPY_EDIT:
            return CopyEditQuestion
        elif self == Game.SPEAKER:
            return SpeakerQuestion
        elif self == Game.NARRATIVE:
            return NarrativeQuestion
        elif self == Game.EXPRESSIONS:
            return ExpressionsQuestion

    @property
    def result(self):
        if self == Game.MAD_MINUTE:
            return None
        elif self == Game.SCRIBE:
            return ScribeResult
        elif self == Game.COMPOUND:
            return CompoundResult
        elif self == Game.COPY_EDIT:
            return CopyEditResult
        elif self == Game.SPEAKER:
            return SpeakerResult
        elif self == Game.NARRATIVE:
            return NarrativeResult
        elif self == Game.EXPRESSIONS:
            return ExpressionsResult
