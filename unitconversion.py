# This is the library that handles the unit conversion itself.
# The unit conversion library was originally created by ficolas2, https://github.com/ficolas2, 2018/01/21
# The unit conversion library has been modified and updated by ficolas2 and Wendelstein7, https://github.com/Wendelstein7

# Licenced under: MIT License, Copyright (c) 2018 Wendelstein7 and ficolas2

from typing import Any, Callable, Dict, Optional, Tuple, Union, List
from math import log10
from abc import abstractmethod
import re

from compiledregexes import *
from stringcompromise import compromiseBetweenStrings
from modificablemessage import ModificableMessage
from numberparsing import NUMBER_PARSERS, NumberParser, ParserSupportsSigFigs
from sigfigs import SigFigCompliantNumber

SIGFIG_COMPLIANCE_LEVEL = 500   # Option: How hard should the bot try to follow sig figs, at the expense of readability?
                                # Value is an int from 0 to 1000, where largest is most copmliant and least readable. DEFAULT: 500
ASSUME_DECIMAL_INCHES = True    # Option: Should the notation 5'4.25 be assumed to be a foot-inch measurement, or will only integral
                                # values like 5'4 be implicitaly assumed to have inch measurements?

class UnitType:

    def __init__( self ):
        self._multiples = {} # type: Dict[float, str]
        self._cutoffs = {} # type: Dict[float, float]
        self._labelStrings = [] # type: List[str]
        unitTypes.append(self)

    def addMultiple( self, unit, multiple, cutoff = 0.5 ):
        # type: (str, float, float) -> UnitType
        self._multiples[ multiple ] = unit
        self._cutoffs[ multiple ] = cutoff
        self._labelStrings.append(unit)
        return self

    def getStringFromMultiple( self, value, multiple, spacing, parser ):
        # type: (Union[SigFigCompliantNumber, float], float, str, NumberParser) -> str
        if (SIGFIG_COMPLIANCE_LEVEL <= 200 and isinstance(value, SigFigCompliantNumber)):
            if not isinstance(parser, ParserSupportsSigFigs):
                raise TypeError("SigFigCompliantNumbers should have parsers that are instances of ParserSupportsSigFigs")
            numstr = str(value / multiple)
            result = parser.getRadixRegex().search(numstr)
            if (result is not None and result.end() == len(numstr)):
                numstr = numstr[0:result.start()]
            result = parser.getScinotRegex().search(numstr)
            if (result is not None):
                numstr = str(parser.parseNumber([numstr]))
                if (parser.getScinotRegex().search(numstr) is None and parser.getRadixRegex().search(numstr) is not None):
                    while numstr.endswith(parser.createValuelessDigit()):
                        numstr = numstr[0:-len(parser.createValuelessDigit())]
                    match = parser.getRadixRegex().finditer(numstr).__next__()
                    if (match.end() == len(numstr)):
                        numstr = numstr[0:match.start()]
        else:
            numstrs = parser.createStrings(value / multiple)
            if (len(numstrs) != 1):
                raise NotImplementedError("Not configured to handle noncontiguous numbers!")
            numstr = numstrs[0]
        return numstr + spacing + self._multiples[multiple]

    def getString( self, value, spacing, parser ):
        # type: (Union[SigFigCompliantNumber, float], str, NumberParser) -> str
        sortedMultiples = sorted(self._multiples, reverse=True)
        for multiple in sortedMultiples:
            if abs(value) > multiple * self._cutoffs[multiple]:
                return self.getStringFromMultiple( value, multiple, spacing, parser )
        return self.getStringFromMultiple( value, sortedMultiples[-1], spacing, parser )

    def getLabelStrings( self ):
        # type: () -> List[str]
        return self._labelStrings

unitTypes = [] # type: List[UnitType]

DISTANCE = UnitType().addMultiple("m", 1, 3.5).addMultiple( "km", 10**3 ).addMultiple( "cm", 10**-2).addMultiple( "mm", 10**-3).addMultiple( "µm", 10**-6).addMultiple( "nm", 10**-9).addMultiple( "pm", 10**-12 )
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

LABEL_STRING_START_RGXS = [] # type: List[re.Pattern]
for unitType in unitTypes:
    for labelString in unitType.getLabelStrings():
        LABEL_STRING_START_RGXS.append(re.compile("^"+re.escape(labelString)+"($|[^a-zA-Z])"))

class Unit:
    def __init__( self, friendlyName, unitType, toSIMultiplication, toSIAddition ):
        # type: (str, UnitType, float, float) -> None
        self._friendlyName = friendlyName # type: str
        self._unitType = unitType # type: UnitType
        self._toSIMultiplication = toSIMultiplication # type: float
        self._toSIAddition = toSIAddition # type: float

    def toMetric( self, value, spacing, parser ):
        # type: (Union[float, SigFigCompliantNumber], str, NumberParser) -> str
        SIValue = ( value + self._toSIAddition ) * self._toSIMultiplication
        if SIValue == 0:
            if (SIGFIG_COMPLIANCE_LEVEL >= 900 and isinstance(SIValue, SigFigCompliantNumber)):
                return str(SIValue) + spacing + self._unitType._multiples[1]
            strs = parser.createStrings(0)
            if (len(strs) > 1):
                raise NotImplementedError("Does not yet support noncontiguous numbers!")
            return strs[0] + spacing + self._unitType._multiples[1]
        return self._unitType.getString( SIValue, spacing, parser )

    def getName( self ):
        # type: () -> str
        return self._friendlyName

    def __str__(self):
        return self._friendlyName

    @abstractmethod
    def convert( self, message, locale ):
        # type: (ModificableMessage, NumberParser) -> None
        pass

class SupportsSuperunit(Unit):
    # this class is a stub, because I'm not sure what to put here because there's not utilization of the generality it provides, yet
    pass

#NormalUnit class, that follow number + unit name.
class NormalUnit( SupportsSuperunit, Unit ):
    def __init__( self, friendlyName, regex, unitType, toSIMultiplication, toSIAddition = 0, key = None ):
        # type: (str, str, UnitType, float, float, SupportsSuperunit) -> None
        super( NormalUnit, self ).__init__( friendlyName, unitType, toSIMultiplication, toSIAddition )
        self._regex = re.compile( "(" + regex + ")((?=$)|(?=[^a-z]))", re.IGNORECASE ) # type: re.Pattern
        self._key = self # type: SupportsSuperunit
        if key is not None:
            self._key = key

    def convert( self, message, locale ):
        # type: (ModificableMessage, NumberParser) -> None
        originalText = message.getText()
        iterator = self._regex.finditer( originalText )
        replacements = []
        for find in iterator:
            preunitstr = originalText[ 0 : find.start() ]
            value = self.getValueFromIteration(preunitstr, locale, [])
            if value is None:
                continue
            (preunitstr, usernumber, spacings, conversionFormula) = value
            end = find.end()
            # here lies one of the extremely special cases
            if (self._friendlyName == "foot"):
                end2 = SUPERUNIT_SUBUNIT_SPACER_START_RGX.finditer(originalText[end:]).__next__().end() + end
                (numstrings, remstrs) = locale.takeNumberFromStringStart(originalText[end2:], False)
                if len(numstrings) > 0:
                    if (len(numstrings) > 1 or len(remstrs) > 1):
                        raise NotImplementedError("Does not yet support noncontiguous numbers!")
                    numstring = numstrings[0]
                    remstr = remstrs[0]
                    spclen = NUMBER_UNIT_SPACERS_START_RGX.finditer(remstr).__next__().end()
                    remstr = remstr[spclen:]
                    end2 += len(numstring)
                    belongstoother=False
                    for unit in units:
                        if (isinstance(unit, NormalUnit)):
                            pmatch = unit._regex.search(remstr)
                            if ((pmatch is not None) and (pmatch.start() == 0)):
                                belongstoother = True
                                break
                        else:
                            raise NotImplementedError("Cannot ensure number is not explicitly part of unit " + str(unit) + " of type " + str(type(unit)) + "!")
                    for labelStringRgx in LABEL_STRING_START_RGXS:
                        if (labelStringRgx.search(remstr) is not None):
                            belongstoother = True
                            break
                    if not belongstoother:
                        if isinstance(locale, ParserSupportsSigFigs):
                            actualnumSFcompli = SigFigCompliantNumber(numstring, locale)
                            if actualnumSFcompli < 12 and actualnumSFcompli >= 0:
                                radixcheck = locale.getRadixRegex().search(numstring)
                                if (radixcheck is None) or (radixcheck.end() == len(numstring)) or ASSUME_DECIMAL_INCHES:
                                    ratio = 12
                                    terminatingradix = (radixcheck is not None) and (radixcheck.end() == len(numstring))
                                    end = end2 if not terminatingradix else end2-1
                                    usernumber = actualnumSFcompli.addNumberOnLargerScale(usernumber, ratio, terminatingradix) / ratio
                        else:
                            actualnum = locale.parseNumber([numstring])
                            if not isinstance(usernumber, (int, float)):
                                raise RuntimeError("Inconsistent internal behavior!")
                            if actualnum < 12 and actualnum >= 0:
                                ratio = 12
                                usernumber = actualnum / ratio + usernumber
                                end = end2
            if (SIGFIG_COMPLIANCE_LEVEL <= 600 and isinstance(usernumber, SigFigCompliantNumber)):
                # special sig fig cases that assume what people mean by colloquial measurements rather than strictly using what they say
                if (self._friendlyName == "inch"):
                    if (usernumber / (10**int(log10(usernumber._value))) > 10 / 2.54):
                        usernumber._leastSignificantDigit += 1
                        usernumber._numSigFigs += 1
                if (self._friendlyName == "foot"):
                    if (usernumber / (10**int(log10(usernumber._value))) > 10 / 3.048):
                        usernumber._leastSignificantDigit += 1
                        usernumber._numSigFigs += 1
            metricValue = conversionFormula(usernumber, compromiseBetweenStrings(spacings), locale)
            repl = {} # type: Dict[str, Any]
            repl[ "start" ] = len(preunitstr)
            repl[ "text"  ] = metricValue
            repl[ "end" ] = end
            replacements.append(repl)
        if len(replacements)>0:
            lastPoint = 0
            finalMessage = ""
            for repl in replacements:
                finalMessage += originalText[ lastPoint: repl[ "start" ] ] + repl[ "text" ]
                lastPoint = repl["end"]
            finalMessage += originalText[ lastPoint : ]
            message.setText(finalMessage)

    def getValueFromIteration(
                            self,
                            string, # type: str
                            parser, # type: NumberParser
                            spacings = [] # type: List[str]
                            ):
        # type: (...) -> Optional[Tuple[str, Union[SigFigCompliantNumber, float], List[str], Callable[[Union[float, SigFigCompliantNumber], str, NumberParser], str]]]
        spacerRes = NUMBER_UNIT_SPACERS_END_RGX.search(string)
        if spacerRes is None:
            return None
        spacing = spacerRes.group()
        preunitstr = string[ 0 : spacerRes.start() ]
        read = parser.takeNumberFromStringEnd(preunitstr)
        if read is None:
            return None
        (nums, notnums) = read
        if (len(nums) > 1 or len(notnums) > 1):
            raise NotImplementedError("Noncontinguous numbers not supported!")
        usernumber : Union[SigFigCompliantNumber, float] = 0
        if isinstance(parser, ParserSupportsSigFigs):
            usernumber = SigFigCompliantNumber(nums[0], parser)
        else:
            usernumber = parser.parseNumber(nums)
        preunitstr = "" if len(notnums) == 0 else notnums[0]
        spacer = SUPERUNIT_SUBUNIT_SPACER_END_RGX.finditer(preunitstr).__next__()
        nextunitstr = preunitstr[0:spacer.start()]
        match = None
        for superunit in superunits[self._key]:
            if (isinstance(superunit[0], NormalUnit)):
                match = superunit[0]._regex.search(nextunitstr)
                if match is None:
                    continue
                value = superunit[0].getValueFromIteration(preunitstr[0:match.start()], parser, spacings)
                if value is None:
                    continue
                if ((SUPERUNIT_SUBUNIT_SPACER_START_RGX.search(nums[0]) is not None) and (spacer.span()[1] == spacer.span()[0])):
                    nums[0] = nums[0][1:]
                    usernumber = parser.parseNumber(nums)
                (preunitstr, supernumber, spacings, _) = value
                ratio = superunit[1]
                if isinstance(usernumber, SigFigCompliantNumber):
                    if not isinstance(parser, ParserSupportsSigFigs):
                        raise RuntimeError("Inconsistent internal behavior!")
                    usernumber = usernumber.addNumberOnLargerScale(supernumber, ratio, parser.getRadixRegex().search(nums[0]) is not None)
                else:
                    usernumber = usernumber + supernumber * ratio
                break
            else:
                raise NotImplementedError("Superuniting is not supported for unit type " + str(type(potentialsuperunit)) + "!")
        conversionFormula = self.toMetric
        # here lies one of the extremely special cases
        if (match is None and self._friendlyName == "ounce"):
            for superunit in superunits[unit_by_name_lookup["fluid ounce"]]:
                if (isinstance(superunit[0], NormalUnit)):
                    match = superunit[0]._regex.search(nextunitstr)
                    if match is None:
                        continue
                    value = superunit[0].getValueFromIteration(preunitstr[0:match.start()], parser, spacings)
                    if value is None:
                        continue
                    if ((SUPERUNIT_SUBUNIT_SPACER_START_RGX.search(nums[0]) is not None) and (spacer.span()[1] == spacer.span()[0])):
                        nums[0] = nums[0][1:]
                        usernumber = parser.parseNumber(nums)
                    (preunitstr, supernumber, spacings, _) = value
                    ratio = superunit[1]
                    if isinstance(usernumber, SigFigCompliantNumber):
                        if not isinstance(parser, ParserSupportsSigFigs):
                            raise RuntimeError("Inconsistent internal behavior!")
                        usernumber = usernumber.addNumberOnLargerScale(supernumber, ratio, parser.getRadixRegex().search(nums[0]) is not None)
                    else:
                        usernumber = usernumber + supernumber * ratio
                    conversionFormula = unit_by_name_lookup["fluid ounce"].toMetric
                    break
        spacings.insert(0, spacing)
        return (preunitstr, usernumber, spacings, conversionFormula)

class CaseSensitiveNormalUnit( NormalUnit ):
    def __init__( self, friendlyName, regex, unitType, toSIMultiplication, toSIAddition = 0, key = None ):
        # type: (str, str, UnitType, float, float, SupportsSuperunit) -> None
        super( CaseSensitiveNormalUnit, self ).__init__( friendlyName, "(placeholder)", unitType, toSIMultiplication, toSIAddition, key )
        self._regex = re.compile( "(" + regex + ")((?=$)|(?=[^a-zA-Z]))" )

class RegexFlagsExposedNormalUnit( NormalUnit ):
    def __init__( self, friendlyName, regex, flags, unitType, toSIMultiplication, toSIAddition = 0, key = None ):
        # type: (str, str, int, UnitType, float, float, SupportsSuperunit) -> None
        super( RegexFlagsExposedNormalUnit, self ).__init__( friendlyName, "(placeholder)", unitType, toSIMultiplication, toSIAddition, key )
        self._regex = re.compile( "(" + regex + ")((?=$)|(?=[^a-zA-Z]))", flags )

units = [] # type: List[Unit]

# every unit must be defined before its superunits, so unit definitions are sorted by size

#Area
units.append( NormalUnit( "inch squared", "in(ch(es)?)? ?(\^2|squared|²)", AREA, 0.00064516 ) )     #inch squared
units.append( NormalUnit( "foot squared", "f(oo|ee)?t ?(\^2|squared|²)", AREA, 0.09290304 ) )       #foot squared
units.append( NormalUnit( "rood", "roods?", AREA, 1011.7141056 ) )                                  #rood
units.append( NormalUnit( "acre", "acres?", AREA, 4046.8564224 ) )                                  #acre
units.append( NormalUnit( "mile squared", "mi(les?)? ?(\^2|squared|²)", AREA, 2589988.110336 ) )    #mile squared

#Mass
units.append( NormalUnit( "grain", "grains?", MASS, 0.06479891 ) )                          #grains
units.append( NormalUnit( "pennyweight", "penny ?weights?|dwt", MASS, 1.55517384 ) )        #pennywheight
units.append( NormalUnit( "dram", "drams?", MASS, 1.7718451953125 ) )                       #drams
units.append( NormalUnit( "ounce", "ounces?|(oz(?! t))", MASS, 28.349523125 ) )             #ounces
units.append( NormalUnit( "troy ounce", "troy ?ounces?|oz t", MASS, 31.1034768 ) )          #troy ounces
units.append( NormalUnit( "troy pound", "troy ?pounds?", MASS, 373.2417216 ) )              #troy pound
units.append( NormalUnit( "pound", "pounds?|lbs?", MASS, 453.59237 ) )                      #pounds
units.append( NormalUnit( "stone", "stones?|(?<!1)st", MASS, 6350.29318 ) )                 #stones
units.append( NormalUnit( "slug", "slugs?", MASS, 14593.90293720636482939632545931759 ) )   #slug
units.append( NormalUnit( "hundredweight", "hundredweights?|cwt", MASS, 50802.34544 ) )     #hundredweights

#Volume
units.append( NormalUnit( "teaspoon", "tsp|teaspoons?", VOLUME, 0.00492892159375 ) )                 #US teaspoon
units.append( NormalUnit( "tablespoon", "tbsp|tablespoons?", VOLUME, 0.01478676478125 ) )            #US tablespoon
units.append( NormalUnit( "fluid ounce", "fl(\\.|uid)? o(z\\.?|unces)", VOLUME, 0.0295735295625 ) )  #fluid ounce
units.append( NormalUnit( "pint", "pints?|pt", VOLUME, 0.473176473 ) )                               #pint
units.append( NormalUnit( "quart", "quarts?|qt", VOLUME, 0.946352946 ) )                             #quart
units.append( NormalUnit( "gallon", "gal(lons?)?", VOLUME, 3.785411784 ) )                           #gallon
units.append( NormalUnit( "peck", "pecks?", VOLUME, 8.80976754172 ) )                                #pecks
units.append( NormalUnit( "bushel", "bushels?", VOLUME, 35.23907016688 ) )                           #bushels
units.append( NormalUnit( "barrel", "drum|barrels?", VOLUME, 158.987294928) )                        #barrel

#Energy
units.append( NormalUnit( "ergs", "ergs?", ENERGY, 10**-7 ) )                                                #ergs
units.append( NormalUnit( "foot-pound", "ft( |\*)?lbf?|foot( |-)pound", ENERGY, 1.3558179483314004 ) )       #foot-pound
units.append( CaseSensitiveNormalUnit( "calories", "cal(ories?)?", ENERGY, 4.184 ) )                         #calories
units.append( NormalUnit( "British thermal unit", "btu", ENERGY, 1055.05585262 ) )                           #British thermal unit
units.append( CaseSensitiveNormalUnit( "kilocalories", "(k(ilo)?c|C)al(ories?)?", ENERGY, 4184 ) )           #kilocalories

#Force
units.append( NormalUnit( "pound-force", "pound( |-)?force|lbf", FORCE, 4.4482216152605 ) )            #pound-force

#Torque
units.append( NormalUnit( "pound-foot", "Pound(-| )?(f(oo|ee)?t)|lbf( |\*)?ft", TORQUE, 1.3558179483314004 ) )      #pound-foot

#Velocity
units.append( NormalUnit( "feet per second", "f(oo|ee)?t ?(per|/|p) ?s(ec|onds?)?", VELOCITY, 0.3048 ) )  #feet per second
units.append( NormalUnit( "miles per hour", "miles? per hour|mph|mi/h", VELOCITY, 0.44704 ) )             #miles per hour
units.append( NormalUnit( "knot", "knots?|kts?", VELOCITY, 1852 / 3600 ) )                                #knots

#Temperature
units.append( NormalUnit( "degrees fahrenheit", "((°|º|deg(ree)?s?) ?)?(fahrenheit|freedom|f)", TEMPERATURE, 5/9, -32 ) )  #Degrees freedom
units.append( NormalUnit( "degrees rankine", "((°|º|deg(ree)?s?) ?)?(ra?(nkine)?)", TEMPERATURE, 5/9, -491.67 ) )          #Degrees rankine

#Pressure
units.append( NormalUnit( "pound per square inch", "pounds?((-| )?force)? per square in(ch)?|lbf\/in\^2|psi", PRESSURE, 0.0680459639098777333996809617108008 ) ) #Pounds per square inch

#Distance
units.append( NormalUnit( "thou", "thou", DISTANCE, 0.0000254 ) )                                   #thou
units.append( NormalUnit( "inch", "\"|in(ch(es)?)?", DISTANCE, 0.0254 ) )                           #inch
units.append( NormalUnit( "rack unit", "rack ?units?|ru", DISTANCE, 0.04445 ) )                     #rack units
units.append( NormalUnit( "foot", ALL_PRIMES_RGX_STR+"|f(oo|ee)?t", DISTANCE, 0.3048 ) )            #foot
units.append( NormalUnit( "yard", "yd|yards?", DISTANCE, 0.9144 ) )                                 #yard
units.append( NormalUnit( "smoot", "smoots?", DISTANCE, 1.7018 ) )                                  #Smoot units
units.append( NormalUnit( "fathom", "fathoms?", DISTANCE, 1.8288 ) )                                #fathom
units.append( NormalUnit( "furlong", "furlongs?", DISTANCE, 201.168 ) )                             #furlong
units.append( NormalUnit( "mile", "mi(les?)?", DISTANCE, 1609.344 ) )                               #mile
units.append( NormalUnit( "nautical mile", "nautical ?(mi(les?)?)?|nmi", DISTANCE, 1852 ) )         #nautical miles

#Luminous intensity
#units.append( NormalUnit( "Lumen", "lumens?|lm", LUMINOUSINTENSITY, 1 ) )          #lumens

#Power
units.append( NormalUnit( "horsepower", "horse ?power", POWER, 745.69987158227022 ) )                            #horsepower
units.append( NormalUnit( "ton of refrigeration", "ton of refrigeration", POWER, 10550.5585262 / 3 ) )           #ton of refrigeration

# END UNIT DEFINITIONS
# BEGIN SUPERUNIT DEFINITIONS

superunits = {} # type: Dict[Unit, List[Tuple[SupportsSuperunit, int]]]
superunits_by_name_lookup = {} # type: Dict[str, SupportsSuperunit]
unit_by_name_lookup = {} # type: Dict[str, Unit]
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
            superunits_by_name_lookup[potentialsuperunit._friendlyName] = RegexFlagsExposedNormalUnit(
                potentialsuperunit._friendlyName,
                potentialsuperunit._regex.pattern + "(?=$)",
                potentialsuperunit._regex.flags,
                potentialsuperunit._unitType,
                potentialsuperunit._toSIMultiplication,
                potentialsuperunit._toSIAddition, # this is always zero
                potentialsuperunit
            )
        else:
            if isinstance(potentialsuperunit, SupportsSuperunit):
                raise NotImplementedError("Superuniting is not supported for unit type " + str(type(potentialsuperunit)) + "!")
    unit_by_name_lookup[key._friendlyName] = key

#Processes a string, converting freedom units to science units.
def process(message, locales = ["en_US"]):
    # type: (str, List[str]) -> Optional[ModificableMessage]
    modificableMessage = ModificableMessage(message) # REMOVE_REGEX.sub("", message)
    for u in units:
        for locale in locales:
            u.convert(modificableMessage, NUMBER_PARSERS[locale])
    if modificableMessage.isModified():
        return modificableMessage.getText()
    return None
