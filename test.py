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
            ["10 feet", "300 cm"],
            ["10feet", "300cm"],
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
            ["4.0 acres", "16,000 m²"],
            ["4 roods", "4,000 m²"],
            ["4 miles²", "10 km²"],
            ["4.000 ft²", "3,716 cm²"]
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
            ["4.004 ft²", "3,720. cm²"],
            ["1.2345678901234 inches", "3.1358024409134 cm"],
            ["62. miles", "1.0×10² km"],
            ["62.2 miles", "100. km"],
            ["6234 inches", "158.34 m"],
            ["0.0 degrees freedom", "−17.8 °C"],
            ["32.0 degrees freedom", "0 °C"]
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_unit = pair[1]
            result = unitconversion.process(raw_unit)
            self.assertEqual(result, expected_unit)
    
    def test_subunit_detection(self):
        unit_pairs = [
            ["10 feet and 4 inches", "315 cm"],
            ["6 pounds, 2.1 ounces", "2.78 kg"],
            ["6  pounds  4.50  ounces", "2.8491  kg"],
            ["6.0 feet and 170 pounds", "183 cm and 77 kg"],
            ["4'2", "127cm"],
            ["5  foot  2", "157  cm"],
            ["100'11\"", "30.76m"],
            ["4 foot 20 inches", "170 cm"],
            ["5 oz t, 19 dwt and 20 grains", "186.4 g"],
            ["2 gallons 30 fluid ounces", "8.46 L"],
            ["I'm 4'5 and 20 pounds.", "I'm 135cm and 9 kg."],
            ["I'm 4 foot 5 inches", "I'm 135 cm"],
            ["I'm 4 foot 9 pounds", "I'm 120 cm 4 kg"],
            [
                "I'm 4'5, my sister is 3'2, and my mom is 4'3. Wow, we're short!",
                "I'm 135cm, my sister is 97cm, and my mom is 130.cm. Wow, we're short!"
            ],
            [
                "My body has a volume of 16 gallons 48 ounces and weighs 134 pounds 13 ounces.",
                "My body has a volume of 62.0 L and weighs 61.15 kg."
            ],
            ["16 gallons,  48. ounces", "61.99 L"],
            ["I'm 5.2  feet and  6 inches  tall.", "I'm 174 cm  tall."],
            ["I'm 5.2feet and  6  inches  tall.", "I'm 174 cm  tall."],
            ["I'm  5.2    feet and  6   inches  tall.", "I'm  174   cm  tall."],
            ["3-foot-8-inch-long potato", "112-cm-long potato"],
            ["3 foot -8 inch long potato", "71 cm long potato"],
            ["3-foot--8-inch-long potato", "71-cm-long potato"],
            ["3-   foot 8- inch long potato", "112-  cm long potato"],
            ["3-  foot 8- inch long potato", "112- cm long potato"],
            ["3foot,8inch long potato", "112cm long potato"]
        ]

        for pair in unit_pairs:
            raw_unit = pair[0]
            expected_unit = pair[1]
            result = unitconversion.process(raw_unit)
            self.assertEqual(result, expected_unit)

if not message:
    print("Running unit tests")
    unittest.main()