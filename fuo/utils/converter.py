from discord.ext.commands import BadArgument

from fuo import model


def to_score_type(s: str) -> model.ScoreType:
    try:
        res = model.ScoreType[s.upper()]
    except KeyError:
        raise BadArgument(f"{s} is not a valid score type.")
    return res


def to_channel_type(s: str) -> model.ChannelType:
    try:
        res = model.ChannelType[s.upper()]
    except KeyError:
        raise BadArgument(f"{s} is not a valid channel type.")
    return res
