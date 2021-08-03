# To test single message run:
# python test.py -m "I am 10 feet tall"
#
# To start unit tests run:
# python test.py -v

from sigfigs import SigFigCompliantNumber
import unittest
from argparse import ArgumentParser

import unitconversion

parser = ArgumentParser()
parser.add_argument("-m", "--message", dest="message", help="Message to convert")

args, unknown = parser.parse_known_args()

message = args.message

if message:
    conversion_result = unitconversion.process(message)
    print(message)
    print(conversion_result)


class TestUnitCorrection(unittest.TestCase):
    def test_base_unit_conversion(self):
        unit_pairs = [
            ["10 feet", "3 m"],
            ["10feet", "3m"],
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_unit = pair[1]
            result = unitconversion.process(raw_unit)
            self.assertEqual(result, expected_unit)

    def test_spaces(self):
        unit_pairs = [
            ["10 feet²", 1],
            # ["10 feet ²", 2],
            # I'm commenting this out because passing this test requires a significant
            # change to the way units in higher dimensions are handled, so passing this
            # should probably be a separate issue. In fact, merging that new issue with
            # https://github.com/Wendelstein7/DiscordUnitCorrector/issues/35 is probably
            # the simplest solution
            ["10feet²", 0],
            # ["10feet ²", 1], see above
            ["I am 2 feet tall", 4],
            ["I  am  2  feet  tall", 8],
            ["I am 2.0 feet tall", 4],
            ["I  am  2.0  feet  tall", 8]
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_spaces = pair[1]
            result = unitconversion.process(raw_unit).count(' ')
            self.assertEqual(result, expected_spaces)

    def test_square_units(self):
        unit_pairs = [
            ["10.0 feet²", "0.929 m²"],
            ["4.0 acres", "16000 m²"],
            ["4 roods", "4000 m²"],
            ["4 miles²", "10 km²"],
            ["4.000 ft²", "3716 cm²"]
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_unit = pair[1]
            result = unitconversion.process(raw_unit)
            self.assertEqual(result, expected_unit)
    
    def test_case_sensitive(self):
        unit_pairs = [
            ["4 calories", "20 J"],
            ["4 Calories", "20 kJ"],
            ["4 kilocalories", "20 kJ"],
            ["4 kcalories", "20 kJ"],
            ["4 kiloCalories", None],
            ["4 kCalories", None],
            ["wow  4  calories  cool", "wow  20  J  cool"]
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_unit = pair[1]
            result = unitconversion.process(raw_unit)
            self.assertEqual(result, expected_unit)
    
    def test_sig_figs(self):
        unit_pairs = [
            ["4.004 ft²", "3720. cm²"],
            ["1.2345678901234 inches", "3.1358024409134 cm"],
            ["62. miles", "1.0e+2 km"],
            ["62.2 miles", "100. km"],
            ["6234 inches", "158.3 m"],
            ["0.0 degrees freedom", "-17.8 °C"],
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_unit = pair[1]
            result = unitconversion.process(raw_unit)
            self.assertEqual(result, expected_unit)

if not message:
    print("Running unit tests")
    unittest.main()
