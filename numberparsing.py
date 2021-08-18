from abc import abstractmethod
from typing import Dict, List, Tuple, Union, Optional
from compiledregexes import *
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
            if not spans1_elem in spans2:
                in_ = []
                out_ = []
                tracer = 0
                while tracer < len(string):
                    min_ = (len(string), len(string))
                    for span in spans1_elem:
                        if (span[0] < min_[0] and span[0] >= tracer):
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
            if not spans1_elem in spans2:
                in_ = []
                out_ = []
                tracer = 0
                while tracer < len(string):
                    min_ = (len(string), len(string))
                    for span in spans1_elem:
                        if (span[0] < min_[0] and span[0] >= tracer):
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

class SuperExponentialMaker:
    def liftNumber(self, num):
        # type: (int) -> str
        chars = str(num)
        out = ""
        for i in range(len(chars)):
            out += SUPERSCRIPT_DIGITS_ARR[int(chars[i])]
        return out

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
    @abstractmethod
    def reformat(self, string): # given just the digits, radix, and scientific notation, put in the rest of the stuff
        # type: (str) -> str
        pass

# a contiguous number with place value separators and a radix
class NormalNumberParser(ParserSupportsSigFigs, NumberParser):
    def __init__(self, *,
            decimalRgxStr, # type: str
            decimalRgxStrNoPvsep, # type: str
            exponentRgxStr, # type: str
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
        numberRgxStr = decimalRgxStr + "(" + scinotRgxStr + exponentRgxStr + ")?"
        numberRgxStrNoPvsep = decimalRgxStrNoPvsep + "(" + scinotRgxStr + exponentRgxStr + ")?"
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

    @abstractmethod
    def reformat(self, string):
        # type: (str) -> str
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
        return ([match.group()], [string[match.end():]] if match.end() < len(string) else [])

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
        if not isinstance(exponent, str):
            exponent = self.createStrings(exponent)[0]
        if isinstance(self, SuperExponentialMaker) and (self.parseNumber([exponent])%1==0):
            exponent = self.liftNumber(int(self.parseNumber([exponent])))
        out = base + self.usableScinotStr + exponent
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
            decimalRgxStrNoPvsep = None, # type: Optional[str]
            exponentRgxStr = None, # type: Optional[str]
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
        if exponentRgxStr is None:
            exponentRgxStr = "({0}|{2})?(({1})+)".format(ALL_DASHES_RGX_STR, digitsRgxStr, ALL_PLUS_RGX_STR)
        NormalNumberParser.__init__(
            self,
            decimalRgxStr=decimalRgxStr,
            decimalRgxStrNoPvsep=decimalRgxStrNoPvsep,
            exponentRgxStr=exponentRgxStr,
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

    @abstractmethod
    def reformat(self, string):
        # type: (str) -> str
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
            decimalRgxStrNoPvsep, # type: str
            exponentRgxStr, # type: str
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
            decimalRgxStrNoPvsep=decimalRgxStrNoPvsep,
            exponentRgxStr=exponentRgxStr,
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
        if "e" in output:
            parts = output.split("e")
            return [self.createScientificString(float(parts[0]), int(parts[1]))]
        output.replace(".", self.usableRadix)
        m = self.radixRegex.search(output)
        i = len(output)
        if m is not None:
            i = m.start()
        while True:
            i -= 3
            if i <= 0:
                break
            output = output[:i] + self.usablePvSep + output[i:]
        return [self.setPositive(output, not negate)]

    def createStringFloat(self, number):
        # type: (float) -> str
        if (number < 0):
            negate = True
        number = abs(number)
        output = str(number)
        if "e" in output:
            parts = output.split("e")
            return self.createScientificString(float(parts[0]), int(parts[1]))
        output.replace(".", self.usableRadix)
        m = self.radixRegex.search(output)
        i = len(output)
        if m is not None:
            i = m.start()
        while True:
            i -= 3
            if i <= 0:
                break
            output = output[:i] + self.usablePvSep + output[i:]
        return self.setPositive(output, not negate)

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
    def reformat(self, string):
        # type: (str) -> str
        (positive, number) = self.getPositive(string)
        m = self.radixRegex.search(number)
        i = len(number)
        if m is not None:
            i = m.start()
        while True:
            i -= 3
            if i <= 0:
                break
            number = number[:i] + self.usablePvSep + number[i:]
        return self.setPositive(number, positive)

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
        if pvSepRgxStr is None:
            pvSepRgxStr = re.escape(pvSep)
        if radixRgxStr is None:
            radixRgxStr = re.escape(radix)
        if scinotRgxStr is None:
            scinotRgxStr = re.escape(scinot)
        decimalRgxStr = "{0}?(((({1}){{1,3}}(({2})({1}){{3}})+)|({1})+)(({3})({1})*)?|({3})({1})+)".format(ALL_DASHES_RGX_STR, digitsRgxStr, pvSepRgxStr, radixRgxStr)
        decimalRgxStrNoPvsep = "{0}?((({1})+({2}({1})*)?)|({2}({1})+))".format(ALL_DASHES_RGX_STR, digitsRgxStr, radixRgxStr)
        integerRgxStrNoPvsep = "({0}|{2})?(({1})+)".format(ALL_DASHES_RGX_STR, digitsRgxStr, ALL_PLUS_RGX_STR)
        NormalNumberParser.__init__(
            self,
            decimalRgxStr=decimalRgxStr,
            decimalRgxStrNoPvsep=decimalRgxStrNoPvsep,
            exponentRgxStr=integerRgxStrNoPvsep,
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

    def reformat(self, string):
        # type: (str) -> str
        return NormalThreeGroupNumberParser.reformat(self, string)

    def getPositive(self, string):
        # type: (str) -> Tuple[bool, str]
        return NormalDashNumberParser.getPositive(self, string)

    def setPositive(self, string, positive):
        # type: (str, bool) -> str
        return NormalDashNumberParser.setPositive(self, string, positive)

# Normal Parser, uses dashes for negatives, uses groups of three between radices, and uses superscript exponents
class FixedSuperParser(NormalDashThreeGroupNumberParser, SuperExponentialMaker):
    def __init__(self, *,
            pvSep, # type: str
            pvSepRgxStr = None, # type: Optional[str]
            radix, # type: str
            radixRgxStr = None, # type: Optional[str]
    ):
        if pvSepRgxStr is None:
            pvSepRgxStr = re.escape(pvSep)
        if radixRgxStr is None:
            radixRgxStr = re.escape(radix)
        decimalRgxStr = "{0}?(((({1}){{1,3}}(({2})({1}){{3}})+)|({1})+)(({3})({1})*)?|({3})({1})+)".format(ALL_DASHES_RGX_STR, "[0-9]", pvSepRgxStr, radixRgxStr)
        exponentRgxStr = "({0}|{3})?((({1}){{1,3}}(({2})({1}){{3}})+)|({1})+|({4})+)".format(ALL_DASHES_RGX_STR, "[0-9]", pvSepRgxStr, ALL_PLUS_RGX_STR, SUPERSCRIPT_DIGITS_RGX_STR)
        decimalRgxStrNoPvsep = "{0}?((({1})+({2}({1})*)?)|({2}({1})+))".format(ALL_DASHES_RGX_STR, "[0-9]", radixRgxStr)
        NormalNumberParser.__init__(self,
            decimalRgxStr=decimalRgxStr,
            decimalRgxStrNoPvsep=decimalRgxStrNoPvsep,
            exponentRgxStr=exponentRgxStr,
            pvSep=pvSep,
            pvSepRgxStr=pvSepRgxStr,
            radix=radix,
            radixRgxStr=radixRgxStr,
            scinot="×10",
            scinotRgxStr="(({1})10(?={0})|({1})10\\^)".format(SUPERSCRIPT_DIGITS_RGX_STR, ALL_TIMES_RGX_STR),
            digitsRgxStr="[0-9]",
            zeroDigit="0"
        )

NUMBER_PARSERS = {} # type: Dict[str, NumberParser]

# en-US (English, United States)
NUMBER_PARSERS["en-US"] = FixedSuperParser(pvSep=",", radix=".")

# en-ZA (English, South Africa)
NUMBER_PARSERS["en-ZA"] = FixedSuperParser(pvSep=" ", pvSepRgxStr="\\s", radix=".")

# pythonic (handles numbers the same way python does)
class PythonicParser(NormalDashNumberParser):
    def __init__(self):
        # type: () -> None
        NormalDashNumberParser.__init__(self,
            decimalRgxStr=ALL_DASHES_RGX_STR+"?(((\\d+(_\\d+)*)(\\.(\\d+(_\\d+)*))?)|\\.(\\d+(_\\d+)*))",
            exponentRgxStr=ALL_DASHES_RGX_STR+"?\\d+(_\\d+)*",
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
    def reformat(self, string):
        return string
NUMBER_PARSERS["pythonic"] = PythonicParser()

# add more parsers as necessary