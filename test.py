# python3 test.py -m "I am 10 feet tall"

import unitconversion
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-m", "--message", dest="message", help="Message to convert")

args = parser.parse_args()

message = args.message
converted = unitconversion.process(message)

print(message)
print(converted)