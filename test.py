# To test single message run:
# python test.py -m "I am 10 feet tall"
#
# To start unit tests run:
# python test.py -v

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
            ["10 feet", "3.05 m"],
            ["10feet", "3.05m"],
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_unit = pair[1]
            result = unitconversion.process(raw_unit)
            self.assertEqual(result, expected_unit)

    def test_spaces(self):
        unit_pairs = [
            ["10 feet^2", 1],
            ["10 feet ^2", 2],
            ["10feet^2", 0],
            ["10feet ^2", 1],
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_spaces = pair[1]
            result = unitconversion.process(raw_unit).count(' ')
            self.assertEqual(result, expected_spaces)

    def test_square_units(self):
        unit_pairs = [
            ["10 feet^2", "0.929 m^2"],
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_unit = pair[1]
            result = unitconversion.process(raw_unit)
            self.assertEqual(result, expected_unit)


if not message:
    print("Running unit tests")
    unittest.main()
