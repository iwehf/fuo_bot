import re

import emoji as em

LIKE_EMOJI_CODES = ["thumbs_up"]
DISLIKE_EMOJI_CODES = ["cross_mark"]
VALID_EMOJI_CODES = LIKE_EMOJI_CODES + DISLIKE_EMOJI_CODES


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
