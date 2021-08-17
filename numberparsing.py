from abc import abstractmethod
from typing import Dict, List, Tuple, Union
from compiledregexes import ALL_DASHES_RGX_STR
import re

class NumberParser:
    # for each number, the tuples will be returned in order and be nonoverlapping
    @abstractmethod
    def getNumberSpans(self, string : str, enablepvseps : bool = True) -> List[List[Tuple[int, int]]]: pass
    @abstractmethod
    def parseNumber(self, strings : List[str]) -> float: pass
    @abstractmethod
    def createStrings(self, number : float) -> List[str]: pass
    # these methods should only be used when a number is being printed without context
    @abstractmethod
    def createStringFloat(self, number : float) -> str: pass
    @abstractmethod
    def createStringInt(self, number : int) -> str: pass
    # these two utility methods may take on more effective implementations in subclasses
    @abstractmethod
    def takeNumberFromStringEnd(self, string : str, enablepvseps : bool = True) -> Tuple[List[str], List[str]]:
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
    def takeNumberFromStringStart(self, string : str, enablepvseps : bool = True) -> Tuple[List[str], List[str]]:
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
    def getPositive(self, string : str) -> Tuple[bool, str]: pass
    @abstractmethod
    def setPositive(self, string : str, positive : bool) -> str: pass

class ParserSupportsSciNotation(NumberParser):
    @abstractmethod
    def createScientificString(self, base : Union[float, str], exponent : Union[int, str]) -> str: pass
    @abstractmethod
    def isScientificString(self, string : str) -> bool: pass

class ParserSupportsSigFigs(ParserSupportsPosNeg, ParserSupportsSciNotation):
    @abstractmethod
    def getRadixRegex(self) -> re.Pattern: pass
    @abstractmethod
    def getDigitsRegex(self) -> re.Pattern: pass
    @abstractmethod
    def getScinotRegex(self) -> re.Pattern: pass
    @abstractmethod
    def createRadix(self) -> str: pass
    @abstractmethod
    def createValuelessDigit(self) -> str: pass

# a number with place value separators and a radix, using the digits 0 to 9
class NormalNumberParser(ParserSupportsSigFigs, NumberParser):
    def __init__(self, *, numberRgxStr, pvSepRgxStr, radixRgxStr, scinotRgxStr):
        self.startRegex = re.compile("^" + numberRgxStr + "(?=(\D|^))")
        self.endRegex = re.compile("(?<=(\D|^))" + numberRgxStr + "$")
        self.anywhereRegex = re.compile("(?<=(\D|^))" + numberRgxStr + "(?=(\D|^))")
        self.usablePvSep = ","
        self.pvSepRegex = re.compile(pvSepRgxStr)
        self.usableRadix = "."
        self.radixRegex = re.compile(radixRgxStr)
        self.scinotRegex = re.compile(scinotRgxStr)

# at some point, some utility functions to help generate the regular expression strings could be handy

NUMBER_PARSERS : Dict[str, NumberParser] = {}
NUMBER_PARSERS["pythonic"] = NormalNumberParser(numberRgxStr=ALL_DASHES_RGX_STR+"?(((\\d+(_\\d+)*)(\\.(\\d+(_\\d+)*))?)|\\.(\\d+(_\\d+)*))", pvSepRgxStr="_", radixRgxStr="\\.", scinotRgxStr="e")
NUMBER_PARSERS["en-US"] = NormalNumberParser(numberRgxStr=ALL_DASHES_RGX_STR+"?(((\\d{1,3}(,\\d{3})+)|\\d+)(\\.\\d*)?|\\.\\d+)", pvSepRgxStr=",", radixRgxStr="\\.")
NUMBER_PARSERS["en-ZA"] = NormalNumberParser(numberRgxStr=ALL_DASHES_RGX_STR+"?(((\\d{1,3}(\\s\\d{3})+)|\\d+)(\\.\\d*)?|\\.\\d+)", pvSepRgxStr="\\s", radixRgxStr="\\.")