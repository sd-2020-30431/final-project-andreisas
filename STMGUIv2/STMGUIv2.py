from Tkinter import *
from shutil import copyfile
from itertools import cycle
import ttk
import CRUD
import pygame
import threading
import random
import os
import math
import time
import logging
import CtoSTM as fromC
import XMLtoSTM as fromXML

#Config
##############################################################################################################################################
tkWindowSize = "200x450"
tkWindowPosX = 40
tkWindowPosY = 135
pyWindowSize = (1440, 810)
pyWindowPosX = 250
pyWindowPosY = 135
popUpMsgSize = "150x100"
popUpMsgPosX = 25
popUpMsgPosY = 100
stateRectHeight = 30
stateRectWidth = 100
infoRectWidth = 100
infoRectHeight = 20
fontSize = 20
statePickTime = 0.01
coordFile = "Data/CoordFile.txt"
inputsFile = "Data/inputs.csv"
logfile = "Logs/logfile.log"
runlogfile = "Logs/runLog.log"
xmlin = "Data/XMLFile.xml"
cin = "Data/CFile.c"
color = {	
		"active":(86, 224, 67), "inactive":(150,150,150), "background":(220,220,220), 
		"info":(150,220,50), "pickedup": (0, 150, 250), "normal": (255, 255, 255), 
		"fontcolor": (0, 0, 0), "SteelBlue1": (224, 67, 188), "running": (220, 40, 50)
		}
key = {"enter": 28, "backspace": 14, "delete": 83}

#Classes
##############################################################################################################################################
class PyWindowClass:
	def __init__(self, app):
		self.app = app
		self.inputsHash = {}
		self.mouseLeftPressed = 0
		self.lastMousePressedTime = time.time()
		self.timeStep = 0.1
		self.stateNameToBeSpawned = ""
		self.collision = 1
		self.info = 1
		self.animationRun = 0
		self.animationSteps = 0
		self.animationTime = 0
		self.animationTrace = []
		self.animationLog = ""
		self.currAnimationState = ""
		self.stateCoordinates = {} #statename: XposxYpos (left corner)
		self.transitionCoordinates = {} #src|dest: XposxYpos (circle's center)
		self.stateColor = {}#statename: (R, G, B)
		self.transitionColor = {}#src|dest: (R, G, B)
		os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (pyWindowPosX,pyWindowPosY)
		pygame.init()
		pygame.display.set_icon(pygame.image.load('icon.ico'))
		self.pywindow = pygame.display.set_mode(pyWindowSize)
		self.pywindow.fill(color["background"])
		pygame.display.set_caption("STM View")

		pygame.mouse.set_cursor(*pygame.cursors.tri_left)
		self.paintAllStates(color["active"])
		self.paintAllTransitions(color["inactive"])


	def paintAllTransitions(self, color):
		'''
		Change all transition colors in transitionColor to 'color'
		'''
		self.transitionColor = {x: color for x in CRUD.mySTM.transitionsDict}

	def paintAllStates(self, color):
		'''
		Change all state colors in stateColor to 'color'
		'''
		self.stateColor = {x: color for x in CRUD.mySTM.statesDict}

	def updatePyWindow(self):
		'''
		Draw all the states and transitions of the STM
		'''
		self.pywindow.fill(color["background"])
		for tr in CRUD.mySTM.transitionsDict:
			srcx, srcy = self.stateCoordinates[CRUD.mySTM.transitionsDict[tr].src.name].split("x")
			destx, desty = self.stateCoordinates[CRUD.mySTM.transitionsDict[tr].dest.name].split("x")
			self.spawnTransitionLine(self.getCenterOfShape(int(srcx), int(srcy)), self.getCenterOfShape(int(destx), int(desty)), tr)
		for sc in self.stateCoordinates:
			x, y = self.stateCoordinates[sc].split("x")
			self.spawnStateRect(int(x), int(y), str(sc))

	def pyWindowThreadUpdate(self):
		'''
		Update using threads
		'''
		pyUpdateThread = threading.Thread(target=self.updatePyWindow)
		pyUpdateThread.start()
		pyUpdateThread.join()

	def getCenterOfShape(self, x, y):
		'''
		Returns the center of a state rectangle having the upper left corner at (x, y)
		'''
		cx = x + stateRectWidth/2
		cy = y + stateRectHeight/2
		return cx, cy

	def spawnTransitionName(self, x, y, name):
		'''
		Write the name of a transition at (x, y)
		'''
		font = pygame.font.SysFont("arial", fontSize, False)
		text = font.render(name, True, (0,0,0))
		self.pywindow.blit(text, (x, y))

	def spawnTransitionLine(self, p1, p2, name):
		'''
		Draw a transition as a line with an arrow and a name on it
		'''
		if name.split("|")[0] > name.split("|")[1]:
			srcx = p1[0] 
			srcy = p1[1] + stateRectHeight/4
			destx = p2[0] 
			desty = p2[1] + stateRectHeight/4
		else:
			srcx = p1[0] 
			srcy = p1[1] - stateRectHeight/4
			destx = p2[0] 
			desty = p2[1] - stateRectHeight/4
		H = 10
		L = 20
		ix = (srcx + destx)//2
		ix = (ix + destx)//2
		iy = (srcy + desty)//2
		iy = (iy + desty)//2
		if ix != srcx or iy != srcy:
			dX = ix - srcx
			dY = iy - srcy
			lineLen = math.sqrt(dX**2 + dY**2)
			udX = dX / lineLen
			udY = dY / lineLen
			perpX = -udY
			perpY = udX
			leftX = ix - L * udX + H * perpX
			leftY = iy - L * udY + H * perpY
			rightX = ix - L * udX - H * perpX
			rightY = iy - L * udY - H * perpY
			pygame.draw.line(self.pywindow, self.transitionColor[name], (srcx, srcy), (destx,desty), 3)
			pygame.draw.line(self.pywindow, self.transitionColor[name], (leftX, leftY), (ix, iy), 5)
			pygame.draw.line(self.pywindow, self.transitionColor[name], (rightX, rightY), (ix, iy), 5)
			self.transitionCoordinates[name] = str(int((ix + leftX + rightX)/3)) + "x" + str(int((iy + leftY + rightY)/3))
			self.spawnTransitionName(int((ix + leftX + rightX)/3), int((iy + leftY + rightY)/3), CRUD.mySTM.transitionsDict[name].name + " (" + CRUD.mySTM.transitionsDict[name].cond + ")")

	def spawnStateRect(self, x, y, name):
		'''
		Draw a state as a rectangle and a name
		'''
		pygame.draw.rect(self.pywindow, self.stateColor[name], (x,y,stateRectWidth,stateRectHeight))
		font = pygame.font.SysFont("arial", fontSize, True)
		text = font.render(name, True, color["fontcolor"])
		self.pywindow.blit(text, (x + (stateRectWidth/2 - text.get_width()/2), y + (stateRectHeight/2 - text.get_height()/2)))

	def spawnInfoRect(self, x, y, name, color):
		'''
		Draw a rectangle with text in it
		'''
		pygame.draw.rect(self.pywindow, color, (x,y,infoRectWidth,infoRectHeight))
		font = pygame.font.SysFont("arial", 15)
		text = font.render(name, True, (0,0,0))
		self.pywindow.blit(text, (x + (infoRectWidth/2 - text.get_width()/2), y + (infoRectHeight/2 - text.get_height()/2)))

	def isEmptySpace(self, x, y):
		'''
		Verify if a state rectangle can be placed at (x, y) by verifying the colors at it's corners
		'''
		if self.collision == -1:
			return True
		cond4 = 0
		if x + stateRectWidth >= pyWindowSize[0]:
			return False
		if y + stateRectHeight >= pyWindowSize[1]:
			return False
		okColors = [color["background"], color["inactive"], color["pickedup"], color["running"]]
		if self.pywindow.get_at((x, y))[:3] in okColors:
			cond4 += 1
		if self.pywindow.get_at((x+stateRectWidth, y))[:3] in okColors:
			cond4+= 1
		if self.pywindow.get_at((x+stateRectWidth, y+stateRectHeight))[:3] in okColors:
			cond4+= 1
		if self.pywindow.get_at((x, y+stateRectHeight))[:3] in okColors:
			cond4+= 1
		if cond4 == 4:
			return True
		else:
			return False

	def getTransitionNameAtPos(self, x, y):
		'''
		Return the name of the transition located at (x, y)
		'''
		for tc in self.transitionCoordinates:
			tx, ty = self.transitionCoordinates[tc].split("x")
			if math.sqrt((x - int(tx))**2 + (y - int(ty))**2) <= 30:
				return tc
		return None

	def getStateNameAtPos(self, x, y):
		'''
		Return the name of the state located at (x, y)
		'''
		for sc in self.stateCoordinates:
			sx, sy = self.stateCoordinates[sc].split("x")
			if x >= int(sx) and x <= int(sx)+stateRectWidth and y >= int(sy) and y <= int(sy)+stateRectHeight:
				return sc
		return None

	def statePickedMode(self):
		'''
		If there is a picked-up state and the space is empty change the location of that state to the current one and refresh the window
		'''
		if self.stateNameToBeSpawned != "":
			if self.isEmptySpace(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
				self.stateCoordinates[self.stateNameToBeSpawned] = str(pygame.mouse.get_pos()[0]+1) + "x" + str(pygame.mouse.get_pos()[1]+1)
				self.pyWindowThreadUpdate()

	def statePick(self):
		'''
		If animation is off, the leftMouseButton is pressed a certain amount of time, the click is on a state and there is not other state
		That needs to be spawned, pick the clicked state (put it's name into stateNameToBeSpawned)
		'''
		if self.animationRun == 0:
			if time.time() - self.lastMousePressedTime >= statePickTime and self.mouseLeftPressed == 1 and self.stateNameToBeSpawned == "" and self.getStateNameAtPos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) != None:
				self.stateNameToBeSpawned = self.getStateNameAtPos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
				self.stateColor[self.stateNameToBeSpawned] = color["pickedup"]
				pygame.mouse.set_cursor(*pygame.cursors.diamond)

	def stateRelease(self):
		'''
		The state needs to be released so empty the stateNameToBeSpawned and change the color to active
		'''
		threading.Thread(target=self.app.updateCoordFile).start()
		self.stateColor[self.stateNameToBeSpawned] = color["active"]
		self.stateNameToBeSpawned = ""
		pygame.mouse.set_cursor(*pygame.cursors.tri_left)
		self.pyWindowThreadUpdate()

	def selectState(self):
		'''
		Select a state
			- If in state mode, put it's name in the first entry
			- If in transition mode, write the text from destination entry into the source entry and write the name of the state into the destination entry
		'''
		mx, my = pygame.mouse.get_pos()
		whatIsClicked = self.getStateNameAtPos(mx, my)
		if whatIsClicked != self.stateNameToBeSpawned:
			if whatIsClicked != None:
				if self.app.modeOption == 1:
					self.app.tkpart.entry1.delete(0, END)
					self.app.tkpart.entry1.insert(0, whatIsClicked)
				elif self.app.modeOption == 2:
					self.app.tkpart.entry3.delete(0, END)
					self.app.tkpart.entry3.insert(0, self.app.tkpart.entry4.get())
					self.app.tkpart.entry4.delete(0, END)
					self.app.tkpart.entry4.insert(0, whatIsClicked)

	def selectTransition(self):
		'''
		Select a transition and fill all the entries with it's data
		'''
		mx, my = pygame.mouse.get_pos()
		whatIsClicked = self.getTransitionNameAtPos(mx, my)
		if whatIsClicked != None:
			tname = CRUD.mySTM.transitionsDict[whatIsClicked].name
			tcond = CRUD.mySTM.transitionsDict[whatIsClicked].cond
			tsrc = CRUD.mySTM.transitionsDict[whatIsClicked].src.name
			tdest = CRUD.mySTM.transitionsDict[whatIsClicked].dest.name
			self.app.tkpart.entry1.delete(0, END)
			self.app.tkpart.entry1.insert(0, tname)
			self.app.tkpart.entry2.delete(0, END)
			self.app.tkpart.entry2.insert(0, tcond)
			self.app.tkpart.entry3.delete(0, END)
			self.app.tkpart.entry3.insert(0, tsrc)
			self.app.tkpart.entry4.delete(0, END)
			self.app.tkpart.entry4.insert(0, tdest)

	def showSystemInfo(self):
		'''
		If system info is enabled show: Cursor coordinates, mode, collision
		'''
		if self.info == 1:
			self.showCursorCoordinates()
			self.showMode()
			self.showCollisionInfo()

	def showCursorCoordinates(self):
		'''
		Spawn an info rectangle with the cursor coordinates
		'''
		self.spawnInfoRect(0, 0, str(pygame.mouse.get_pos()[0]) + ", " + str(pygame.mouse.get_pos()[1]), color["info"])

	def showMode(self):
		'''
		Spawn an info rectangle with the current mode
		'''
		if self.app.modeOption == 1:
			self.spawnInfoRect(infoRectWidth+2, 0, "State Mode", color["info"])
		elif self.app.modeOption == 2:
			self.spawnInfoRect(infoRectWidth+2, 0, "Transition Mode", color["info"])

	def showCollisionInfo(self):
		'''
		Spawn an info rectangle showing if the collision is on or off
		'''
		if self.collision == 1:
			self.spawnInfoRect(2*infoRectWidth+3, 0, "Collision: On", color["info"])
		else:
			self.spawnInfoRect(2*infoRectWidth+3, 0, "Collision: Off", color["info"])

	def verifyTimeEvents(self):
		'''
		At the specified period (time.Step) do the necessary time events
		'''
		if time.time() - self.animationTime >= self.timeStep:
			self.animationTime = time.time()
			self.animationTryStep()

	def verifyKeyEvents(self):
		'''
		Manage the pressing and releasing of the keys
		'''
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				self.app.run = False
			if event.type == pygame.KEYDOWN:
				if event.scancode == key["enter"]:
					self.app.tkpart.addBtnCmd()
				elif event.scancode == key["delete"] or event.scancode == key["backspace"]:
					self.app.tkpart.removeBtnCmd()
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if self.app.modeOption == 1:
					self.mouseLeftPressed = 1
					self.lastMousePressedTime = time.time()
				elif self.app.modeOption == 2:
					self.selectTransition()
				self.selectState()
			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				if self.app.modeOption == 1:
					self.mouseLeftPressed = 0
					self.stateRelease()
			if event.type == pygame.MOUSEBUTTONDOWN and event.button in [4, 5]:
				self.app.toggleMode()
			if self.mouseLeftPressed == 1:
				self.statePick()

	def animationStartRun(self):
		'''
		Get from the entries: the start state, the nr of steps and the timeStep
		Update the inputHash
		Make the trace according to the inputHash and cycle it
		If a timeStep is not given, the last one will be used
		Update the pyWindow
		'''
		self.animationTime = time.time()
	 	self.app.tkpart.startBtn.config(text="Stop", bg="red")
		self.animationRun = 1
	 	self.currAnimationState = str(self.app.tkpart.omStateVar.get())
	 	self.stateColor[self.currAnimationState] = color["running"]
	 	self.animationSteps = int(self.app.tkpart.entry5.get())
	 	self.updateInputsHash()
	 	trace = self.updateTrace(self.currAnimationState, self.animationSteps)
	 	self.animationTrace = cycle(trace)
	 	if self.app.tkpart.entry7.get() != "":
	 		self.timeStep = float(self.app.tkpart.entry7.get())
	 	self.animationLog += "Run - " + str(time.asctime()) + "\n" + str(round(time.time() - self.animationTime,4)) + " - In state " + self.currAnimationState
	 	self.pyWindowThreadUpdate()

	def animationStopRun(self):
		'''
		Paint the states and transitions according to the current mode
		Log the event
		Update the pyWindow
		'''
		self.app.tkpart.startBtn.config(text="Start", bg="green")
		self.animationRun = 0
		if self.app.modeOption == 1:
			self.paintAllStates(color["active"])
			self.paintAllTransitions(color["inactive"])
		elif self.app.modeOption == 2:
			self.paintAllStates(color["inactive"])
			self.paintAllTransitions(color["active"])
		self.animationLog += "\nEnded after " + str(round(time.time() - self.animationTime,4)) + " seconds"
		self.app.logThisIn(self.animationLog, runlogfile, 'w')
		self.animationLog = ""
		self.pyWindowThreadUpdate()

	def animationTryStep(self):
		'''
		If the animation runs and there are states left in the trace, color the state and the coresponding transition
		A step is made even if the animation remains on the same state
		If all the steps have been made, stop the animation
		'''
		nextstate = ""
		if self.animationRun == 1:
			if self.animationSteps > 0:
				nextstate = next(self.animationTrace)
				self.animationSteps -= 1
				if nextstate != None:
					self.animationLog += "\n" + str(round(time.time() - self.animationTime,4)) + " - In state " + nextstate
					self.transitionColor[self.currAnimationState + "|" + nextstate] = color["running"]
					self.stateColor[self.currAnimationState] = color["active"]
					self.currAnimationState = nextstate
					self.stateColor[self.currAnimationState] = color["running"]
					self.pyWindowThreadUpdate()
			else:
				self.animationStopRun()

	def updateTrace(self, startState, steps):
		'''
		Return a full trace according to the inputs in the inputHash 
		'''
		currState = startState
		trace = [currState]
		for i in range(steps):
			CRUD.updateInputsDict(self.inputsHash[i].keys(), self.inputsHash[i].values())
			nextState = CRUD.getNextStateFrom(currState)
			trace.append(nextState)
			currState = nextState
		return trace

	def updateInputsHash(self):
		'''
		Read the input csv and insert it into the inputHash
		'''
		self.inputsHash = {}
		for i in range(self.animationSteps):
			self.inputsHash[i] = {}
		f = open(inputsFile, 'r')
		line = f.readline()
		for line in f:
			inputVals = line.replace("\n", "").split(",") 
			for i in range(1, self.animationSteps+1):
				self.inputsHash[i-1][inputVals[0]] = inputVals[i]

	def generateInputs(self):
		'''
		Get from the entries, the startState, the nr of steps and the timeStep
		Generate a set of inputs which make possible a trace through the STM that includes as many different states as possible
		Write the inputs along with a times list into the CSV file
		'''
		if self.app.tkpart.omStateVar.get() == "-select-" or self.app.tkpart.entry5.get() == "" or self.app.tkpart.entry7.get() == "":
			return 0
		currState = self.app.tkpart.omStateVar.get()
		nrOfSteps = int(self.app.tkpart.entry5.get())
		self.timeStep = float(self.app.tkpart.entry7.get())
		inputChangeTimes = []
		self.inputsHash = {}
		trace = CRUD.fullTraceFrom(currState, nrOfSteps)
		for inp in CRUD.mySTM.inputsDict:
			self.inputsHash[inp] = []
		for i in range(1, len(trace)):
			nextState = trace[i]
			transitionCond = CRUD.mySTM.transitionsDict[currState+"|"+nextState].cond
			CRUD.modifyInputsToFit(transitionCond)
			changeTime = (i-2)*self.timeStep + self.timeStep/2
			if changeTime < 0:
				changeTime = 0
			inputChangeTimes.append(changeTime)

			for inp in CRUD.mySTM.inputsDict:
				self.inputsHash[inp].append(CRUD.mySTM.inputsDict[inp])

			currState = nextState

		f = open(inputsFile, "w")
		f.write("0")
		for t in inputChangeTimes:
			f.write(","+str(t))
		for inp in self.inputsHash:
			f.write("\n"+str(inp))
			for i in self.inputsHash[inp]:
				f.write(","+str(i))
		f.close()	

class TkWindowClass:
	def __init__(self, app):
		self.app = app
		self.tkwindow = Tk()
		self.tkwindow.update()
		self.omStateVar = StringVar(self.tkwindow)
		self.omStateVar.set("-select-")
		self.omStateVar.trace("w", self.changeStartState)
		self.omFileVar = StringVar(self.tkwindow)
		self.omFileVar.set("-select-")
		self.omFileVar.trace("w", self.changeImportFile)
		self.tkwindow.title("Menu")
		self.tkwindow.protocol("WM_DELETE_WINDOW", self.disable_event)
		self.tkwindow.geometry(tkWindowSize + "+" + str(tkWindowPosX) + "+" + str(tkWindowPosY))
		self.tkwindow.columnconfigure(0, weight=100)
		self.tkwindow.columnconfigure(1, weight=100)
		self.tabbedpane = ttk.Notebook(self.tkwindow)
		self.tabbedpane.grid(row=0, column=0, columnspan=30, rowspan=30, sticky=N+E+S+W)
		self.page1 = ttk.Frame(self.tabbedpane)
		self.page1.columnconfigure(0, weight=100)
		self.page1.columnconfigure(1, weight=100)
		self.tabbedpane.add(self.page1, text="CRUD")
		self.page2 = ttk.Frame(self.tabbedpane)
		self.page1.columnconfigure(0, weight=100)
		self.page1.columnconfigure(1, weight=100)
		self.tabbedpane.add(self.page2, text="Animation")
		self.page3 = ttk.Frame(self.tabbedpane)
		self.page1.columnconfigure(0, weight=100)
		self.page1.columnconfigure(1, weight=100)
		self.tabbedpane.add(self.page3, text="Files")

		self.label1 = Label(self.page1, text="State name:", fg="black", state=NORMAL)
		self.label1.grid(row=0, column=0, columnspan=2, sticky=N+S+W)
		self.label2 = Label(self.page1, text="", fg="black", state=DISABLED)
		self.label2.grid(row=2, column=0, columnspan=2, sticky=N+S+W)
		self.label3 = Label(self.page1, text="", fg="black", state=DISABLED)
		self.label3.grid(row=4, column=0, columnspan=2, sticky=N+S+W)
		self.label4 = Label(self.page1, text="", fg="black", state=DISABLED)
		self.label4.grid(row=6, column=0, columnspan=2, sticky=N+S+W)
		self.label5 = Label(self.page2, text="Starting state:", fg="black", state=NORMAL)
		self.label5.grid(row=0, column=0, sticky=N+S+W)
		self.label6 = Label(self.page2, text="Steps:", fg="black", state=NORMAL)
		self.label6.grid(row=1, column=0, sticky=N+S+W)
		self.label7 = Label(self.page3, text="Import file: ", fg="black", state=NORMAL)
		self.label7.grid(row=0, column=0, sticky=N+E+S+W)
		self.label8 = Label(self.page3, text="Save as: ", fg="black", state=NORMAL)
		self.label8.grid(row=2, column=0, sticky=N+S+W)
		self.label9 = Label(self.page2, text="Timestep(s): ", fg="black", state=NORMAL)
		self.label9.grid(row=2, column=0, sticky=N+S+W)

		self.entry1 = Entry(self.page1, state=NORMAL)
		self.entry1.grid(row=1, column=0, columnspan=2, sticky=N+E+S+W)
		self.entry2 = Entry(self.page1, state=DISABLED)
		self.entry2.grid(row=3, column=0, columnspan=2, sticky=N+E+S+W)
		self.entry3 = Entry(self.page1, state=DISABLED)
		self.entry3.grid(row=5, column=0, columnspan=2, sticky=N+E+S+W)
		self.entry4 = Entry(self.page1, state=DISABLED)
		self.entry4.grid(row=7, column=0, columnspan=2, sticky=N+E+S+W)
		self.entry5 = Entry(self.page2, state=NORMAL)
		self.entry5.grid(row=1, column=1, sticky=N+E+S+W)
		self.entry6 = Entry(self.page3, state=NORMAL)
		self.entry6.grid(row=2, column=1, sticky=N+E+S+W)
		self.entry7 = Entry(self.page2, state=NORMAL)
		self.entry7.grid(row=2, column=1, sticky=N+E+S+W)
	
		self.addBtn = Button(self.page1, text="Add", bg="SteelBlue1", command=self.addBtnCmd)
		self.addBtn.grid(row=8, column=0, sticky=N+E+S+W)
		self.removeBtn = Button(self.page1, text="Remove", bg="SteelBlue1", command=self.removeBtnCmd)
		self.removeBtn.grid(row=8, column=1, sticky=N+E+S+W)
		self.updateBtn = Button(self.page1, text="Update", bg="SteelBlue1", command=self.updateBtnCmd)
		self.updateBtn.grid(row=9, column=0, sticky=N+E+S+W)
		self.findBtn = Button(self.page1, text="Find", bg="SteelBlue1", command=self.findBtnCmd)
		self.findBtn.grid(row=9, column=1, sticky=N+E+S+W)
		self.toggleCollisionBtn = Button(self.page1, text="Toggle Collision", bg="SteelBlue1", command=self.toggleCollisionBtnCmd)
		self.toggleCollisionBtn.grid(row=10, column=0, columnspan=2, sticky=N+E+S+W)
		self.toggleInfoBtn = Button(self.page1, text="Toggle Info", bg="SteelBlue1", command=self.toggleInfoBtnCmd)
		self.toggleInfoBtn.grid(row=11, column=0, columnspan=2, sticky=N+E+W)
		self.startBtn = Button(self.page2, text="Start", bg="green", command=self.toggleRunBtnCmd)
		self.startBtn.grid(row=4, column=0, sticky=N+S+E+W)
		self.genInputsBtn = Button(self.page2, text="Generate Inputs", bg="SteelBlue1", command=self.generateInputsBtnCmd)
		self.genInputsBtn.grid(row=4, column=1, sticky=N+S+E+W)
		self.importBtn = Button(self.page3, text="Import", bg="SteelBlue1", command=self.importFileBtnCmd)
		self.importBtn.grid(row=1, column=0, sticky=N+S+E+W)
		self.clearBtn = Button(self.tkwindow, text="Clear", bg="lightblue", command=self.clearBtnCmd)
		self.clearBtn.grid(row=31, column=0, sticky=N+E+S+W)
		self.saveBtn = Button(self.page3, text="Save", bg="SteelBlue1", command=self.saveFileBtnCmd)
		self.saveBtn.grid(row=3, column=0, sticky=N+E+S+W)
		
		self.statesOptionMenu = OptionMenu(self.page2, self.omStateVar, "")
		self.statesOptionMenu.grid(row=0, column=1, sticky=N+E+S+W)
		self.filesOptionMenu = OptionMenu(self.page3, self.omFileVar, "")
		self.filesOptionMenu.grid(row=0, column=1, sticky=N+E+S+W)

	def changeStartState(self, *args):
		pass

	def changeImportFile(self, *args):
		pass

	def disable_event(self):
		self.app.run = 0

	def emptyEntries(self):
		'''
		Empty the entries from the CRUD page
		'''
		self.entry1.delete(0, END)
		self.entry1.insert(0, "")
		self.entry2.delete(0, END)
		self.entry2.insert(0, "")
		self.entry3.delete(0, END)
		self.entry3.insert(0, "")
		self.entry4.delete(0, END)
		self.entry4.insert(0, "")

	def stateMode(self):
		'''
		Enable only the first entry on the CRUD page
		'''
		self.emptyEntries()
		self.label1.config(text="State name: ", state=NORMAL)
		self.label2.config(text="", state=DISABLED)
		self.label3.config(text="", state=DISABLED)
		self.label4.config(text="", state=DISABLED)
		self.entry1.config(state=NORMAL)
		self.entry2.config(state=DISABLED)
		self.entry3.config(state=DISABLED)
		self.entry4.config(state=DISABLED)

	def transitionMode(self):
		'''
		Enable all the entries on the CRUD page
		'''
		self.emptyEntries()
		self.label1.config(text="Transition name: ", state=NORMAL)
		self.label2.config(text="Condition: ", state=NORMAL)
		self.label3.config(text="Source name: ", state=NORMAL)
		self.label4.config(text="Destination name: ", state=NORMAL)
		self.entry1.config(state=NORMAL)
		self.entry2.config(state=NORMAL)
		self.entry3.config(state=NORMAL)
		self.entry4.config(state=NORMAL)

	def popupmsg(self, msg):
		'''
		Create a pop-up message with the text 'msg'
		'''
		popup = Toplevel()
		popup.title("!")
		popup.geometry(popUpMsgSize + "+" + str(tkWindowPosX + popUpMsgPosX) + "+" + str(tkWindowPosY + popUpMsgPosY))
		message = Message(popup, text=msg)
		message.pack()
		button = Button(popup, text="Ok", command=popup.destroy)
		button.pack()

	def updateStartStateMenu(self):
		'''
		Update the option of the StartStateMenu
		'''
		self.omStateVar.set("-select-")
		menu = self.statesOptionMenu["menu"]
		menu.delete(0, END)
		for st in CRUD.mySTM.statesDict:
			menu.add_command(label=st, command=lambda value=st: self.omStateVar.set(value))
		self.tkwindow.update()

	def updateImportMenu(self):
		'''
		Update the options of the ImportMenu
		'''
		menu = self.filesOptionMenu["menu"]
		menu.delete(0, END)
		for r, d, f in os.walk("Inputs"):
			for file in f:
				if file.split(".")[1] in "xml/c":
					 menu.add_command(label=file, command=lambda value=file: self.omFileVar.set(value))
		self.tkwindow.update()

	def addBtnCmd(self):
		'''
		If it's state mode
			- If possible spawn a state
		If it's transition mode
			- If possible spawn a transition
		Log the event
		'''
		if self.app.modeOption == 1:
			sname = self.entry1.get()
			if sname == "":
				return 0
			result = CRUD.addState(sname)
			if result == "Success":
				self.app.logThisIn(str(time.asctime()) + " - " + "State was added (name: " + sname + ")\n", logfile, 'a')
				self.app.pypart.stateNameToBeSpawned = sname
				self.app.pypart.stateColor[self.app.pypart.stateNameToBeSpawned] = color["pickedup"]
				self.emptyEntries()
				self.updateStartStateMenu()
				self.app.pypart.stateCoordinates[sname] = "100x100"
				threading.Thread(target=self.app.updateSTMFiles).start()
				threading.Thread(target=self.app.updateCoordFile).start()
			else:
				self.popupmsg(result)
			
		elif self.app.modeOption == 2:
			result = CRUD.addTransition(self.entry1.get(), self.entry2.get(), self.entry3.get(), self.entry4.get())
			if result != "Source or/and destination not existing":
				self.app.logThisIn(str(time.asctime()) + " - " + "Transition was added (name: " + self.entry1.get() + ", condition: " + self.entry2.get() + ", source: " + self.entry3.get() + ", destination: " + self.entry4.get() + ")\n", logfile, 'a')
				threading.Thread(target=self.app.updateSTMFiles).start()
				self.app.pypart.transitionColor[self.entry3.get() + "|" + self.entry4.get()] = color["active"]
				self.emptyEntries()
				self.app.pypart.pyWindowThreadUpdate()
			else:
				self.popupmsg(result)

	def removeBtnCmd(self):
		'''
		If it's state mode:
			- If it's possible remove the state
		If it's transition mode:
			- If it's possible remove the transition
		Log the event
		'''
		if self.app.modeOption == 1:
			sname = self.entry1.get()
			deletedTransitions = CRUD.getTransitionsIncluding(sname)
			result = CRUD.removeState(sname)
			if result == "Success":
				self.app.logThisIn(str(time.asctime()) + " - " + "State was deleted (name: " + sname + ")\n", logfile, 'a')
				del self.app.pypart.stateCoordinates[sname]
				for dt in deletedTransitions:
					self.app.logThisIn(str(time.asctime()) + " - " + "Transition was deleted (source: " + dt.split("|")[0] + ", destination: " + dt.split("|")[1] + ")\n", logfile, 'a')
					del self.app.pypart.transitionCoordinates[dt]
				threading.Thread(target=self.app.updateCoordFile).start()
				threading.Thread(target=self.app.updateSTMFiles).start()
				self.emptyEntries()
				self.app.pypart.pyWindowThreadUpdate()
				self.updateStartStateMenu()
			else:
				self.popupmsg(result)
		elif self.app.modeOption == 2:
			src = self.entry3.get()
			dest = self.entry4.get()
			result = CRUD.removeTransition(src, dest)
			if result == "Success":
				self.app.logThisIn(str(time.asctime()) + " - " + "Transition was deleted (source: " + src + ", destination: " + dest + ")\n", logfile, 'a')
				threading.Thread(target=self.app.updateSTMFiles).start()
				del self.app.pypart.transitionCoordinates[src + "|" + dest]
				self.emptyEntries()
				self.app.pypart.pyWindowThreadUpdate()
			else:
				self.popupmsg(result)

	def updateBtnCmd(self):
		'''
		If it's state mode:
			- If possible update the state
		If it's transition mode:
			- If possible update the transition
		Log the event
		'''
		if self.app.modeOption == 1:
			sname = self.entry1.get()
			result = CRUD.updateState(sname)
			if result == "Success":
				self.app.logThisIn(str(time.asctime()) + " - " + "State was updated (name: " + sname + ")\n", logfile, 'a')
				threading.Thread(target=self.app.updateSTMFiles).start()
				self.emptyEntries()
				self.app.pypart.pyWindowThreadUpdate()
			else:
				self.popupmsg(result)
		elif self.app.modeOption == 2:
			result = CRUD.updateTransition(self.entry1.get(), self.entry2.get(), self.entry3.get(), self.entry4.get())
			if result == "Success":
				self.app.logThisIn(str(time.asctime()) + " - " + "Transition was updated (name: " + self.entry1.get() + ", condition: " + self.entry2.get() + ", source: " + self.entry3.get() + ", destination: " + self.entry4.get() + ")\n", logfile, 'a')
				threading.Thread(target=self.app.updateSTMFiles).start()
				self.emptyEntries()
				self.app.pypart.pyWindowThreadUpdate()
			else:
				self.popupmsg(result)

	def findBtnCmd(self):
		'''
		If it's state mode find the state
		If it's transition mode fint the transition
		'''
		if self.app.modeOption == 1:
			result = CRUD.findState(self.entry1.get())
			self.popupmsg(result)
		elif self.app.modeOption == 2:
			result = CRUD.findTransition(self.entry3.get(), self.entry4.get())
			self.popupmsg(result)

	def toggleCollisionBtnCmd(self):
		'''
		Toggle the collision option
		'''
		self.app.pypart.collision *= -1

	def toggleInfoBtnCmd(self):
		'''
		Toggle the info option
		'''
		self.app.pypart.info *= -1
		self.app.pypart.pyWindowThreadUpdate()

	def toggleRunBtnCmd(self):
		'''
		If animation is on, stop it, else, start it
		'''
		if self.app.pypart.animationRun == 0:
			if self.entry5.get() != "" and str(self.omStateVar.get()) != "-select-":
			 	self.app.pypart.animationStartRun()
		else:
			self.app.pypart.animationStopRun()

	def generateInputsBtnCmd(self):
		'''
		Call generateInputs from the pypart Class
		'''
		self.app.pypart.generateInputs()

	def importFileBtnCmd(self):
		'''
		Truncate the current STM
		Log the event
		Copy the files selected in the import menu into the Data folder
		Read the coordinates and paint the states and transitions
		Update the startStateMenu
		Update the pyWindow
		'''
		filename = str(self.omFileVar.get())
		if filename != "-select-":
			if filename.split(".")[1] in "xml/c":
				self.clearBtnCmd()
				self.app.logThisIn(str(time.asctime()) + " - " + "Imported " + filename + "\n", logfile, 'a')
				if filename.split(".")[1] == "xml":
					self.app.initSTMfromXML("Inputs/"+filename.split(".")[0] + "/" + filename)
				elif filename.split(".")[1] == "c":
					self.app.initSTMfromC("Inputs/"+filename.split(".")[0] + "/" + filename)
				copyfile("Inputs/"+filename.split(".")[0] + "/" + filename.split(".")[0] + "coord.txt", "Data/CoordFile.txt")
				copyfile("Inputs/"+filename.split(".")[0] + "/" + filename.split(".")[0] + "inputs.csv", "Data/inputs.csv")
				self.app.readCoordinates()
				self.app.pypart.paintAllStates(color["active"])
				self.app.pypart.paintAllTransitions(color["inactive"])
				self.updateStartStateMenu()
				self.app.pypart.pyWindowThreadUpdate()

	def saveFileBtnCmd(self):
		'''
		Save the files from the Data folder into the input folder as a new folder representing an STM
		Files saved: XML/C, inputs, coordinates
		'''
		filename = str(self.entry6.get())
		if filename.split(".")[1] in "xml/c":
			self.app.logThisIn(str(time.asctime()) + " - " + "Saved as " + filename + "\n", logfile, 'a')
			if not os.path.isdir("Inputs/"+filename.split(".")[0]):
				os.mkdir("Inputs/"+filename.split(".")[0])
			if filename.split(".")[1] == "c":
				copyfile("Data/CFile.c", "Inputs/"+filename.split(".")[0] + "/"+filename)
			elif filename.split(".")[1] == "xml":
				copyfile("Data/XMLFile.xml", "Inputs/"+filename.split(".")[0] + "/"+filename)
			self.updateImportMenu()
			copyfile("Data/CoordFile.txt", "Inputs/"+filename.split(".")[0] + "/"+filename.split(".")[0]+"coord.txt")
			copyfile("Data/inputs.csv", "Inputs/"+filename.split(".")[0] + "/" +filename.split(".")[0]+"inputs.csv")

	def clearBtnCmd(self):
		'''
		Truncate the STM and all it's relations
		'''
		self.app.logThisIn(str(time.asctime()) + " - " + "Truncate STM" + "\n", logfile, 'a')
		CRUD.truncateSTM()
		self.app.pypart.stateCoordinates = {}
		self.app.pypart.transitionCoordinates = {}
		self.app.pypart.stateColor = {}
		self.app.pypart.transitionColor = {}
		self.updateStartStateMenu()
		self.app.updateSTMFiles()
		threading.Thread(target=self.app.updateCoordFile).start()
		self.app.pypart.pyWindowThreadUpdate()

class AppClass:
	def __init__(self):
		self.run = True
		self.apptime = time.time()
		self.modeOption = 1 
		self.pypart = PyWindowClass(self)
		self.tkpart = TkWindowClass(self)

	def initApp(self):
		'''
		Reads the STM from the xml file
		Initiate the Color dictionaries for states and transitions
		Update the menus
		Read the coordinates
		Update the pyWindow
		'''
		self.initSTMfromXML(xmlin)
		self.pypart.paintAllStates(color["active"])
		self.pypart.paintAllTransitions(color["inactive"])
		self.tkpart.updateStartStateMenu()
		self.readCoordinates()
		self.tkpart.updateImportMenu()
		self.pypart.pyWindowThreadUpdate()

	def toggleMode(self):
		'''
		According to the mode modify the colors of states and transitions (active/inactive) 
		Update the pyWindow
		'''
		if self.modeOption == 1:
			self.modeOption = 2
			self.tkpart.transitionMode()
			self.pypart.paintAllStates(color["inactive"])
			self.pypart.paintAllTransitions(color["active"])
			self.pypart.pyWindowThreadUpdate()
		else:
			self.modeOption = 1
			self.tkpart.stateMode()
			self.pypart.paintAllStates(color["active"])
			self.pypart.paintAllTransitions(color["inactive"])
			self.pypart.pyWindowThreadUpdate()

	def readCoordinates(self):
		'''
		Read the coordinates and add them to stateCoordinates
		'''
		auxList = []
		needUpdate = 0
		f = open(coordFile, "rt")
		for line in f:
			self.pypart.stateCoordinates[line.split(" ")[0]] = line.replace("\n", "").split(" ")[1]
			auxList.append(line.split(" ")[0])
		for st in CRUD.mySTM.statesDict:
			if st not in auxList:
				self.pypart.stateCoordinates[st] = "100x100"
				needUpdate = 1
		if needUpdate:
			self.updateCoordFile()

	def updateSTMFiles(self):
		'''
		Update the STM files to the current STM
		'''
		CRUD.updateFiles()

	def updateCoordFile(self):
		'''
		Write the current coordinates into the coordinate file
		'''
		f = open(coordFile, "wt")
		text = ""
		for st in CRUD.mySTM.statesDict:
			text += st + " " + self.pypart.stateCoordinates[st] + "\n"
		f.write(text)
		f.close()

	def logThisIn(self, text, file, mode):
		'''
		Write 'text' into 'file' by 'mode'
		'''
		f = open(file, mode)
		f.write(text)
		f.close()

	def runOnModes(self):
		self.pypart.statePickedMode()

	def initSTMfromXML(self, file):
		'''
		Initiate the STM from XML file
		'''
		CRUD.addStatesList(fromXML.getStatesList(file))
		CRUD.addTransitionsList(fromXML.getTransitionsList(file))
		self.updateSTMFiles()

	def initSTMfromC(self, file):
		'''
		Initiate the STM from C file
		'''
		CRUD.addStatesList(fromC.getStatesList(file))
		CRUD.addTransitionsList(fromC.getTransitionsList(file))
		self.updateSTMFiles()

#Main
##############################################################################################################################################
app = AppClass()
app.initApp()

while app.run == True:
	app.tkpart.tkwindow.update()
	app.runOnModes()
	app.pypart.verifyTimeEvents()
	app.pypart.verifyKeyEvents()
	app.pypart.showSystemInfo()
	pygame.display.update()

pygame.quit()