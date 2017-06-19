import csv
import argparse as ap

AT_PATH = "data/annotated_corpus.csv"
MET_PATH = "data/results.csv"
SAMPLE_PATH = "data/sample.txt"
DEFAULT_TEXT = "The original text is divided into three or more parts - and some new punctuation of course. We can talk about a sweet child and a tall child. A golden boy and a young man. And also red green brain ideas and intelligent boats."
VERBOSE = False

def writeToCSV(dicList, path, columns):
	with open(path, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, columns)
		writer.writeheader()
		writer.writerows(dicList)

def getText(path):
	data = ""
	with open(path, 'r') as textFile:
		data = textFile.read()
	return data 

def parseCommandLine():
	global VERBOSE
	parser = ap.ArgumentParser()
	parser.add_argument("-v", "--verbose", help="print details", action="store_true")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-f", "--file", type=str, help="look for metaphors in a text file")
	group.add_argument("-s", "--string", type=str, help="look for metaphors in a specified string")
	args = parser.parse_args()

	if args.verbose:
		VERBOSE = True

	if args.file:
		return getText(args.file)
	elif args.string:
		return args.string
	else:
		return DEFAULT_TEXT