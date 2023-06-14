from discord.ext.commands import BadArgument

from fuo import models


def to_score_type(s: str) -> models.ScoreType:
    try:
        res = models.ScoreType[s.upper()]
    except KeyError:
        raise BadArgument(f"{s} is not a valid score type.")
    return res


def to_channel_type(s: str) -> models.ChannelType:
    try:
        res = models.ChannelType[s.upper()]
    except KeyError:
        raise BadArgument(f"{s} is not a valid channel type.")
    return res


def to_score_source(s: str) -> models.ScoreSource:
    try:
        res = models.ScoreSource[s.upper()]
    except KeyError:
        raise BadArgument(f"{s} is not a valid score source.")
    return res
