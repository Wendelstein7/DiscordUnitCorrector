from math import log10, floor

SPACED = True    # Option: Should there be a space between the number and the unit? DEFAULT: True
USESIGNIFICANT = True    # Option: Should rounding be done using significancy? If false, rounding will be done using decimal places. DEFAULT: True
SIGNIFICANTFIGURES = 3    # Option: The amount of significant digits that will be kept when rounding.  Ignored when USESIGNIFICANT = False. DEFAULT: 3
DECIMALS = 2    # Option: The amount of decimals to output after conversion. Ignored when USESIGNIFICANT = True. DEFAULT: 2

def roundsignificant(number):
	if number is 0:
		return 0
    return round(number, -int(floor(log10(abs(number))))+SIGNIFICANTFIGURES-1)
    
class UnitType:

    def __init__( self ):
        self._multiples = {}

    def addMultiple( self, unit, multiple ):
        self._multiples[ multiple ] = unit
        return self

    def getStringFromMultiple(self, value, multiple):
        numberString = str((roundsignificant(value / multiple) if USESIGNIFICANT else round(value / multiple, DECIMALS)))
        if numberString[-2:] == ".0":
            numberString = numberString[:-2]
        return numberString + (' ' if SPACED else '') + self._multiples[multiple]

    def getString( self, value ):
        sortedMultiples = sorted(self._multiples, reverse=True)
        for multiple in sortedMultiples:
            if value > multiple/2:
                return self.getStringFromMultiple(value, multiple)
        return self.getStringFromMultiple( value, sortedMultiples[-1] )