# Class containing a string, for the modificable message, and a boolean
# to indicate if the message has been modified
class ModificableMessage:
    def __init__(self, text):
        self._text = text
        self._modified = False

    def getText(self):
        return self._text

    def setText(self, text):
        self._text = text
        self._modified = True

    def isModified(self):
        return self._modified