# This is the library that handles the unit conversion itself.
# The unit conversion library was originally created by ficolas2, https://github.com/ficolas2, 2018/01/21
# The unit conversion library has been modified and updated by ficolas2 and Wendelstein7, https://github.com/Wendelstein7

# Licenced under: MIT License, Copyright (c) 2018 Wendelstein7 and ficolas2

import re

import json

from unit import Unit
from unitType import UnitType

REMOVE_REGEX = re.compile("((´|`)+[^>]+(´|`)+)")


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


unitTypes = {}
allUnits = []
targetedUnits = []


unitsArray = json.load(open("units.json"))

#Loop to create unitTypes from SI units
for unitJson in unitsArray:
    if unitJson["SI"]:
        unitType = UnitType()
        unitTypes[ unitJson["Type"] ] = unitType
        for multiple in unitJson["Multiples"]:
            unitType.addMultiple( multiple[0], multiple[1] )
            
#Loop to create all units, and targeted units
for unitJson in unitsArray:
    unit = Unit( unitJson, unitTypes )
    allUnits.append( unit )
    if unit.targeted:
        targetedUnits.append( unit )
        
        
#Finds an unit and returns the information embed message
def lookup(search):
    for unit in allUnits:
        if unit.find( search ):
            return unit.getEmbed()
    return None

#Processes a string, converting freedom units to science units.
def process(message):
    modificableMessage = ModificableMessage(REMOVE_REGEX.sub("", message))
    for unit in targetedUnits:
        unit.convert(modificableMessage)
    if modificableMessage.isModified():
        return modificableMessage.getText()
