# This is the library that handles the unit conversion itself.
# The unit conversion library was originally created by ficolas2, https://github.com/ficolas2, 2018/01/21
# The unit conversion library has been modified and updated by ficolas2 and Wendelstein7, https://github.com/Wendelstein7

# Licenced under: MIT License, Copyright (c) 2018 Wendelstein7 and ficolas2

import re
from abc import abstractmethod
from sigfigs import SigFigCompliantNumber

EMPTY_RGX = re.compile("\A\b\Z^$")
ALL_DASHES_RGX_STR = "(\-|‐|‑|–|‒|−|﹘|﹘|﹘)"
PLACE_VALUE_SEPARATOR_RGXS = ["\\.", "\\s", "٬", ",", "('|‘|’|\\`|′)", "_"]
RADIX_RGX_STRS = ["٫", "\\.", "⎖", ","]
NUMBER_RGX_STRS = [(ALL_DASHES_RGX_STR+"?(\\d+)", EMPTY_RGX, EMPTY_RGX)]
for radix in RADIX_RGX_STRS:
    NUMBER_RGX_STRS.append((
        ALL_DASHES_RGX_STR+"?\\d+"+radix+"\\d*",
        EMPTY_RGX,
        re.compile(radix)
    ))
for radix in RADIX_RGX_STRS:
    for pvsep in PLACE_VALUE_SEPARATOR_RGXS:
        if (radix == pvsep):
            continue
        NUMBER_RGX_STRS.append((
            ALL_DASHES_RGX_STR+"?(\\d*)("+pvsep+"(\\d{2,3})+)*"+radix+"(((\\d{2,3})+"+pvsep+")*\\d+)?",
            re.compile(pvsep),
            re.compile(radix)
        ))
        NUMBER_RGX_STRS.append((
            ALL_DASHES_RGX_STR+"?(\\d*)("+pvsep+"(\\d{2,3})+)+",
            re.compile(pvsep),
            re.compile(radix)
        ))
NUMBER_UNIT_SPACERS_RGX = re.compile("\\s*$")
END_NUMBER_RGXS = []
for rgx in NUMBER_RGX_STRS:
    END_NUMBER_RGXS.append((re.compile(rgx[0]+"$"), rgx[1], rgx[2]))
SUPERUNIT_SUBUNIT_SPACER_RGX = re.compile("\\s*$") # TODO make this more effective
REMOVE_REGEX = re.compile("((´|`)+[^>]+(´|`)+)")
FORMAT_CONTROL_REGEX = re.compile("(?<!\\\\)(´|`|\\*|_|~~)|((?<=\n)> |(?<=^)> )")

SIGFIG_COMPLIANCE_LEVEL = 1 # Option: How hard should the bot try to follow sig figs, at the expense of readability?
                            # Value is an int from 0 to 2, where largest is most copmliant and least readable. DEFAULT: 1
USE_TENPOW = False          # Option: Should outputs in scientific notation be like `4*10^3` instead of `4e+3`? DEFAULT: False

class UnitType:

    def __init__( self ):
        self._multiples = {}

    def addMultiple( self, unit, multiple ):
        self._multiples[ multiple ] = unit
        return self

    def getStringFromMultiple(self, value, multiple, SPACING):
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
        return numstr + SPACING + self._multiples[multiple]

    def getString( self, value, SPACING ):
        sortedMultiples = sorted(self._multiples, reverse=True)
        for multiple in sortedMultiples:
            if abs(value) > multiple/2:
                return self.getStringFromMultiple(value, multiple, SPACING)
        return self.getStringFromMultiple( value, sortedMultiples[-1], SPACING )

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

    def toMetric( self, value, SPACING ):
        SIValue = ( value + self._toSIAddition ) * self._toSIMultiplication
        if SIValue == 0:
            if (SIGFIG_COMPLIANCE_LEVEL == 2):
                numstr = str(SIValue)
                if USE_TENPOW:
                    numstr = numstr.replace("e+", "*10^")
                    numstr = numstr.replace("e", "*10^")
                return numstr + SPACING + self._unitType._multiples[1]
            return "0" + SPACING + self._unitType._multiples[1]
        return self._unitType.getString( SIValue, SPACING )

    def getName( self ):
        return self._friendlyName

    def __str__(self):
        return self._friendlyName

    @abstractmethod
    def convert( self, message ): pass

def readNumFromStringEnd( string ):
    bestrgx = None
    bestlen = 0
    for endnumrgx in END_NUMBER_RGXS:
        numberResult = endnumrgx[0].search(string)
        if numberResult is not None:
            if (len(numberResult.group()) > bestlen):
                bestrgx = endnumrgx
                bestlen = len(numberResult.group())
    if (bestrgx is not None):
        numberResult = bestrgx[0].search(string)
        cleanedstring = numberResult.group().strip()
        cleanedstring = bestrgx[1].sub("", cleanedstring)
        cleanedstring = bestrgx[2].sub(".", cleanedstring)
        return (SigFigCompliantNumber(cleanedstring), string[0 : numberResult.start()])

def compromiseBetweenStrings( stringarr ):
    return stringarr[0] # TODO actually implement, this is a dummy.

#NormalUnit class, that follow number + unit name.
class NormalUnit( Unit ):
    def __init__( self, friendlyName, regex, unitType, toSIMultiplication, toSIAddition = 0, key = None ):
        super( NormalUnit, self ).__init__( friendlyName, unitType, toSIMultiplication, toSIAddition )
        self._regex = re.compile( "(" + regex + ")((?=$)|(?=[^a-z]))", re.IGNORECASE )
        if key is None:
            self._key = self
        else:
            self._key = key

    def convert( self, message ):
        originalText = message.getText()
        iterator = self._regex.finditer( originalText )
        replacements = []
        for find in iterator:
            preunitstr = originalText[ 0 : find.start() ]
            value = self.getValueFromIteration(preunitstr)
            if value is None:
                continue
            (preunitstr, usernumber, SPACINGS) = value
            metricValue = self.toMetric(usernumber, compromiseBetweenStrings(SPACINGS))
            repl = {}
            repl[ "start" ] = len(preunitstr)
            repl[ "text"  ] = metricValue
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
    
    def getValueFromIteration(self, string, SPACINGS = []):
        spacerRes = NUMBER_UNIT_SPACERS_RGX.search(string)
        if spacerRes is None:
            return None
        SPACINGS.append(spacerRes.group())
        preunitstr = string[ 0 : spacerRes.start() ]
        read = readNumFromStringEnd(preunitstr)
        if read is None:
            return None
        (usernumber, preunitstr) = read
        nextunitstr = preunitstr[0:SUPERUNIT_SUBUNIT_SPACER_RGX.search(preunitstr).start()]
        for superunit in superunits[self._key]:
            match = superunit[0]._regex.search(nextunitstr)
            if match is None:
                continue
            value = superunit[0].getValueFromIteration(preunitstr[0:match.start()], SPACINGS)
            if value is None:
                continue
            (preunitstr, supernumber, SPACINGS) = value
            ratio = superunit[1]
            print("will add", supernumber * ratio, "imperial units to the converted value")
            # combine supernumber and usernumber into a new value for usernumber
            # gotta make SURE the ratio is cancelled out tho (that is, the value returned is in the subunit, not the superunit)
            # TODO implement
            break
        return (preunitstr, usernumber, SPACINGS)

class CaseSensitiveNormalUnit( NormalUnit ):
    def __init__( self, friendlyName, regex, unitType, toSIMultiplication, toSIAddition = 0, key = None ):
        super( CaseSensitiveNormalUnit, self ).__init__( friendlyName, "(placeholder)", unitType, toSIMultiplication, toSIAddition, key )
        self._regex = re.compile( "(" + regex + ")((?=$)|(?=[^a-zA-Z]))" )

class RegexFlagsExposedNormalUnit( NormalUnit ):
    def __init__( self, friendlyName, regex, flags, unitType, toSIMultiplication, toSIAddition = 0, key = None ):
        super( RegexFlagsExposedNormalUnit, self ).__init__( friendlyName, "(placeholder)", unitType, toSIMultiplication, toSIAddition, key )
        self._regex = re.compile( "(" + regex + ")((?=$)|(?=[^a-zA-Z]))", flags )

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
units.append( NormalUnit( "foot squared", "f(oo|ee)?t ?(\^2|squared|²)", AREA, 0.09290304 ) )       #foot squared
units.append( NormalUnit( "mile squared", "mi(les?)? ?(\^2|squared|²)", AREA, 1609.344**2 ) )       #mile squared
units.append( NormalUnit( "acre", "acres?", AREA, 4046.8564224 ) )                                  #acre
units.append( NormalUnit( "rood", "roods?", AREA, 1011.7141056 ) )                                  #rood

#Volume
units.append( NormalUnit( "pint", "pints?|pt", VOLUME, 0.473176473 ) )                     #pint
units.append( NormalUnit( "quart", "quarts?|qt", VOLUME, 0.946352946 ) )                   #quart
units.append( NormalUnit( "gallon", "gal(lons?)?", VOLUME, 3.785411784 ) )                 #gallon
units.append( NormalUnit( "fluid ounce", "fl\.? oz\.?", VOLUME, 0.0295735295625 ) )        #fluid ounce
units.append( NormalUnit( "teaspoon", "tsp|teaspoons?", VOLUME, 0.00492892159375 ) )       #US teaspoon
units.append( NormalUnit( "tablespoon", "tbsp|tablespoons?", VOLUME, 0.01478676478125 ) )  #US tablespoon
units.append( NormalUnit( "barrel", "drum|barrels?", VOLUME, 158.987294928) )              #barrel
units.append( NormalUnit( "peck", "pecks?", VOLUME, 8.80976754172 ) )                      #pecks
units.append( NormalUnit( "bushel", "bushels?", VOLUME, 35.23907016688 ) )                 #bushels

#Energy
units.append( NormalUnit( "foot-pound", "ft( |\*)?lbf?|foot( |-)pound", ENERGY, 1.3558179483314004 ) )       #foot-pound
units.append( NormalUnit( "British thermal unit", "btu", ENERGY, 1055.05585262 ) )                           #British thermal unit
units.append( CaseSensitiveNormalUnit( "calories", "cal(ories?)?", ENERGY, 4.184 ) )                               #calories
units.append( CaseSensitiveNormalUnit( "kilocalories", "(k(ilo)?c|C)al(ories?)?", ENERGY, 4184 ) )                 #kilocalories
units.append( NormalUnit( "ergs", "ergs?", ENERGY, 10**-7 ) )                                                #ergs

#Force
units.append( NormalUnit( "pound-force", "pound( |-)?force|lbf", FORCE, 4.4482216152605 ) )            #pound-force

#Torque
units.append( NormalUnit( "pound-foot", "Pound(-| )?(f(oo|ee)?t)|lbf( |\*)?ft", TORQUE, 1.3558179483314004 ) )      #pound-foot

#Velocity
units.append( NormalUnit( "miles per hour", "miles? per hour|mph|mi/h", VELOCITY, 0.44704 ) )             #miles per hour
units.append( NormalUnit( "knot", "knots?|kts?", VELOCITY, 1852 / 3600 ) )                              #knots
units.append( NormalUnit( "feet per second", "f(oo|ee)?t ?(per|/|p) ?s(ec|onds?)?", VELOCITY, 0.3048 ) )  #feet per second

#Temperature
units.append( NormalUnit( "degrees fahrenheit", "((°|º|deg(ree)?s?) ?)?(fahrenheit|freedom|f)", TEMPERATURE, 5/9, -32 ) )  #Degrees freedom
units.append( NormalUnit( "degrees rankine", "((°|º|deg(ree)?s?) ?)?(ra?(nkine)?)", TEMPERATURE, 5/9, -491.67 ) )          #Degrees rankine

#Pressure
units.append( NormalUnit( "pound per square inch", "pounds?((-| )?force)? per square in(ch)?|lbf\/in\^2|psi", PRESSURE, 0.0680459639098777333996809617108008 ) ) #Pounds per square inch

#Mass
units.append( NormalUnit( "ounce", "ounces?|oz", MASS, 28.349523125 ) )                     #ounces
units.append( NormalUnit( "pound", "pounds?|lbs?", MASS, 453.59237 ) )                      #pounds
units.append( NormalUnit( "stone", "stones?|(?<!1)st", MASS, 6350.29318 ) )                 #stones
units.append( NormalUnit( "grain", "grains?", MASS, 0.06479891 ) )                          #grains
units.append( NormalUnit( "slug", "slugs?", MASS, 14593.90293720636482939632545931759 ) )   #slug
units.append( NormalUnit( "troy ounce", "troy ?ounces?", MASS, 31.1034768 ) )               #troy ounces
units.append( NormalUnit( "pennyweight", "penny ?weights?", MASS, 1.55517384 ) )            #pennywheight
units.append( NormalUnit( "troy pound", "troy ?pounds?", MASS, 373.2417216 ) )              #troy pound
units.append( NormalUnit( "dram", "drams?", MASS, 1.7718451953125 ) )                       #drams
units.append( NormalUnit( "hundredweight", "hundredweights?|cwt", MASS, 50802.34544 ) )     #hundredweights

#Distance
units.append( NormalUnit( "inch", "inch(es)?", DISTANCE, 0.0254 ) )                           #inch
units.append( NormalUnit( "foot", "f(oo|ee)?t", DISTANCE, 0.3048 ) )                      #foot
units.append( NormalUnit( "mile", "mi(les?)?", DISTANCE, 1609.344 ) )                         #mile
units.append( NormalUnit( "yard", "yd|yards?", DISTANCE, 0.9144 ) )                           #yard
units.append( NormalUnit( "nautical mile", "nautical ?(mi(les?)?)?|nmi", DISTANCE, 1852 ) )   #nautical miles
units.append( NormalUnit( "thou", "thou", DISTANCE, 0.0000254 ) )                             #thou
units.append( NormalUnit( "fathom", "fathoms?", DISTANCE, 1.8288 ) )                          #fathom
units.append( NormalUnit( "furlong", "furlongs?", DISTANCE, 201.168 ) )                      #furlong
units.append( NormalUnit( "rack unit", "rack ?units?|ru", DISTANCE, 0.04445 ) )               #rack units
units.append( NormalUnit( "smoot", "smoots?", DISTANCE, 1.7018 ) )                            #Smoot units

#Luminous intensity
#units.append( NormalUnit( "Lumen", "lumens?|lm", LUMINOUSINTENSITY, 1 ) )          #lumens

#Power
units.append( NormalUnit( "horsepower", "horse ?power", POWER, 745.69987158227022 ) )         #horsepower
units.append( NormalUnit( "ton of refrigeration", "ton of refrigeration", POWER, 10550.5585262 / 3 ) )                    #ton of refrigeration

# END UNIT DEFINITIONS
# BEGIN SUPERUNIT DEFINITIONS

superunits = {}
for key in units:
    superunits[key] = []
    if (key._toSIAddition != 0):
        continue
    for potentialsuperunit in units:
        if (key._unitType != potentialsuperunit._unitType):
            continue
        if (key == potentialsuperunit):
            continue
        if (potentialsuperunit._toSIAddition != 0):
            continue
        ratio = potentialsuperunit._toSIMultiplication / key._toSIMultiplication
        if (abs(ratio - round(ratio)) > 1.0e-6):
            continue
        ratio = round(ratio)
        if (ratio <= 1):
            continue
        if (isinstance(potentialsuperunit, NormalUnit)):
            superunits[key].append((RegexFlagsExposedNormalUnit(
                potentialsuperunit._friendlyName,
                potentialsuperunit._regex.pattern + "(?=$)",
                potentialsuperunit._regex.flags,
                potentialsuperunit._unitType,
                potentialsuperunit._toSIMultiplication,
                potentialsuperunit._toSIAddition, # this is always zero
                potentialsuperunit
            ), ratio))
        else:
            print("Superuniting is not supported for " + type(potentialsuperunit) + "!")
            print("Somebody must've added some code but not fully integrated it *shoves work at you*")
            print("Or maybe somebody made a class that COULD subclass NormalUnit but just didn't for no reason.")
            print("That would be nice, it means I just shoved less work at you.")

#Processes a string, converting freedom units to science units.
def process(message):
    modificableMessage = ModificableMessage(message) # REMOVE_REGEX.sub("", message)
    for u in units:
        u.convert(modificableMessage)
    if modificableMessage.isModified():
        return modificableMessage.getText()
