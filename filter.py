class Filter:
    '''Hasty hot fix module, used to prevent @everyone and @here mentions.'''

    def init(self):
        pass

    def apply(self, text):
        text = self.__apply_mention_everyone(text)
        return text

    def apply_strict(self, text):
        text = self.__apply_all_mentions(text)
        return text

    def __apply_mention_everyone(self, text):
        text = text.replace('@everyone', '@\u200beveryone')
        text = text.replace('@here', '@\u200bhere')
        return text

    def __apply_all_mentions(self, text):
        text = text.replace('@', '@\u200b')
        return text
