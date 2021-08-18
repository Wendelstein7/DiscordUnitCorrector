from abc import abstractmethod
from typing import Dict, List, Tuple, Union, Optional
from compiledregexes import ALL_DASHES_RGX_STR, ALL_DASHES_RGX
import re

class NumberParser:
    # for each number, the tuples will be returned in order and be nonoverlapping
    @abstractmethod
    def getNumberSpans(self, string, enablepvseps = True):
        # type: (str, bool) -> List[List[Tuple[int, int]]]
        pass
    @abstractmethod
    def parseNumber(self, strings):
        # type: (List[str]) -> float
        pass
    @abstractmethod
    def createStrings(self, number):
        # type: (float) -> List[str]
        pass
    # these methods should only be used when a number is being printed without context
    @abstractmethod
    def createStringFloat(self, number):
        # type: (float) -> str
        pass
    @abstractmethod
    def createStringInt(self, number):
        # type: (int) -> str
        pass
    # these two utility methods may take on more effective implementations in subclasses
    @abstractmethod
    def takeNumberFromStringEnd(self, string, enablepvseps = True):
        # type: (str, bool) -> Tuple[List[str], List[str]]
        spans1 = self.getNumberSpans(string, enablepvseps)
        spans2 = self.getNumberSpans(string[:-1], enablepvseps)
        for spans1_elem in spans1:
            if not spans1 in spans2:
                in_ = []
                out_ = []
                tracer = 0
                while tracer < len(string):
                    min_ = (len(string), len(string))
                    for span in spans1_elem:
                        if span[0] < min_[0]:
                            min_ = span
                    if min_[0] == tracer:
                        in_.append(string[min_[0]:min_[1]])
                        tracer = min_[1]
                    else:
                        out_.append(string[tracer:min_[0]])
                        tracer = min_[0]
                return (in_, out_)
        return ([], [string])
    @abstractmethod
    def takeNumberFromStringStart(self, string, enablepvseps = True):
        # type: (str, bool) -> Tuple[List[str], List[str]]
        spans1 = self.getNumberSpans(string, enablepvseps)
        spans2 = self.getNumberSpans(string[1:], enablepvseps)
        for spans1_elem in spans1:
            if not spans1 in spans2:
                in_ = []
                out_ = []
                tracer = 0
                while tracer < len(string):
                    min_ = (len(string), len(string))
                    for span in spans1_elem:
                        if span[0] < min_[0]:
                            min_ = span
                    if min_[0] == tracer:
                        in_.append(string[min_[0]:min_[1]])
                        tracer = min_[1]
                    else:
                        out_.append(string[tracer:min_[0]])
                        tracer = min_[0]
                return (in_, out_)
        return ([], [string])

class ParserSupportsPosNeg(NumberParser):
    @abstractmethod
    def getPositive(self, string):
        # type: (str) -> Tuple[bool, str]
        pass
    @abstractmethod
    def setPositive(self, string, positive):
        # type: (str, bool) -> str
        pass

class ParserSupportsSciNotation(NumberParser):
    @abstractmethod
    def createScientificString(self, base, exponent):
        # type: (Union[float, str], Union[int, str]) -> str
        pass
    @abstractmethod
    def isScientificString(self, string):
        # type: (str) -> bool
        pass

class ParserSupportsSigFigs(ParserSupportsPosNeg, ParserSupportsSciNotation):
    @abstractmethod
    def getRadixRegex(self):
        # type: () -> re.Pattern
        pass
    @abstractmethod
    def getDigitsRegex(self):
        # type: () -> re.Pattern
        pass
    @abstractmethod
    def getScinotRegex(self):
        # type: () -> re.Pattern
        pass
    @abstractmethod
    def createRadix(self):
        # type: () -> str
        pass
    @abstractmethod
    def createValuelessDigit(self):
        # type: () -> str
        pass

# a contiguous number with place value separators and a radix
class NormalNumberParser(ParserSupportsSigFigs, NumberParser):
    def __init__(self, *,
                decimalRgxStr, # type: str
                integerRgxStr, # type: str
                decimalRgxStrNoPvsep, # type: str
                integerRgxStrNoPvsep, # type: str
                pvSep, # type: str
                pvSepRgxStr = None, # type: Optional[str]
                radix, # type: str
                radixRgxStr = None, # type: Optional[str]
                scinot, # type: str
                scinotRgxStr = None, # type: Optional[str]
                digitsRgxStr = "\\d", # type: str
                zeroDigit = "0" # type: str
            ):
        # type: (...) -> None
        if pvSepRgxStr is None:
            pvSepRgxStr = re.escape(pvSep)
        if radixRgxStr is None:
            radixRgxStr = re.escape(radix)
        if scinotRgxStr is None:
            scinotRgxStr = re.escape(scinot)
        numberRgxStr = decimalRgxStr + scinotRgxStr + integerRgxStr
        numberRgxStrNoPvsep = decimalRgxStrNoPvsep + scinotRgxStr + integerRgxStrNoPvsep
        self.startRegex = re.compile("^" + numberRgxStr + "(?!"+digitsRgxStr+")") # type: re.Pattern
        self.startRegexNoPvsep = re.compile("^" + numberRgxStrNoPvsep + "(?!"+digitsRgxStr+")") # type: re.Pattern
        self.endRegex = re.compile("(?<!"+digitsRgxStr+")" + numberRgxStr + "$") # type: re.Pattern
        self.endRegexNoPvsep = re.compile("(?<!"+digitsRgxStr+")" + numberRgxStrNoPvsep + "$") # type: re.Pattern
        self.anywhereRegex = re.compile("(?<!"+digitsRgxStr+")" + numberRgxStr + "(?!"+digitsRgxStr+")") # type: re.Pattern
        self.anywhereRegexNoPvsep = re.compile("(?<!"+digitsRgxStr+")" + numberRgxStrNoPvsep + "(?!"+digitsRgxStr+")") # type: re.Pattern
        self.usablePvSep = pvSep # type: str
        self.pvSepRegex = re.compile(pvSepRgxStr) # type: re.Pattern
        self.usableRadix = radix # type: str
        self.radixRegex = re.compile(radixRgxStr) # type: re.Pattern
        self.usableScinotStr = scinot # type: str
        self.scinotRegex = re.compile(scinotRgxStr) # type: re.Pattern
        self.digitsRegex = re.compile(digitsRgxStr) # type: re.Pattern
        self.zeroDigit = zeroDigit # type: str

    def getNumberSpans(self, string, enablepvseps = True):
        # type: (str, bool) -> List[List[Tuple[int, int]]]
        out = [] # type: List[List[Tuple[int, int]]]
        for match in (self.anywhereRegex if enablepvseps else self.anywhereRegexNoPvsep).finditer(string):
            out.append([match.span()])
        return out

    def parseNumber(self, strings):
        # type: (List[str]) -> float
        if (len(strings) != 1):
            raise ValueError("Could not parse!")
        string = strings[0]
        string = self.pvSepRegex.sub("", string)
        string = self.radixRegex.sub(".", string)
        string = self.scinotRegex.sub("e", string)
        return float(string)

    @abstractmethod
    def createStrings(self, number):
        # type: (float) -> List[str]
        pass

    @abstractmethod
    def createStringFloat(self, number):
        # type: (float) -> str
        pass

    @abstractmethod
    def createStringInt(self, number):
        # type: (int) -> str
        pass

    def takeNumberFromStringEnd(self, string, enablepvseps = True):
        # type: (str, bool) -> Tuple[List[str], List[str]]
        match = (self.endRegex if enablepvseps else self.endRegexNoPvsep).search(string)
        if match is None:
            return ([], [string])
        return ([match.group()], [string[:match.start()]] if match.start() > 0 else [])

    def takeNumberFromStringStart(self, string, enablepvseps = True):
        # type: (str, bool) -> Tuple[List[str], List[str]]
        match = (self.startRegex if enablepvseps else self.startRegexNoPvsep).search(string)
        if match is None:
            return ([], [string])
        return ([match.group()], [string[match.start():]] if match.end() < len(string) else [])

    @abstractmethod
    def getPositive(self, string):
        # type: (str) -> Tuple[bool, str]
        pass

    @abstractmethod
    def setPositive(self, string, positive):
        # type: (str, bool) -> str
        pass

    def createScientificString(self, base, exponent):
        # type: (Union[float, str], Union[float, str]) -> str
        negate = False
        if not isinstance(base, str):
            negate = base < 0
            base = self.createStrings(base)[0]
        out = base + self.usableScinotStr + (exponent if isinstance(exponent, str) else self.createStrings(exponent)[0])
        return self.setPositive(out, not negate)

    def isScientificString(self, string):
        # type: (str) -> bool
        return self.scinotRegex.search(string) is not None

    def getRadixRegex(self):
        # type: () -> re.Pattern
        return self.radixRegex

    def getDigitsRegex(self):
        # type: () -> re.Pattern
        return self.digitsRegex

    def getScinotRegex(self):
        # type: () -> re.Pattern
        return self.scinotRegex

    def createRadix(self):
        # type: () -> str
        return self.usableRadix

    def createValuelessDigit(self):
        # type: () -> str
        return self.zeroDigit

class NormalDashNumberParser(NormalNumberParser):
    def __init__(self, *,
                decimalRgxStr, # type: str
                integerRgxStr, # type: str
                decimalRgxStrNoPvsep = None, # type: Optional[str]
                integerRgxStrNoPvsep = None, # type: Optional[str]
                pvSep, # type: str
                pvSepRgxStr = None, # type: Optional[str]
                radix, # type: str
                radixRgxStr = None, # type: Optional[str]
                scinot, # type: str
                scinotRgxStr = None, # type: Optional[str]
                digitsRgxStr = "\\d", # type: str
                zeroDigit = "0" # type: str
            ):
        # type: (...) -> None
        if radixRgxStr is None:
            radixRgxStr = re.escape(radix)
        if decimalRgxStrNoPvsep is None:
            decimalRgxStrNoPvsep = "{0}?((({1})+(({2})({1})*)?)|(({2})({1})+))".format(ALL_DASHES_RGX_STR, digitsRgxStr, radixRgxStr)
        if integerRgxStrNoPvsep is None:
            integerRgxStrNoPvsep = "{0}?(({1})+)".format(ALL_DASHES_RGX_STR, digitsRgxStr)
        NormalNumberParser.__init__(
            self,
            decimalRgxStr=decimalRgxStr,
            integerRgxStr=integerRgxStr,
            decimalRgxStrNoPvsep=decimalRgxStrNoPvsep,
            integerRgxStrNoPvsep=integerRgxStrNoPvsep,
            pvSep=pvSep,
            pvSepRgxStr=pvSepRgxStr,
            radix=radix,
            radixRgxStr=radixRgxStr,
            scinot=scinot,
            scinotRgxStr=scinotRgxStr,
            digitsRgxStr=digitsRgxStr,
            zeroDigit=zeroDigit
        )

    @abstractmethod
    def createStrings(self, number):
        # type: (float) -> List[str]
        pass

    @abstractmethod
    def createStringFloat(self, number):
        # type: (float) -> str
        pass

    @abstractmethod
    def createStringInt(self, number):
        # type: (int) -> str
        pass

    def getPositive(self, string):
        # type: (str) -> Tuple[bool, str]
        m = ALL_DASHES_RGX.search(string)
        if m is None:
            return (True, string)
        if m.start() != 0:
            raise ValueError("Could not parse number properly!")
        return (False, string[m.end():])

    def setPositive(self, string, positive):
        # type: (str, bool) -> str
        m = ALL_DASHES_RGX.search(string)
        if (m is not None) ^ positive:
            return string
        if m is None:
            return "−" + string
        return string[m.end():]

class NormalThreeGroupNumberParser(NormalNumberParser):
    def __init__(self, *,
                decimalRgxStr, # type: str
                integerRgxStr, # type: str
                decimalRgxStrNoPvsep, # type: str
                integerRgxStrNoPvsep, # type: str
                pvSep, # type: str
                pvSepRgxStr = None, # type: Optional[str]
                radix, # type: str
                radixRgxStr = None, # type: Optional[str]
                scinot, # type: str
                scinotRgxStr = None, # type: Optional[str]
                digitsRgxStr = "\\d", # type: str
                zeroDigit = "0" # type: str
            ):
        # type: (...) -> None
        NormalNumberParser.__init__(
            self,
            decimalRgxStr=decimalRgxStr,
            integerRgxStr=integerRgxStr,
            decimalRgxStrNoPvsep=decimalRgxStrNoPvsep,
            integerRgxStrNoPvsep=integerRgxStrNoPvsep,
            pvSep=pvSep,
            pvSepRgxStr=pvSepRgxStr,
            radix=radix,
            radixRgxStr=radixRgxStr,
            scinot=scinot,
            scinotRgxStr=scinotRgxStr,
            digitsRgxStr=digitsRgxStr,
            zeroDigit=zeroDigit
        )

    def createStrings(self, number):
        # type: (float) -> List[str]
        negate = False
        if (number < 0):
            negate = True
        number = abs(number)
        output = str(number)
        output = output[:-2] if output.endswith(".0") else output
        output.replace(".", self.usableRadix)
        outputparts = output.split("e")
        m = self.radixRegex.search(outputparts[0])
        i = len(outputparts[0])
        if m is not None:
            i = m.start()
        while True:
            i -= 3
            if i <= 0:
                break
            outputparts[0] = outputparts[0][:i] + self.usablePvSep + outputparts[0][i:]
        return [self.setPositive(output + ((self.usableScinotStr + outputparts[1]) if len(outputparts) > 1 else ""), not negate)]

    def createStringFloat(self, number):
        # type: (float) -> str
        negate = False
        if (number < 0):
            negate = True
        number = abs(number)
        output = str(number)
        output.replace(".", self.usableRadix)
        outputparts = output.split("e")
        m = self.radixRegex.search(outputparts[0])
        i = len(outputparts[0])
        if m is not None:
            i = m.start()
        while True:
            i -= 3
            if i <= 0:
                break
            outputparts[0] = outputparts[0][:i] + self.usablePvSep + outputparts[0][i:]
        return self.setPositive(output + ((self.usableScinotStr + outputparts[1]) if len(outputparts) > 1 else ""), not negate)

    def createStringInt(self, number):
        # type: (int) -> str
        negate = False
        if (number < 0):
            negate = True
        number = abs(number)
        output = str(number)
        i = len(output)
        while True:
            i -= 3
            if i <= 0:
                break
            output = output[:i] + self.usablePvSep + output[i:]
        return self.setPositive(output, not negate)

    @abstractmethod
    def getPositive(self, string):
        # type: (str) -> Tuple[bool, str]
        pass

    @abstractmethod
    def setPositive(self, string, positive):
        # type: (str, bool) -> str
        pass

class NormalDashThreeGroupNumberParser(NormalDashNumberParser, NormalThreeGroupNumberParser):
    def __init__(self, *,
                pvSep, # type: str
                pvSepRgxStr = None, # type: Optional[str]
                radix, # type: str
                radixRgxStr = None, # type: Optional[str]
                scinot, # type: str
                scinotRgxStr = None, # type: Optional[str]
                digitsRgxStr = "\\d", # type: str
                zeroDigit = "0" # type: str
            ):
        # type: (...) -> None
        if radixRgxStr is None:
            radixRgxStr = re.escape(radix)
        decimalRgxStr = "{0}?(((({1}){{1,3}}(({2})({1}){{3}})+)|({1})+)(({3})({1})*)?|({3})({1})+)".format(ALL_DASHES_RGX_STR, digitsRgxStr, pvSepRgxStr, radixRgxStr)
        integerRgxStr = "{0}?((({1}){{1,3}}(({2})({1}){{3}})+)|({1})+)".format(ALL_DASHES_RGX_STR, digitsRgxStr, pvSepRgxStr)
        decimalRgxStrNoPvsep = "{0}?((({1})+({2}({1})*)?)|({2}({1})+))".format(ALL_DASHES_RGX_STR, digitsRgxStr, radixRgxStr)
        integerRgxStrNoPvsep = "{0}?(({1})+)".format(ALL_DASHES_RGX_STR, digitsRgxStr)
        NormalNumberParser.__init__(
            self,
            decimalRgxStr=decimalRgxStr,
            integerRgxStr=integerRgxStr,
            decimalRgxStrNoPvsep=decimalRgxStrNoPvsep,
            integerRgxStrNoPvsep=integerRgxStrNoPvsep,
            pvSep=pvSep,
            pvSepRgxStr=pvSepRgxStr,
            radix=radix,
            radixRgxStr=radixRgxStr,
            scinot=scinot,
            scinotRgxStr=scinotRgxStr,
            digitsRgxStr=digitsRgxStr,
            zeroDigit=zeroDigit
        )
    
    def createStrings(self, number):
        # type: (float) -> List[str]
        return NormalThreeGroupNumberParser.createStrings(self, number)

    def createStringFloat(self, number):
        # type: (float) -> str
        return NormalThreeGroupNumberParser.createStringFloat(self, number)

    def createStringInt(self, number):
        # type: (int) -> str
        return NormalThreeGroupNumberParser.createStringInt(self, number)

    def getPositive(self, string):
        # type: (str) -> Tuple[bool, str]
        return NormalDashNumberParser.getPositive(self, string)

    def setPositive(self, string, positive):
        # type: (str, bool) -> str
        return NormalDashNumberParser.setPositive(self, string, positive)

# at some point, some utility functions to help generate the regular expression strings could be handy

NUMBER_PARSERS = {} # type: Dict[str, NumberParser]

# en-US (English, United States)
NUMBER_PARSERS["en-US"] = NormalDashThreeGroupNumberParser(pvSep=",", radix=".", scinot="*10^", digitsRgxStr="[0-9]")

# en-ZA (English, South Africa)
NUMBER_PARSERS["en-ZA"] = NormalDashThreeGroupNumberParser(pvSep=" ", pvSepRgxStr="\\s", radix=".", scinot="*10^", digitsRgxStr="[0-9]")

# pythonic (handles numbers the same way python does)
class PythonicParser(NormalDashNumberParser):
    def __init__(self):
        # type: () -> None
        NormalDashNumberParser.__init__(self,
            decimalRgxStr=ALL_DASHES_RGX_STR+"?(((\\d+(_\\d+)*)(\\.(\\d+(_\\d+)*))?)|\\.(\\d+(_\\d+)*))",
            integerRgxStr=ALL_DASHES_RGX_STR+"?\\d+(_\\d+)*",
            pvSep="_", radix=".", scinot="e"
        )
    def createStrings(self, number):
        # type: (float) -> List[str]
        return [str(number if number%1>0 else round(number))]
    def createStringFloat(self, number):
        # type: (float) -> str
        return str(float(number))
    def createStringInt(self, number):
        # type: (int) -> str
        return str(int(number))
NUMBER_PARSERS["pythonic"] = PythonicParser()

# add more parsers as necessary