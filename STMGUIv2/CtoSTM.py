def getStatesList(file):
	'''
	Reads the states from the C file and returns them as a list
	'''
	f = open(file, 'r')
	text = f.read()
	states = []
	for i in range(1, len(text.split("typedef enum {")[1].split("}")[0].split("\n"))):
		x = text.split("typedef enum {")[1].split("}")[0].split("\n")[i].replace(",", "")
		x = x.replace("\t", "")
		if x != "":
			states.append(x)
	f.close()
	return states
	
def getTransitionsList(file):
	'''
	Reads the transitions from the C file and returns them as a list
	'''
	f = open(file, 'r')
	text = f.read()
	transitions = []
	cases = text.split("switch (st) {")[1].split("case ")
	for case in cases:
		case = case.replace("\t", "")
		case = case.replace("\n", "")
		case = case.split("break;")[0]
		if case != "":
			splitcase = case.split("if (")
			for i in range(1, len(splitcase)):
				transitions.append([splitcase[i].split("())")[0], text.split("static uint8 " + splitcase[i].split("())")[0] + "()")[1].split("return ")[1].split(";")[0],case.split(":")[0], splitcase[i].split("st=")[1].split(";")[0]])
	f.close()
	return transitions