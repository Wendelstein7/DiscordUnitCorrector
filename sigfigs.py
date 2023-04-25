import re
from math import isfinite, log10, floor
from typing import SupportsAbs

def numSigFigs(string):
    lzs = 1 if string[0] == "-" else 0
    preexponential = re.compile("[\s\S]*(?=(e))").search(string)
    string = preexponential.group() if preexponential else string
    while((string[lzs] == ".") | (string[lzs] == "0")):
        lzs += 1
        if (lzs == len(string)):
            return 0
    if ("." in string):
        if (string.index(".") >= lzs):
            return len(string) - lzs - 1
        if (string.index(".") >= 0):
            return len(string) - lzs
        return None
    tzs = len(string) - 1
    while(string[tzs] == "0"):
        tzs -= 1
    return tzs - lzs + 1

# precondition: string is a full-form int, not terminated with a radix
def scientificnotation(string, sigfigs):
    i=1
    j=0
    if string[0] == "-" :
        sigfigs += 1
        i += 1
        j += 1
        out = string[0:2] + "."
    else:
        out = string[0]+"."
    while(i<sigfigs):
        out += string[i]
        i += 1
    return out + "e+" + str(len(string)-1-j)

def roundsignificant(number, sigfigs):
    if number == 0 or sigfigs == 0:
        return "0"
    scinot = False
    digits = -int(floor(log10(abs(number))))+sigfigs-1
    digits = -int(floor(log10(abs(round(number, digits)))))+sigfigs-1
    if (digits <= 0):
        if ("e" in str(float(number))):
            scinot = True
        number = round(number)
    out = str(round(number, digits))
    if (digits > 0):
        addex = len(out)
        if ("e" in out):
            addex = out.index("e")
        if (not "." in out and sigfigs > 1):
            out = out[0:addex] + "." + out[addex:len(out)]
            addex += 1
        while (numSigFigs(out) < sigfigs):
            out = out[0:addex] + "0" + out[addex:len(out)]
        return out
    bad = numSigFigs(out) != sigfigs
    if (scinot or (bad and digits != 0)):
        return scientificnotation(out, sigfigs)
    if (bad and digits == 0):
        return out + "."
    return out

def leastSigDigit(string):
    postdecimal = re.compile("(?<=(\.))\d*").search(string)
    if postdecimal:
        pdlen = len(postdecimal.group())
    else:
        pdlen = 0
    exponential = re.compile("(?<=(e)).+").search(string)
    if exponential:
        evalu = int(exponential.group())
    else:
        evalu = 0
    return pdlen - evalu


class SigFigCompliantNumber(SupportsAbs):

    def __init__(self, stringRepresentation, *, exact = False, sigfigs = None, leastsigdig = None):
        if ((exact and sigfigs is not None) or (exact and leastsigdig is not None)):
            raise ValueError("Cannot specify sig figs / places on an exact number!")
        self.value = float(stringRepresentation)
        self.isNan = False
        self.isZero = False
        if (self.value == 0):
            if (sigfigs != None):
                raise ValueError("Cannot specify sig figs on zero!")
            self.isZero = True
            if exact:
                self.leastSignificantDigit = MAX_SIG_FIGS
                return
            if (leastsigdig != None):
                self.leastSignificantDigit = leastsigdig
                return
            self.leastSignificantDigit = leastSigDigit(stringRepresentation)
            return
        if (not isfinite(self.value)):
            self.isNan = True
            return
        if exact:
            self.numSigFigs = MAX_SIG_FIGS
            self.leastSignificantDigit = -int(floor(log10(abs(self.value))))+MAX_SIG_FIGS-1
            return
        if (sigfigs is None and leastsigdig is None):
            self.numSigFigs = numSigFigs(stringRepresentation)
            self.leastSignificantDigit = -int(floor(log10(abs(self.value))))+self.numSigFigs-1
        if (sigfigs is not None):
            self.numSigFigs = sigfigs
            self.leastSignificantDigit = -int(floor(log10(abs(self.value))))+self.numSigFigs-1
        if (leastsigdig is not None):
            self.leastSignificantDigit = leastsigdig
            self.numSigFigs = self.leastSignificantDigit+1+int(floor(log10(abs(self.value))))
        if (sigfigs is not None and sigfigs != self.numSigFigs):
            raise ValueError("Incongruity created!")
        if (leastsigdig is not None and leastsigdig != self.leastSignificantDigit):
            raise ValueError("Incongruity created!")

    # this string output value can always be parsed by float()
    # when supplied to the constructor it will always recreate the same sigfigcompliantnumber
    def __str__(self):
        if (self.isZero):
            return "0e" + str(-self.leastSignificantDigit)
        if (self.isNan):
            return "nan"
        return roundsignificant(self.value, self.numSigFigs)

    # all math operations should behave under effectively the same contract as the python float class
    # if a nonunary operation has a parameter that can be converted to a float rather than a sigfigcompliantnumber, it is converted and treated as exact
    # operations return sigfigcompliantnumbers to indicate the precision embedded in the calculation and its inputs

    def __add__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            if (self.isNan or other.isNan):
                return SigFigCompliantNumber(self.value + other.value)
            return SigFigCompliantNumber(self.value + other.value, leastsigdig=min(self.leastSignificantDigit, other.leastSignificantDigit))
        else:
            return self + SigFigCompliantNumber(other, exact=True)
    
    def __sub__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            if (self.isNan or other.isNan):
                return SigFigCompliantNumber(self.value - other.value)
            return SigFigCompliantNumber(self.value - other.value, leastsigdig=min(self.leastSignificantDigit, other.leastSignificantDigit))
        else:
            return self - SigFigCompliantNumber(other, exact=True)
    
    def __mul__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            if (self.isNan or other.isNan):
                return SigFigCompliantNumber(self.value * other.value)
            if (self.isZero):
                outLeastSigDigit = self.leastSignificantDigit
                outLeastSigDigit -= int(round(log10(other.value)))
                return SigFigCompliantNumber(0, leastsigdig=outLeastSigDigit)
            if (other.isZero):
                outLeastSigDigit = other.leastSignificantDigit
                outLeastSigDigit -= int(round(log10(self.value)))
                return SigFigCompliantNumber(0, leastsigdig=outLeastSigDigit)
            return SigFigCompliantNumber(self.value * other.value, sigfigs=min(self.numSigFigs, other.numSigFigs))
        else:
            return self * SigFigCompliantNumber(other, exact=True)
    
    def __truediv__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            if (other.isZero):
                raise ZeroDivisionError("SigFigCompliantNumber division by zero")
            if (self.isNan or other.isNan):
                return SigFigCompliantNumber(self.value + other.value)
            if (self.isZero):
                outLeastSigDigit = self.leastSignificantDigit
                outLeastSigDigit += int(round(log10(other.value)))
                return SigFigCompliantNumber(0, leastsigdig=outLeastSigDigit)
            return SigFigCompliantNumber(self.value / other.value, sigfigs=min(self.numSigFigs, other.numSigFigs))
        else:
            return self / SigFigCompliantNumber(other, exact=True)
    
    def __lt__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self.value < other.value
        else:
            return self < SigFigCompliantNumber(other, exact=True)
    
    def __le__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self.value <= other.value
        else:
            return self <= SigFigCompliantNumber(other, exact=True)
    
    def __ne__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self.value != other.value
        else:
            return self != SigFigCompliantNumber(other, exact=True)
    
    def __eq__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self.value == other.value
        else:
            return self == SigFigCompliantNumber(other, exact=True)
    
    def __gt__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self.value > other.value
        else:
            return self > SigFigCompliantNumber(other, exact=True)
    
    def __ge__(self, other):
        if (isinstance(other, SigFigCompliantNumber)):
            return self.value >= other.value
        else:
            return self >= SigFigCompliantNumber(other, exact=True)
    
    def __abs__(self):
        if (self.value >= 0):
            return self
        else:
            return SigFigCompliantNumber(-self.value, sigfigs=self.numSigFigs, leastsigdig=self.leastSignificantDigit)

MAX_SIG_FIGS = 1024