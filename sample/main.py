# Author : Henri Toussaint
# Latest revision : 01/25/2017

# 23/02 12pm


import modules.annotator as an
import modules.cand_id as ci
import modules.met_id as mi
import modules.sample_functions as sf
import modules.utils
from modules.darkthoughts import darkthoughtsFunction

if __name__ == "__main__":

	data = utils.parseCommandLine()
	annotator = an.Annotator(data)
	annotator.addColumn("POS", sf.posFunction)
	annotator.addColumn("lemma", sf.lemmatizingFunction)
	annotatedText = annotator.getAnnotatedText()
	annotatedText.writeToCSV(utils.AT_PATH)
	if utils.VERBOSE:
		print(annotatedText)

	identifier = ci.CandidateIdentifier(annotatedText)
	identifier.IDCandidates(sf.adjNounFinder)
	candidates = identifier.getCandidates()
	if utils.VERBOSE:
		print(candidates)

	labeler = mi.MetaphorIdentifier(candidates)
	#labeler.IDMetaphors(sf.testLabelFunction)
	labeler.IDMetaphors(darkthoughtsFunction)
	results = labeler.getMetaphors()
	results.writeToCSV(utils.MET_PATH)
	print(results)

	
# read from csv file, take source/targett and keep the rest

