'''Hasty hot fix module, used to prevent @everyone and @here mentions.'''


def __apply_mention_everyone(text):
    text = text.replace('@everyone', '@\u200beveryone')
    text = text.replace('@here', '@\u200bhere')
    return text


def __apply_all_mentions(text):
    text = text.replace('@', '@\u200b')
    return text


def apply(text):
    text = __apply_mention_everyone(text)
    return text


def apply_strict(text):
    text = __apply_all_mentions(text)
    return text
