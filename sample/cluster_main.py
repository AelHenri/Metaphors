from modules.datastructs.clustered_data import ClusteredData
from modules.parsing_functions import parseVerbNet, parseNouns, parseTroFi
from modules.utils import writeToCSV
from modules.cluster_module import test
from nltk.parse.stanford import StanfordDependencyParser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
import sys
import ast
import csv

FIRST_CLUSTER = 2
LAST_CLUSTER = 3

# Find the object of a verb in a sentence
def getObj(sentence, verb):
	parser = StanfordDependencyParser()
	lemmatizer = WordNetLemmatizer()
	dependency_tree = [list(line.triples()) for line in parser.raw_parse(sentence)]
	dependencies = dependency_tree[0]
	verbLemma = lemmatizer.lemmatize(verb, wordnet.VERB)
	obj = ""
	for dep in dependencies:
		if  "VB" in dep[0][1]:
			depVerbLemma = lemmatizer.lemmatize(dep[0][0], wordnet.VERB)
			if (verbLemma == depVerbLemma and ("obj" in dep[1] or "nsubjpass" in dep[1])):
				obj = dep[2][0]

	return lemmatizer.lemmatize(obj, wordnet.NOUN) 

# Determine the labels of the verb-object relationship (L for litteral, N for non-litteral)
# Returns a dictionnary with the verb-object tuple as the key and the list of labels found as the value
def getVerbObjTags(data, first, last):
	verbObjTags = {}
	objects = []
	verbs = []
	dataEntries = []
	if first == 0 and last == 0:
		dataEntries = data.getEntries()
	elif last == 0:
		dataEntries = data.getEntries()[first:]
	else:
		dataEntries = data.getEntries()[first:last+1]
	for verb in dataEntries:
		actualVerb = ""
		clusterTag = ""
		if verb.endswith("-NL"):
			actualVerb = verb[:-3]
			clusterTag = "N"
		elif verb.endswith("-L"):
			actualVerb = verb[:-2]
			clusterTag = "L"

		clusterSentences = data.getClusterContent(verb, "sentence")
		clusterTags = data.getClusterContent(verb, "annotation")
		for i in range(len(clusterSentences)):
			currentTag = ""
			if clusterTags[i] != "U":
				currentTag = clusterTags[i]
			else:
				currentTag = clusterTag

			currentSentence = clusterSentences[i]
			verbObjKey = (actualVerb, getObj(currentSentence ,actualVerb))
			if (verbObjKey[1] != ""):
				if verbObjKey not in verbObjTags.keys():
					verbObjTags[verbObjKey] = []
				verbObjTags[verbObjKey].append(currentTag)
				print("(" + verbObjKey[0] + ", " + verbObjKey[1] + "): " + currentTag)
	return verbObjTags

# Get the  tags from a CSV file constructed with the previous function
def getTagsFromCSV(path):
	verbObjTags = {}
	with open(path) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			verb = row["Verb"]
			noun = row["Noun"]
			verbObjTags[(verb, noun)] = ast.literal_eval(row["Labels"])
	return verbObjTags

# Associate verb-nouns couples from the database with available and corresponding verb-object couples from the processed TroFi database,
# and determine the final tag and confidence by counting the tags in the list.
def tagVerbNouns(tags, verbNouns):
	finalTags = {}
	for couple in verbNouns:
		if couple in tags.keys():
			litterals = 0
			nonlitterals = 0
			for t in tags[couple]:
				if t == "N":
					nonlitterals+=1
				elif t == "L":
					litterals+=1
			if nonlitterals > litterals:
				finalTags[couple] = ("N", nonlitterals/(litterals+nonlitterals))
			else:
				finalTags[couple] = ("L", litterals/(litterals+nonlitterals))
	return finalTags

# Get a list of all the possible verb-noun couples in the database
def getVerbNouns(verbsData, nounsData):
	verbsData = ClusteredData.fromFile("data/clustering/verbnet_150_50_200.log-preprocessed", parseVerbNet)
	nounsData = ClusteredData.fromFile("data/clustering/200_2000.log-preprocessed", parseNouns)
	verbs = []
	nouns = []
	for cluster in verbsData.getEntries():
		for v in verbsData.getClusterContent(cluster, "words"):
			verbs.append(v)
	for cluster in nounsData.getEntries():
		for n in nounsData.getClusterContent(cluster, "words"):
			nouns.append(n)
	return [(v, n) for v in verbs for n in nouns]

# Export the results to a CSV file
def resultsToCSV(results):
	dictList = []
	verbNouns = results.keys()
	for vn in verbNouns:
		newDict = {}
		newDict["Verb"] = vn[0]
		newDict["Noun"] = vn[1]
		newDict["Label"] = results[vn][0]
		newDict["Confidence"] = results[vn][1]
		dictList.append(newDict)
	writeToCSV(dictList, "data/cluster_results.csv", ["Verb", "Noun", "Label", "Confidence"])

# Export the tags to a CSV file
def tagsToCSV(tags):
	dictList = []
	verbNouns = tags.keys()
	for vn in verbNouns:
		newDict = {}
		newDict["Verb"] = vn[0]
		newDict["Noun"] = vn[1]
		newDict["Labels"] = tags[vn]
		dictList.append(newDict)
	writeToCSV(dictList, "data/trofi_tags_bis.csv", ["Verb", "Noun", "Labels"])

if __name__ == '__main__':
	'''
	data1 = ClusteredData.fromFile("data/clustering/verbnet_150_50_200.log-preprocessed", parseVerbNet)
	#print(data1.getClusterContent("3", "words"))
	#
	data2 = ClusteredData.fromFile("data/clustering/200_2000.log-preprocessed", parseNouns)
	#print(data2.getClusterContent("3", "words"))
	#
	data3 = ClusteredData.fromFile("data/clustering/TroFiExampleBase.txt", parseTroFi)
	
	first = FIRST_CLUSTER
	last = LAST_CLUSTER
	if len(sys.argv) >= 3:
		first = int(sys.argv[1])
		last = int(sys.argv[2])
	tags = getVerbObjTags(data3, first, last)
	#tags = getTagsFromCSV("data/trofi_tags_bis.csv")
	print(tags)
	tagsToCSV(tags)
	verbNouns = getVerbNouns(data1, data2)
	results = tagVerbNouns(tags, verbNouns)
	print(results)
	print("\n")
	
	resultsToCSV(results)
	'''
	test()

