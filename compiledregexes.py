import re

def orRegexStrFromArray(options):
    output = "("
    for option in options:
        output += re.escape(option) + "|"
    output = output[:-1]
    output += ")"
    return output

MATCH_NOTHING_RGX = re.compile("\\A\\b\\Z^$")

ALL_DASHES_ARR = ["-", "‐", "‑", "–", "‒", "−"]
ALL_DASHES_RGX_STR = orRegexStrFromArray(ALL_DASHES_ARR)
ALL_DASHES_RGX = re.compile(ALL_DASHES_RGX_STR)
ALL_PRIMES_ARR = ["'", "‘", "’", "`", "´"]
ALL_PRIMES_RGX_STR = orRegexStrFromArray(ALL_PRIMES_ARR)
ALL_PRIMES_RGX = re.compile(ALL_PRIMES_RGX_STR)
ALL_PLUS_ARR = ["＋", "+"]
ALL_PLUS_RGX_STR = orRegexStrFromArray(ALL_PLUS_ARR)
ALL_PLUS_RGX = re.compile(ALL_PLUS_RGX_STR)
ALL_TIMES_ARR = ["×", "x", "*"]
ALL_TIMES_RGX_STR = orRegexStrFromArray(ALL_TIMES_ARR)
ALL_TIMES_RGX = re.compile(ALL_TIMES_RGX_STR)
SUPERSCRIPT_DIGITS_ARR = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]
SUPERSCRIPT_DIGITS_RGX_STR = orRegexStrFromArray(SUPERSCRIPT_DIGITS_ARR)
SUPERSCRIPT_DIGITS_RGX = re.compile(SUPERSCRIPT_DIGITS_RGX_STR)

DISCORD_FORMAT_CONTROL_REGEX = re.compile("(?<!\\\\)(´|`|\\*|_|~~)|((?<=\n)> |(?<=^)> )")

NUMBER_UNIT_SPACERS_END_RGX = re.compile("(\\s|"+ALL_DASHES_RGX_STR+")*$")
NUMBER_UNIT_SPACERS_START_RGX = re.compile("^(\\s|"+ALL_DASHES_RGX_STR+")*")
SUPERUNIT_SUBUNIT_SPACER_END_RGX = re.compile("(\\s|,|and|\\+|"+ALL_DASHES_RGX_STR+")*$")
SUPERUNIT_SUBUNIT_SPACER_START_RGX = re.compile("^(\\s|,|and|\\+|"+ALL_DASHES_RGX_STR+")*")