import re

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


def timestr_to_seconds(s: str) -> int:
    res = 0
    m = re.match(r"^((?P<hour>\d+)h)?((?P<minute>\d+)m)?((?P<second>\d+)s)?$", s)

    if m is None or len(m.groups()) <= 1:
        raise BadArgument(f"{s} is not a valid time string")
    
    hour = m.group("hour")
    if hour is not None:
        res += int(hour) * 3600
    minute = m.group("minute")
    if minute is not None:
        res += int(minute) * 60
    second = m.group("second")
    if second is not None:
        res += int(second)
    
    return res
