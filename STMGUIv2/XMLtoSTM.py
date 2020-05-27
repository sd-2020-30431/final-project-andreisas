import xml.etree.ElementTree as ET

comparatorDict = {" lt ": "<", " gt ": ">", " le ": "<=", " ge ": ">=", " eq ":"==", " not ": "!=", " and ": "&&", " or ": "||"}

def XMLCondToCCond(condtext):
	'''
	Translates a condition from XML to C form
	'''
	for comp in comparatorDict:
		if comp in condtext:
			condtext = condtext.replace(comp, comparatorDict[comp])
	return condtext

def getStatesList(file):
	'''
	Reads the states from the XML file and returns a list of them
	'''
	tree = ET.parse(file)
	root = tree.getroot()
	states = root.find('states').findall('state')
	sList = []
	for state in states:
		sList.append(state.get('name'))
	return sList

def getTransitionsList(file):
	'''
	Reads the transitions from the XML file and returns a list of them
	'''
	tree = ET.parse(file)
	root = tree.getroot()
	transitions  = root.find('transitions').findall('transition')
	tList = []
	for transition in  transitions:
		tList.append([transition.get('name'), XMLCondToCCond(transition.get('cond')), transition.get('src'), transition.get('dest')])
	return tList