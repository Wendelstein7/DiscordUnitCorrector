import re

def orRegexStrFromArray(options):
    output = "("
    for option in options:
        output += re.escape(option) + "|"
    output = output[:-1]
    output += ")"
    return output

MATCH_NOTHING_RGX = re.compile("\A\b\Z^$")

ALL_DASHES_ARR = ["-", "‐", "‑", "–", "‒", "−"]
ALL_DASHES_RGX_STR = orRegexStrFromArray(ALL_DASHES_ARR)
ALL_PRIMES_ARR = ["'", "‘", "’", "`", "´"]
ALL_PRIMES_RGX_STR = orRegexStrFromArray(ALL_PRIMES_ARR)

DISCORD_FORMAT_CONTROL_REGEX = re.compile("(?<!\\\\)(´|`|\\*|_|~~)|((?<=\n)> |(?<=^)> )")

NUMBER_UNIT_SPACERS_END_RGX = re.compile("(\\s|"+ALL_DASHES_RGX_STR+")*$")
NUMBER_UNIT_SPACERS_START_RGX = re.compile("^(\\s|"+ALL_DASHES_RGX_STR+")*")
SUPERUNIT_SUBUNIT_SPACER_END_RGX = re.compile("(\\s|,|and|\\+|"+ALL_DASHES_RGX_STR+")*$")
SUPERUNIT_SUBUNIT_SPACER_START_RGX = re.compile("^(\\s|,|and|\\+|"+ALL_DASHES_RGX_STR+")*")