from math import sin
import re
from typing import List, Optional, Tuple, Dict

END_SPACE_RGX = re.compile("\\s$")

def compromiseBetweenStrings( stringarr ):
    # type: (List[str]) -> str
    dsa1 = directStringAverage(stringarr)
    if dsa1 is not None:
        return dsa1
    best = listOfItemsTiedForMostCommon(stringarr)[0]
    if (len(best) == 1):
        return best[0]
    stringarr = best
    dsa2 = directStringAverage(stringarr)
    if dsa2 is not None:
        return dsa2
    pfstrs = stringarr.copy()
    prefix = "" # type: str
    ati = [] # type: List[str]
    atirev = {} # type: Dict[int, int]
    while True:
        ati = []
        atirev = {}
        for i in range(len(pfstrs)):
            if len(pfstrs[i]) > 0:
                atirev[len(ati)] = i
                ati.append(pfstrs[i][0])
        if (len(ati) == 0):
            return prefix
        (cs, cuts, pops) = listOfItemsTiedForMostCommon(ati)
        if (len(cs)!=1 or len(cuts)*2<=len(pfstrs)):
            break
        prefix = prefix + cs[0]
        for pop in pops:
            pfstrs.pop(pop)
        for cut in cuts:
            pfstrs[atirev[cut]] = pfstrs[atirev[cut]][1:]
    postfix = ""
    while True:
        ati = []
        atirev = {}
        for i in range(len(pfstrs)):
            if len(pfstrs[i]) > 0:
                atirev[len(ati)] = i
                ati.append(pfstrs[i][-1])
        if (len(ati) == 0):
            return prefix+postfix
        (cs, cuts, pops) = listOfItemsTiedForMostCommon(ati)
        if (len(cs)!=1 or len(cuts)*2<=len(pfstrs)):
            break
        postfix = cs[0] + postfix
        for pop in pops:
            pfstrs.pop(pop)
        for cut in cuts:
            pfstrs[cut] = pfstrs[cut][:-1]
    dsa3 = directStringAverage(pfstrs, END_SPACE_RGX.search(prefix) is not None)
    if dsa3 is not None:
        return prefix + dsa3 + postfix
    (options, _, _) = listOfItemsTiedForMostCommon(pfstrs)
    if len(options) == 1:
        return prefix+options[0]+postfix
    if "" in options:
        options.remove("")
    # at this point, as a last resort
    # the compromise will occur via a random-seeming, but deterministic selection from the options
    FAKE_RANDOM_FACTOR = 54.7287857178
    return options[int((len(options) + len(options) * sin(FAKE_RANDOM_FACTOR * len(options))) / 2)]

def directStringAverage(pfstrs, biasdown = False):
    # type: (List[str], bool) -> Optional[str]
    charcount = 0
    if (len("".join(pfstrs)) == 0):
        return ""
    char = "".join(pfstrs)[0]
    uniform = True
    spaces = True
    for c in "".join(pfstrs):
        charcount += 1
        if not c.isspace():
            spaces = False
        if c != char:
            uniform = False
        if ((not uniform) and (not spaces)):
            break
    if uniform:
        l = int(charcount / len(pfstrs))
        l = 1 if (l == 0 and charcount > 0 and not biasdown) else l
        return "".join(l * [char])
    if spaces:
        (charoptions, _, _) = listOfItemsTiedForMostCommon(list("".join(pfstrs)))
        l = int(charcount / len(pfstrs))
        l = 1 if (l == 0 and charcount > 0) else l
        if " " in charoptions:
            return "".join(l * [" "])
        else:
            # at this point, as a last resort
            # the compromise will occur by repating a random-seeming, but deterministic character selected from the options
            FAKE_RANDOM_FACTOR = 61.091056745
            c = charoptions[int((len(charoptions) + len(charoptions) * sin(FAKE_RANDOM_FACTOR * len(charoptions))) / 2)]
            return "".join(l * [c])
    return None

def listOfItemsTiedForMostCommon(inputlist):
    # type: (List[str]) -> Tuple[List[str], List[int], List[int]]
    occurences = {} # type: Dict[str, List[int]]
    for i in range(len(inputlist)):
        item = inputlist[i]
        if item in occurences.keys():
            occurences[item].append(i)
        else:
            occurences[item] = [i]
    most = [] # type: List[str]
    mv = 0
    partition1 = [] # type: List[int]
    partition2 = [] # type: List[int]
    for key in occurences.keys():
        if (len(occurences[key]) > mv):
            mv = len(occurences[key])
            most = [key]
            partition2 += partition1
            partition1 = occurences[key]
        elif (len(occurences[key]) == mv):
            most.append(key)
            partition1 += occurences[key]
        else:
            partition2 += occurences[key]
    return (most, partition1, partition2)