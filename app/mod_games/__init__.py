from enum import Enum

from app.mod_games.mod_compound.models import CompoundQuestion, CompoundResult
from app.mod_games.mod_expressions.models import ExpressionsQuestion, ExpressionsResult
from app.mod_games.mod_mad_minute.models import MadMinuteResult
from app.mod_games.mod_narrative.models import NarrativeQuestion, NarrativeResult
from app.mod_games.mod_scribe.models import ScribeQuestion, ScribeResult

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
