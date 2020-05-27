from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom
import random
import re
import csv

xmlin = "Data/XMLFile.xml"
xmlout = "Data/XMLFile.xml"
cout = "Data/CFile.c"

comparatorDict = {" lt ": "<", " gt ": ">", " le ": "<=", " ge ": ">=", " eq ":"==", " not ": "!=", " and ": "&&", " or ": "||"}
comparatorRevDict = {"<": " lt ", ">": " gt ", "<=": " le ", ">=": " ge ", "==": " eq ", "!=": " not ", "&&": " and ", "||": " or "}
#Classes
##################################################################################################################
class STMClass:

	def __init__(self, statesDict, transitionsDict, inputsDict):
		self.statesDict = statesDict
		self.transitionsDict = transitionsDict
		self.inputsDict = inputsDict
		self.srcDict = dict()
		self.destDict = dict()

	def addState(self, name):
		'''
		Adds a state
		'''
		if self.findState(name) == "Fail":
			self.statesDict[name] = StateClass(name)
			return "Success"
		return "A state with the same name is already existing"

	def addTransition(self, name, cond, src, dest):
		'''
		Add a transition in transitionsDict if the states are existing or merge the conditions if the same transition already exists
		Also adds the transition to srcDict and destDict
		'''
		if self.tryAppendCond(src, dest, cond) == True:
			addInputsIfNeeded(getInputsFromCond(XMLCondToCCond(cond)))
			return "Transition was merged with another one"
		if self.findState(src) == "Success" and self.findState(dest) == "Success":
			self.srcDict.setdefault(src, []).append(dest)
			self.destDict.setdefault(dest, []).append(src)
			if name == "":
				name = "t" + str(random.randint(99, 999))
			self.transitionsDict[src+"|"+dest] = TransitionClass(name, cond, StateClass(src), StateClass(dest))
			addInputsIfNeeded(getInputsFromCond(XMLCondToCCond(cond)))
			return "Success"
		return "Source or/and destination not existing"

	def addInput(self, name, value):
		'''
		Adds an input
		'''
		if name in self.inputsDict:
			return "An input with the same name is already existing"
		self.inputsDict[name] = value
		return "Success"
		
	def findState(self, name):
		'''
		Search for a state by name and return Success if found
		'''
		if name in self.statesDict:
			return "Success"
		return "Fail"

	def findTransition(self, src, dest):
		'''
		Search for a transition by source and destination and return Success if found
		'''
		if src+"|"+dest in self.transitionsDict:
			return "Success"
		return "Fail"

	def findInput(self, name):
		'''
		Search for an input and return Success if found
		'''
		if name in self.inputsDict:
			return "Success"
		return "Fail"

	def tryAppendCond(self, src, dest, cond):
		'''
		Search for transitions by source and destination and if found append the condition and return True
		Also if the transition is found but the new condition is included or identical 
		to the current condition True is returned and the transition remains the same
		'''
		if src+"|"+dest in self.transitionsDict:
			if cond in self.transitionsDict[src+"|"+dest].cond:
				return True
			self.transitionsDict[src+"|"+dest].cond += " || " + cond
			return True
		return False 

	def updateState(self, name):
		'''
		Update a state by name
		'''
		if name in self.statesDict:
			self.statesDict[name].name = name
			return "Success"
		return "State was not found"

	def updateTransition(self, name, cond, src, dest):
		'''
		Update a transition's condition by source and destination'
		'''
		if src+"|"+dest in self.transitionsDict:
			self.transitionsDict[src+"|"+dest].cond = cond
			self.transitionsDict[src+"|"+dest].name = name
			addInputsIfNeeded(getInputsFromCond(XMLCondToCCond(cond)))
			return "Success"
		return "Transition not found"

	def updateInput(self, name, value):
		'''
		Update an input's value
		'''
		if name in self.inputsDict:
			self.inputsDict[name] = value
			return "Success"
		else:
			return self.addInput(name, value)

	def removeState(self, name):
		'''
		Remove a state by name and all transitions it is included in 
		'''
		if name in self.statesDict:
			removeStateLinks(name)
			del self.statesDict[name]
			return "Success"
		return "State not found"

	def removeTransition(self, src, dest, afterRemLinks = None):
		'''
		Remove a transition by source and destination
		Also remove the transition from srcDict and destDict
		It will do nothing if afterRemLinks is not None and will return Success
		'''
		if src+"|"+dest in self.transitionsDict:
			if afterRemLinks == None:
				self.srcDict[src].remove(dest)
				self.destDict[dest].remove(src)
			del self.transitionsDict[src+"|"+dest]
			return "Success"
		return "Transition not found"

	def removeInput(self, name):
		'''
		Remove an input
		'''
		if name in self.inputsDict:
			del self.inputsDict[name]
			return "Success"
		return "Input not found"

	def toString(self):
		text = "\nmySTM"
		text += "\n\tInputs:"
		for inp in self.inputsDict:
			text += "\n\t\t" + inp + " = " + self.inputsDict[inp] 
		text += "\n\tStates:"
		for st in self.statesDict:
			text += "\n\t\t" + self.statesDict[st].toString()
		text += "\n\tTransitions:"
		for tr in self.transitionsDict:
			text += "\n\t\t" + self.transitionsDict[tr].toString()
		return text

class StateClass:
	def __init__(self, name):
		self.name = name

	def toString(self):
		return self.name

class TransitionClass:
	def __init__(self, name, cond, src, dest):
		self.name = name
		self.cond = cond
		self.src = src
		self.dest = dest

	def toString(self):
		return "%s %s %s %s" % (self.name, self.cond, self.src.toString(), self.dest.toString())

#UI Functions
##################################################################################################################
def addState(name):
	return mySTM.addState(name)

def addTransition(name, cond, src, dest):
	return mySTM.addTransition(name, cond, src, dest)

def addInput(name, value):
	return mySTM.addInput(name, value)

def findState(name):
	return mySTM.findState(name)

def findTransition(src, dest):
	return mySTM.findTransition(src, dest)

def findInput(name):
	return mySTM.findInput(name)

def updateState(name):
	return mySTM.updateState(name)

def updateTransition(name, cond, src, dest):
	return mySTM.updateTransition(name, cond, src, dest)

def updateInput(name, value):
	return mySTM.updateInput(name, value)

def removeState(name):
	return mySTM.removeState(name)

def removeTransition(src, dest):
	return mySTM.removeTransition(src, dest)

def removeInput(name):
	return mySTM.removeInput(name)

def showSTM():
	return mySTM.toString()

#Functions
##################################################################################################################
def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def updateXML():
	'''
	Write the current STM into a file as an XML
	'''
	f = open(xmlout,"wt")

	stm = Element("stm")

	states = SubElement(stm, 'states')
	stateselements = [
	Element('state', name=mySTM.statesDict[st].name)
		for st in mySTM.statesDict

	]
	states.extend(stateselements)

	transitions = SubElement(stm, 'transitions')
	transitionselements = [
	Element('transition', name=mySTM.transitionsDict[tr].name, cond=CCondToXMLCond(mySTM.transitionsDict[tr].cond), src=mySTM.transitionsDict[tr].src.name, dest=mySTM.transitionsDict[tr].dest.name)
		for tr in mySTM.transitionsDict
	]
	transitions.extend(transitionselements)
	
	f.write(prettify(stm))

	print "Updated XML file"

def removeStateLinks(name):
	'''
	Removes all transitions that include this state as a source or destination 
	from transitionsDict, srcDict and destDict
	'''
	destname = ""
	srcname = ""
	while name in mySTM.srcDict and len(mySTM.srcDict[name]) != 0:
		destname = mySTM.srcDict[name].pop()
		mySTM.destDict[destname].remove(name)
		mySTM.removeTransition(name, destname, 1)		

	while name in mySTM.destDict and len(mySTM.destDict[name]) != 0:
		srcname = mySTM.destDict[name].pop()									
		mySTM.srcDict[srcname].remove(name)
		mySTM.removeTransition(srcname, name, 1)		

def getTransitionsIncluding(name):
	'''
	Returns a list of transitions that include the state given by the name
	'''
	tlist = []
	for tr in mySTM.transitionsDict:
		if name in tr:
			tlist.append(tr)
	return tlist

def getAdjacentStates(name):
 	'''
 	Returns a list of adjacent states of the state given by the name
 	'''
	if name in mySTM.srcDict:
		return mySTM.srcDict[name]
	else:
		return []

def evalCondition(cond):
	'''
	Translates a condition into a python runnable line and returns True if the condition is true
	'''
	for inp in mySTM.inputsDict:
		if inp in cond:
			cond = cond.replace(inp, mySTM.inputsDict[inp])
	if " && " in cond:
		cond = cond.replace(" && ", " and ")
	if " || " in cond:
		cond = cond.replace(" || ", " or ")
	return eval(cond)

def getNextStateFrom(sname):
	'''
	Takes the list of adjacent and returns the first state with which the given state has a valid transition
	'''
	stateOptions = getAdjacentStates(sname)
	for so in stateOptions:
		if evalCondition(mySTM.transitionsDict[sname+"|"+so].cond) == True:
			return so
	return None

def getInputsFromCond(condtext):
	'''
	Returns a list with the unique inputs from a condition
	'''
	return list(set(re.findall(r"[\w']+", condtext)))

def addInputsIfNeeded(inputlist):
	'''
	Usually used when adding a new transition
	Adds the inputs that are not already existing
	'''
	for inp in inputlist:
		if not inp.isdigit():
			addInput(inp, "0")

def XMLCondToCCond(condtext):
	'''
	Translates a condition from XML to C form
	'''
	for comp in comparatorDict:
		if comp in condtext:
			condtext = condtext.replace(comp, comparatorDict[comp])
	return condtext

def CCondToXMLCond(condtext):
	'''
	Translates a condition from C to XML form
	'''
	for comp in comparatorRevDict:
		if comp in condtext:
			condtext = condtext.replace(comp, comparatorRevDict[comp])
	return condtext  	

def showDicts():
	'''
	Prints the srcDict and destDict dictionaries
	'''
	print mySTM.srcDict
	print mySTM.destDict

def getDefinesC():
	return """#define uint8 unsigned short
#define int32 int
"""

def getEnumsC():
	text = "\ntypedef enum {"
	for st in mySTM.statesDict:
		text += "\n\t" + mySTM.statesDict[st].name + ","
	text = text[:-1]
	text += "\n} MyStm_e;"
	text += "\n\nMyStm_e st;"
	return text

def getInputsC():
	text = "\n"
	for inp in  mySTM.inputsDict:
		text += "\nint32 " + inp + " = " + mySTM.inputsDict[inp] + ";" 	
	return text

def getFuncsC():
	text = ""
	for tr in mySTM.transitionsDict:
		text += "\n\nstatic uint8 " + mySTM.transitionsDict[tr].name + "() {\n\treturn "+ mySTM.transitionsDict[tr].cond + ";\n}"

	return text

def getImplementaionC():
	casesDict = {}
	for tr in mySTM.transitionsDict:
		casesDict.setdefault(mySTM.transitionsDict[tr].src.name, []).append("\n\t\t\tif (" + mySTM.transitionsDict[tr].name + "()) {\n\t\t\t\tst=" + mySTM.transitionsDict[tr].dest.name + ";\n\t\t\t}")

	text = "\n\nstatic uint8 STM_IMPLEMENTATION() {\n\tswitch (st) {"
	for case in casesDict:
		text += "\n\t\tcase " + case + ":"
		for ifs in casesDict[case]:
			text += ifs
		text += "\n\t\t\tbreak;"
	text += "\n\t}\n}"
	return text

def getMainC():
	text = "\n\nint main() {\n\treturn 0;\n}"
	return text

def updateC():
	'''
	Write the STM into a C file
	'''
	cfile = open(cout, "wt")
	cfile.write(getDefinesC())
	cfile.write(getEnumsC())
	cfile.write(getInputsC())
	cfile.write(getFuncsC())
	cfile.write(getImplementaionC())
	cfile.write(getMainC())
	print "Updated C file"

def updateFiles():
	'''
	Update both C and XML file
	'''
	updateXML()
	updateC()

def addStatesList(sList):
	'''
	Add a list of states to the STM
	'''
	for state in sList:
		mySTM.addState(state)

def addTransitionsList(tList):
	'''
	Add a list of transitions to the STM
	'''
	for transition in tList:
		mySTM.addTransition(*transition)

def truncateSTM():
	'''
	Literally truncate the STM
	'''
	mySTM.statesDict = {}
	mySTM.transitionsDict = {}
	mySTM.inputsDict = {}
	mySTM.srcDict = {}
	mySTM.destDict = {}

def updateInputsDict(keys, vals):
	'''
	Update the values of a list of inputs
	'''
	for key,val in zip(keys, vals):
		mySTM.inputsDict[key] = val

def modifyInputsToFit(cond):
	'''
	Split a condition into partial conditions
	Find all the parameters and their values for the condition to be true
	Modify the values so the condition is true
	'''
	params = []
	results = []
	for partCond in getPartialConditions(cond):
		p, r = getGoodInputValue(partCond)
		params.append(p)
		results.append(r)

	updateInputsDict(params, results)

def getGoodInputValue(cond):
	'''
	Given a condition, return the parameter in it and the value for it to make the condition true
	'''
	if "==" in cond:
		return (cond.split("==")[0], str(int(cond.split("==")[1])))
	elif "!=" in cond:
		return (cond.split("!=")[0], str(int(cond.split("!=")[1])+1))
	elif "<=" in cond:
		return (cond.split("<=")[0], int(cond.split("<=")[1]))
	elif "<" in cond:
		return (cond.split("<")[0], int(cond.split("<")[1])-1)
	elif ">=" in cond:
		return (cond.split(">=")[0], int(cond.split(">=")[1]))
	elif ">" in cond:
		return (cond.split(">")[0], int(cond.split(">")[1])+1)

def getPartialConditions(cond):
	'''
	Split a condition into partial conditions
	'''
	condList = []
	slicedCond = cond.split('&&')
	for sl in slicedCond:
		if sl != "":
			if '||' not in sl:
				condList.append(sl.replace(" ", ""))
			else:
				secondSlice = sl.split('||')
				for ssl in secondSlice:
					if ssl != "":
						condList.append(ssl.replace(" ", ""))
	return condList

def makeTrace(currState, steps):
	'''
	Return a full trace through the STM containing as many different states as possible without minding the inputs
	'''
	nrVisits = {}
	trace = []
	for state in mySTM.statesDict:
			nrVisits[state] = 0
	nrVisits[currState] += 1
	trace.append(currState)
	for i in range(steps):
		auxDict = {}
		adjStates = getAdjacentStates(currState)
		for adjS in adjStates:
			auxDict[adjS] = nrVisits[adjS]
		nextState = min(auxDict, key=auxDict.get)
		currState = nextState
		trace.append(currState)
		nrVisits[currState] += 1
	return trace


def fullTraceFrom(startState, nrOfSteps):
	'''
	Return a list of states representing a path through the STM such that it includes as many states as possible
	'''
	return makeTrace(startState, nrOfSteps)
	


#Main
##################################################################################################################

mySTM = STMClass({},{},{})

