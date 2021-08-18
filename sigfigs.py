from math import isfinite, log10, floor, sqrt
from typing import SupportsAbs, Union, Tuple
from numberparsing import ParserSupportsSigFigs

class SigFigCompliantNumber(SupportsAbs):

    def __init__(
            self,
            stringRepresentation, # type: Union[str, float]
            parser, # type: ParserSupportsSigFigs
            *,
            exact = False, # type: bool
            sigfigs = None, # type: int
            leastsigdig = None # type: int
    ):
        # type: (...) -> None
        self._parser = parser
        if ((exact and sigfigs is not None) or (exact and leastsigdig is not None)):
            raise ValueError("Cannot specify sig figs / places on an exact number!")
        if isinstance(stringRepresentation, (int, float)):
            self._value = stringRepresentation
        else:
            self._value = parser.parseNumber([stringRepresentation])
        self._isNan = False
        self._isZero = False
        if (self._value == 0):
            if (sigfigs != None):
                raise ValueError("Cannot specify sig figs on zero!")
            self._isZero = True
            if exact:
                self._leastSignificantDigit = MAX_SIG_FIGS
                return
            if (leastsigdig is not None):
                self._leastSignificantDigit = leastsigdig
                return
            if not isinstance(stringRepresentation, str):
                raise TypeError("Can only determine the number of significant digits from a string")
            self._leastSignificantDigit = leastSigDigit(stringRepresentation, parser)
            return
        if (not isfinite(self._value)):
            self._isNan = True
            return
        if exact:
            self._numSigFigs = MAX_SIG_FIGS
            self._leastSignificantDigit = -int(floor(log10(abs(self._value))))+MAX_SIG_FIGS-1
            return
        if (sigfigs is None and leastsigdig is None):
            if not isinstance(stringRepresentation, str):
                raise TypeError("Can only determine the number of significant digits from a string")
            self._numSigFigs = numSigFigs(stringRepresentation, parser)
            self._leastSignificantDigit = -int(floor(log10(abs(self._value))))+self._numSigFigs-1
        if (sigfigs is not None):
            self._numSigFigs = sigfigs
            self._leastSignificantDigit = -int(floor(log10(abs(self._value))))+self._numSigFigs-1
        if (leastsigdig is not None):
            self._leastSignificantDigit = leastsigdig
            self._numSigFigs = self._leastSignificantDigit+1+int(floor(log10(abs(self._value))))
        if (sigfigs is not None and sigfigs != self._numSigFigs):
            raise ValueError("Incongruity created!")
        if (leastsigdig is not None and leastsigdig != self._leastSignificantDigit):
            raise ValueError("Incongruity created!")
    
    # assumes that this SigFigCompliantNumber was generated as part of a measurement on multiple scales
    # then, it increases this measurement by an appropriate amount, using the same scale as before
    # but with another measurement on a scale that is larger by an integer ratio added in
    def addNumberOnLargerScale(self, largerNumber, ratio, fixToIntegerPrecision = False):
        return combineSuperAndSubunits(largerNumber, self, ratio, fixToIntegerPrecision)

    # this string output value is based on the parser given to the sigfigcompliantnumber when it was constructed
    def __str__(self):
        if (self._isZero):
            return self._parser.createScientificString(0, -self._leastSignificantDigit)
        if (self._isNan):
            strs = self._parser.createStrings(float("nan"))
            if (len(strs) != 1):
                raise NotImplementedError("Noncontiguous number in measurement context is not supported!")
            return strs[0]
        return roundsignificant(self._value, self._numSigFigs, self._parser)

    # all math operations should behave under effectively the same contract as the python float class
    # if a nonunary operation has a parameter that can be converted to a float rather than a sigfigcompliantnumber, it is converted and treated as exact
    # operations return sigfigcompliantnumbers to indicate the precision embedded in the calculation and its inputs

    def __add__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            if (self._isNan or other._isNan):
                return SigFigCompliantNumber(self._value + other._value, self._parser)
            return SigFigCompliantNumber(self._value + other._value, self._parser, leastsigdig=min(self._leastSignificantDigit, other._leastSignificantDigit))
        else:
            return self + SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __sub__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            if (self._isNan or other._isNan):
                return SigFigCompliantNumber(self._value - other._value, self._parser)
            return SigFigCompliantNumber(self._value - other._value, self._parser, leastsigdig=min(self._leastSignificantDigit, other._leastSignificantDigit))
        else:
            return self - SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __mul__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            if (self._isNan or other._isNan):
                return SigFigCompliantNumber(self._value * other._value, self._parser)
            if (self._isZero):
                outLeastSigDigit = self._leastSignificantDigit
                outLeastSigDigit -= int(round(log10(other._value)))
                return SigFigCompliantNumber(0, self._parser, leastsigdig=outLeastSigDigit)
            if (other._isZero):
                outLeastSigDigit = other._leastSignificantDigit
                outLeastSigDigit -= int(round(log10(self._value)))
                return SigFigCompliantNumber(0, self._parser, leastsigdig=outLeastSigDigit)
            return SigFigCompliantNumber(self._value * other._value, self._parser, sigfigs=min(self._numSigFigs, other._numSigFigs))
        else:
            return self * SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __truediv__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            if (other._isZero):
                raise ZeroDivisionError("SigFigCompliantNumber division by zero")
            if (self._isNan or other._isNan):
                return SigFigCompliantNumber(self._value + other._value, self._parser)
            if (self._isZero):
                outLeastSigDigit = self._leastSignificantDigit
                outLeastSigDigit += int(round(log10(other._value)))
                return SigFigCompliantNumber(0, self._parser, leastsigdig=outLeastSigDigit)
            return SigFigCompliantNumber(self._value / other._value, self._parser, sigfigs=min(self._numSigFigs, other._numSigFigs))
        else:
            return self / SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __lt__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self._value < other._value
        else:
            return self < SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __le__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self._value <= other._value
        else:
            return self <= SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __ne__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self._value != other._value
        else:
            return self != SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __eq__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self._value == other._value
        else:
            return self == SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __gt__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self._value > other._value
        else:
            return self > SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __ge__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self._value >= other._value
        else:
            return self >= SigFigCompliantNumber(other, self._parser, exact=True)
    
    def __abs__(self):
        if (self._value >= 0):
            return self
        else:
            return SigFigCompliantNumber(-self._value, self._parser, sigfigs=self._numSigFigs, leastsigdig=self._leastSignificantDigit)

MAX_SIG_FIGS = 1024

def combineSuperAndSubunits(superunitval, subunitval, ratio, subunithasdot = False):
    # type: (SigFigCompliantNumber, SigFigCompliantNumber, int, bool) -> SigFigCompliantNumber
    if (subunitval > ratio or subunitval._leastSignificantDigit > 0 or subunitval < 0 or subunithasdot):
        subunitval += (superunitval * ratio)._value
        superunitoverprecision = (superunitval * ratio)._leastSignificantDigit - subunitval._leastSignificantDigit
        if (superunitoverprecision > 0):
            subunitval._numSigFigs += superunitoverprecision
            subunitval._leastSignificantDigit += superunitoverprecision
    else:
        (_, denom) = toLowestTerms(int(subunitval._value), ratio)
        mindec = int(log10(5*denom))
        superunitval += subunitval / ratio
        superunitunderprecision = mindec - superunitval._leastSignificantDigit
        if (superunitunderprecision > 0):
            superunitval._numSigFigs += superunitunderprecision
            superunitval._leastSignificantDigit += superunitunderprecision
        subunitval = superunitval * ratio
    return subunitval

def numSigFigs(string, parser):
    # type: (str, ParserSupportsSigFigs) -> int
    lzs = 0
    (_, string) = parser.getPositive(string)
    exp = parser.getScinotRegex().search(string)
    if exp is not None:
        string = string[:exp.start()]
    radixMatch = parser.getRadixRegex().search(string)
    rmlength = 0 if radixMatch is None else len(radixMatch.group())
    while((string[lzs] == parser.createValuelessDigit()) or (radixMatch is not None and (radixMatch.start() >= lzs and radixMatch.end() < lzs))):
        lzs += 1
        if (lzs == len(string)):
            return 0
    if (radixMatch is not None):
        if (radixMatch.start() >= lzs):
            return len(string) - lzs - rmlength
        if (radixMatch.start() >= 0):
            return len(string) - lzs
        raise RuntimeError("Internally inconsistent behavior!")
    tzs = len(string) - 1
    while(string[tzs] == parser.createValuelessDigit()):
        tzs -= 1
    return tzs - lzs + 1

# precondition: string is a full-form int, not terminated with a radix
def scientificnotation(string, sigfigs, parser):
    # type: (str, int, ParserSupportsSigFigs) -> str
    i=1
    (ispos, abs_) = parser.getPositive(string)
    out = abs_[0] + parser.createRadix()
    while(i<sigfigs):
        out += abs_[i]
        i += 1
    return parser.setPositive(parser.createScientificString(out, len(abs_)-1), ispos)

# precondition: number is not zero
def roundsignificant(number, sigfigs, parser):
    # type: (float, int, ParserSupportsSigFigs) -> str
    if sigfigs == 0:
        strs = parser.createStrings(0)
        if (len(strs) != 1):
            raise NotImplementedError("Noncontiguous number in measurement context is not supported!")
        return strs[0]
    scinot = False
    digits = -int(floor(log10(abs(number))))+sigfigs-1
    digits = -int(floor(log10(abs(round(number, digits)))))+sigfigs-1
    rounded = round(number, digits)
    if (digits <= 0):
        if ("e" in str(float(number))):
            scinot = True
        rounded = round(rounded)
    out = str(rounded)
    if (digits > 0):
        addex = len(out)
        if ("e" in out):
            addex = out.find("e")
        if ((parser.getRadixRegex().search(out) is None) and sigfigs > 1):
            out = out[0:addex] + parser.createRadix() + out[addex:len(out)]
            addex += 1
        while (numSigFigs(out, parser) < sigfigs):
            out = out[0:addex] + parser.createValuelessDigit() + out[addex:len(out)]
        return parser.reformat(out)
    bad = numSigFigs(out, parser) != sigfigs
    if (scinot or (bad and digits != 0)):
        return scientificnotation(out, sigfigs, parser)
    if (bad and digits == 0):
        return parser.reformat(out) + parser.createRadix()
    return parser.reformat(out)

def leastSigDigit(string, parser):
    # type: (str, ParserSupportsSigFigs) -> int
    postdecimal = parser.getRadixRegex().search(string)
    pdlen = 0
    if postdecimal is not None:
        pdlen = len(string) - postdecimal.end()
    exponential = parser.getScinotRegex().search(string)
    evalu = 0
    if exponential is not None:
        evalu = int(string[exponential.end():])
    return pdlen - evalu

def toLowestTerms(a, b):
    # type: (int, int) -> Tuple[int, int]
    negative = False
    if ((a<0) ^ (b<0)):
        negative = True
    a = abs(a)
    b = abs(b)
    if a == 0:
        return (0, 1)
    if (b/a == int(b/a)):
        return (1, int(b/a))
    x = 2
    while (x <= sqrt(a) and x <= sqrt(b)):
        if (a%x==0 and b%x==0):
            a //= x
            b //= x
        else:
            x += 1
    return (-a if negative else a, b)