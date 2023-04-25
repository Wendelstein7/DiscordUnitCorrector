# This is the library that handles the unit conversion itself.
# The unit conversion library was originally created by ficolas2, https://github.com/ficolas2, 2018/01/21
# The unit conversion library has been modified and updated by ficolas2 and Wendelstein7, https://github.com/Wendelstein7

# Licenced under: MIT License, Copyright (c) 2018 Wendelstein7 and ficolas2

import re
from abc import abstractmethod
from sigfigs import SigFigCompliantNumber

END_NUMBER_REGEX = re.compile("(^|\s)(-|−)?[0-9]+([\,\.][0-9]*)?\s*$")
REMOVE_REGEX = re.compile("((´|`)+[^>]+(´|`)+)")

UNICODEMINUS = True    # Option: Should UNICODE minus symbol '−' be converted to a standard dash '-'?
SPACED = " "    # Option: What should separate the number and the unit? DEFAULT: one space (" ")

SIGFIG_COMPLIANCE_LEVEL = 1 # Option: How hard should the bot try to follow sig figs, at the expense of readability?
                            # Value is an int from 0 to 2, where largest is most copmliant and least readable. DEFAULT: 1
USE_TENPOW = False          # Option: Should outputs in scientific notation be like `4*10^3` instead of `4e+3`? DEFAULT: False

class UnitType:

    def __init__( self ):
        self._multiples = {}

    def addMultiple( self, unit, multiple ):
        self._multiples[ multiple ] = unit
        return self

    def getStringFromMultiple(self, value, multiple):
        numstr = str(value / multiple)
        if (SIGFIG_COMPLIANCE_LEVEL == 0):
            if (numstr[len(numstr)-1] == '.'):
                numstr = numstr[0:-1]
            if ("e" in numstr):
                numstr = str(float(numstr))
                if (not "e" in numstr and numstr.endswith(".0")):
                    numstr = numstr[0:-2]
        if (USE_TENPOW):
            numstr = numstr.replace("e+", "*10^")
            numstr = numstr.replace("e", "*10^")
        return numstr + SPACED + self._multiples[multiple]

    def getString( self, value ):
        sortedMultiples = sorted(self._multiples, reverse=True)
        for multiple in sortedMultiples:
            if abs(value) > multiple/2:
                return self.getStringFromMultiple(value, multiple)
        return self.getStringFromMultiple( value, sortedMultiples[-1] )

DISTANCE = UnitType().addMultiple("m", 1).addMultiple( "km", 10**3 ).addMultiple( "cm", 10**-2).addMultiple( "mm", 10**-3).addMultiple( "µm", 10**-6).addMultiple( "nm", 10**-9).addMultiple( "pm", 10**-12 )
AREA = UnitType().addMultiple( "m²", 1 ).addMultiple( "km²", 10**6 ).addMultiple( "cm²", 10**-4).addMultiple( "mm²", 10**-6)
VOLUME = UnitType().addMultiple( "L", 1 ).addMultiple( "mL", 10**-3 ).addMultiple( "µL", 10**-6 ).addMultiple( "nL", 10**-9 ).addMultiple( "pL", 10**-12 )
ENERGY = UnitType().addMultiple( "J", 1 ).addMultiple( "TJ", 10**12 ).addMultiple( "GJ", 10**9 ).addMultiple( "MJ", 10**6 ).addMultiple( "kJ", 10**3 ).addMultiple( "mJ", 10**-3 ).addMultiple( "µJ", 10**-6 ).addMultiple( "nJ", 10**-9 )
FORCE = UnitType().addMultiple( "N", 1 ).addMultiple( "MN", 10**6 ).addMultiple( "kN", 10**3 ).addMultiple( "mN", 10**-3 ).addMultiple( "µN", 10**-6 ).addMultiple( "nN", 10**-9 ).addMultiple( "pN", 10**-12 )
TORQUE = UnitType().addMultiple( "N*m", 1 )
VELOCITY = UnitType().addMultiple("m/s", 1).addMultiple( "km/s", 10**3 )
MASS = UnitType().addMultiple( "g", 1 ).addMultiple( "kg", 10**3 ).addMultiple( "mg", 10**-3 ).addMultiple( "µg", 10**-6 ).addMultiple( "ng", 10**-9 ).addMultiple( "pg", 10**-12 )
TEMPERATURE = UnitType().addMultiple( "°C", 1 )
PRESSURE = UnitType().addMultiple( "atm", 1 )
LUMINOUSINTENSITY = UnitType().addMultiple( "cd", 1 )
POWER = UnitType().addMultiple( "W", 1 ).addMultiple( "pW", 10**-12 ).addMultiple( "nW", 10**-9 ).addMultiple( "µW", 10**-6 ).addMultiple( "mW", 10**-3 ).addMultiple( "kW", 10**3 ).addMultiple( "MW", 10**6 ).addMultiple( "GW", 10**9 ).addMultiple( "TW", 10**12 )

class Unit:
    def __init__( self, friendlyName, unitType, toSIMultiplication, toSIAddition ):
        self._friendlyName = friendlyName
        self._unitType = unitType
        self._toSIMultiplication = toSIMultiplication
        self._toSIAddition = toSIAddition

    def toMetric( self, value ):
        SIValue = ( value + self._toSIAddition ) * self._toSIMultiplication
        if SIValue == 0:
            if (SIGFIG_COMPLIANCE_LEVEL == 2):
                numstr = str(SIValue)
                if USE_TENPOW:
                    numstr = numstr.replace("e+", "*10^")
                    numstr = numstr.replace("e", "*10^")
                return numstr + SPACED + self._unitType._multiples[1]
            return "0" + SPACED + self._unitType._multiples[1]
        return self._unitType.getString( SIValue )

    def getName( self ):
        return self._friendlyName

    @abstractmethod
    def convert( self, message ): pass

def convertUnitInModificableMessage( message, unit_regex, toMetric ):
    global SPACED
    originalText = message.getText()
    if UNICODEMINUS:
        originalText = originalText.replace('−', '-')
    iterator = unit_regex.finditer( originalText )
    replacements = []
    for find in iterator:
        numberResult = END_NUMBER_REGEX.search( originalText[ 0 : find.start() ] )
        if numberResult is not None:
            usernumber = SigFigCompliantNumber(numberResult.group().strip().replace(",", "."))
            initialSpaceCount = 0
            prefix = ""
            while (numberResult.group()[initialSpaceCount].isspace()):
                prefix += numberResult.group()[initialSpaceCount]
                initialSpaceCount += 1
            old_spacing = SPACED
            postSpaceCount = len(numberResult.group()) - 1
            SPACED = ""
            while (numberResult.group()[postSpaceCount].isspace()):
                SPACED = numberResult.group()[postSpaceCount] + SPACED
                postSpaceCount -= 1
            metricValue = toMetric( usernumber )
            SPACED = old_spacing
            if metricValue is None:
                continue
            repl = {}
            repl[ "start" ] = numberResult.start()
            repl[ "text"  ] = (prefix) + metricValue
            repl[ "end" ] = find.end()
            replacements.append(repl)
    if len(replacements)>0:
        lastPoint = 0
        finalMessage = ""
        for repl in replacements:
            finalMessage += originalText[ lastPoint: repl[ "start" ] ] + repl[ "text" ]
            lastPoint = repl["end"]
        finalMessage += originalText[ lastPoint : ]
        message.setText(finalMessage)

#NormalUnit class, that follow number + unit name.
class NormalUnit( Unit ):
    def __init__( self, friendlyName, regex, unitType, toSIMultiplication, toSIAddition = 0 ):
        super( NormalUnit, self ).__init__( friendlyName, unitType, toSIMultiplication, toSIAddition )
        self._regex = re.compile( "(" + regex + ")(?=[!?.,()\"\']*(\\s|$))", re.IGNORECASE )

    def convert( self, message ):
        convertUnitInModificableMessage( message, self._regex, self.toMetric )

class CaseSensitiveUnit( Unit ):
    def __init__( self, friendlyName, regex, unitType, toSIMultiplication, toSIAddition = 0 ):
        super( CaseSensitiveUnit, self ).__init__( friendlyName, unitType, toSIMultiplication, toSIAddition )
        self._regex = re.compile( "(" + regex + ")(?=[!?.,()\"\']*(\\s|$))" )
    
    def convert( self, message ):
        return convertUnitInModificableMessage( message, self._regex, self.toMetric)

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

units = []

#Area
units.append( NormalUnit( "inch squared", "in(ch(es)?)? ?(\^2|squared|²)", AREA, 0.00064516 ) )     #inch squared
units.append( NormalUnit( "foot squared", "f(oo|ee)?t ?(\^2|squared|²)", AREA, 0.092903 ) )         #foot squared
units.append( NormalUnit( "mile squared", "mi(les?)? ?(\^2|squared|²)", AREA, 2589990 ) )           #mile squared
units.append( NormalUnit( "acre", "acres?", AREA, 4046.8564224 ) )                                  #acre
units.append( NormalUnit( "rood", "roods?", AREA, 1011.7141 ) )                                     #rood

#Volume
units.append( NormalUnit( "pint", "pints?|pt", VOLUME, 0.473176 ) )                     #pint
units.append( NormalUnit( "quart", "quarts?|qt", VOLUME, 0.946353 ) )                   #quart
units.append( NormalUnit( "gallon", "gal(lons?)?", VOLUME, 3.78541 ) )                  #gallon
units.append( NormalUnit( "fluid ounce", "fl\.? oz\.?", VOLUME, 0.0295735296 ) )        #fluid ounce
units.append( NormalUnit( "teaspoon", "tsp|teaspoons?", VOLUME, 0.00492892159 ) )       #US teaspoon
units.append( NormalUnit( "tablespoon", "tbsp|tablespoons?", VOLUME, 0.0147867648 ) )   #US tablespoon
units.append( NormalUnit( "barrel", "drum|barrels?", VOLUME, 119.240471 ) )             #barrel
units.append( NormalUnit( "peck", "pecks?", VOLUME, 8.809768 ) )                        #pecks
units.append( NormalUnit( "bushel", "bushels?", VOLUME, 35.23907016688 ) )              #bushels

#Energy
units.append( NormalUnit( "foot-pound", "ft( |\*)?lbf?|foot( |-)pound", ENERGY, 1.355818 ) )                 #foot-pound
units.append( NormalUnit( "British thermal unit", "btu", ENERGY, 1055.06 ) )                                 #British thermal unit
units.append( CaseSensitiveUnit( "calories", "cal(ories?)?", ENERGY, 4.184 ) )                               #calories
units.append( CaseSensitiveUnit( "kilocalories", "(k(ilo)?c|C)al(ories?)?", ENERGY, 4184 ) )       #kilocalories
units.append( NormalUnit( "ton of refrigeration", "ton of refrigeration", POWER, 3500 ) )                    #ton of refrigeration
units.append( NormalUnit( "ergs", "ergs?", ENERGY, 10**-7 ) )                                                #ergs

#Force
units.append( NormalUnit( "pound-force", "pound( |-)?force|lbf", FORCE, 4.448222 ) )            #pound-force

#Torque
units.append( NormalUnit( "pound-foot", "Pound(-| )?(f(oo|ee)?t)|lbf( |\*)?ft", TORQUE, 1.355818 ) )      #pound-foot

#Velocity
units.append( NormalUnit( "miles per hour", "miles? per hour|mph|mi/h", VELOCITY, 0.44704 ) )             #miles per hour
units.append( NormalUnit( "knot", "knots?|kts?", VELOCITY, 0.51444444444 ) )                              #knots
units.append( NormalUnit( "feet per second", "f(oo|ee)?t ?(per|/|p) ?s(ec|onds?)?", VELOCITY, 0.3048 ) )  #feet per second

#Temperature
units.append( NormalUnit( "degrees fahrenheit", "((°|º|deg(ree)?s?) ?)?(fahrenheit|freedom|f)", TEMPERATURE, 5/9, -32 ) )  #Degrees freedom
units.append( NormalUnit( "degrees rankine", "((°|º|deg(ree)?s?) ?)?(ra?(nkine)?)", TEMPERATURE, 5/9, -491.67 ) )          #Degrees rankine

#Pressure
units.append( NormalUnit( "pound per square inch", "pounds?((-| )?force)? per square in(ch)?|lbf\/in\^2|psi", PRESSURE, 0.068046 ) ) #Pounds per square inch

#Mass
units.append( NormalUnit( "ounce", "ounces?|oz", MASS, 28.349523125 ) )                  #ounces
units.append( NormalUnit( "pound", "pounds?|lbs?", MASS, 453.59237 ) )                   #pounds
units.append( NormalUnit( "stone", "stones?|(?<!1)st", MASS, 6350.2293318 ) )            #stones
units.append( NormalUnit( "grain", "grains?", MASS, 0.06479891 ) )                       #grains
units.append( NormalUnit( "slug", "slugs?", MASS, 14593.9029 ) )                         #slug
units.append( NormalUnit( "troy ounce", "troy ?ounces?", MASS, 31.1034768 ) )            #troy ounces
units.append( NormalUnit( "pennyweight", "penny ?weights?", MASS, 1.55517384 ) )         #pennywheight
units.append( NormalUnit( "troy pound", "troy ?pounds?", MASS, 373.2417216 ) )           #troy pound
units.append( NormalUnit( "dram", "drams?", MASS, 1.7718451953125 ) )                    #drams
units.append( NormalUnit( "hundredweight", "hundredweights?|cwt", MASS, 50802 ) )        #hundredweights

#Distance
units.append( NormalUnit( "inch", "inch(es)?", DISTANCE, 0.0254 ) )                           #inch
units.append( NormalUnit( "foot", "f(oo|ee)?t", DISTANCE, 0.3048 ) )                      #foot
units.append( NormalUnit( "mile", "mi(les?)?", DISTANCE, 1609.344 ) )                         #mile
units.append( NormalUnit( "yard", "yd|yards?", DISTANCE, 0.9144 ) )                           #yard
units.append( NormalUnit( "nautical mile", "nautical ?(mi(les?)?)?|nmi", DISTANCE, 1852 ) )   #nautical miles
units.append( NormalUnit( "thou", "thou", DISTANCE, 0.0000254 ) )                             #thou
units.append( NormalUnit( "fathom", "fathoms?", DISTANCE, 1.8288 ) )                          #fathom
units.append( NormalUnit( "furlong", "furlongs?", DISTANCE, 201.1680 ) )                      #furlong
units.append( NormalUnit( "rack unit", "rack ?units?|ru", DISTANCE, 0.04445 ) )               #rack units
units.append( NormalUnit( "smoot", "smoots?", DISTANCE, 1.7018 ) )                            #Smoot units

#Luminous intensity
#units.append( NormalUnit( "Lumen", "lumens?|lm", LUMINOUSINTENSITY, 1 ) )          #lumens

#Power
units.append( NormalUnit( "horsepower", "horse ?power", POWER, 745.699872 ) )         #horsepower

#Processes a string, converting freedom units to science units.
def process(message):
    modificableMessage = ModificableMessage(REMOVE_REGEX.sub("", message))
    for u in units:
        u.convert(modificableMessage)
    if modificableMessage.isModified():
        return modificableMessage.getText()
