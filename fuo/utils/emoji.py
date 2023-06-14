import logging
import re

import emoji as em

LIKE_EMOJI_CODES = ["thumbs_up", "hundred_points", "red_heart", "tears_of_joy"]
DISLIKE_EMOJI_CODES = ["cross_mark", "neutral_face"]
VALID_EMOJI_CODES = LIKE_EMOJI_CODES + DISLIKE_EMOJI_CODES

_logger = logging.getLogger(__name__)

def is_valid_emoji(emoji: str):
    if em.is_emoji(emoji):
        code = em.demojize(emoji)
        for dst in VALID_EMOJI_CODES:
            if re.search(dst, code) is not None:
                return True
    return False


def is_like_emoji(emoji: str):
    if em.is_emoji(emoji):
        code = em.demojize(emoji)
        for dst in LIKE_EMOJI_CODES:
            if re.search(dst, code) is not None:
                return True
    return False


def is_dislike_emoji(emoji: str):
    if em.is_emoji(emoji):
        code = em.demojize(emoji)
        for dst in DISLIKE_EMOJI_CODES:
            if re.search(dst, code) is not None:
                return True
    return False
