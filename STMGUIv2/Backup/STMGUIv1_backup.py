from Tkinter import *
import CRUD
import pygame
import threading
import os
import math
import time
import logging
import sched
import csv
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
stateRectWidth = 60
infoRectWidth = 100
infoRectHeight = 20
statePickTime = 0.01
coordFile = "CoordFile.txt"
logfile = "Logs/logfile.log"
runlogfile = "Logs/runLog.log"
color = {"active":(86, 224, 67), "inactive":(150,150,150), "background":(220,220,220), "info":(150,220,50), "pickedup": (0, 150, 250), "normal": (255, 255, 255), "fontcolor": (0, 0, 0), "pink": (224, 67, 188), "running": (220, 40, 50)}
key = {"enter": 28, "backspace": 14, "delete": 83}

#Variables
##############################################################################################################################################
timeStep = 0.2
modeOption = 1
collision = 1
info = 1
run = True
appTime = 0
animationRun = 0
currentStateIndex = 0
currAnimationState = ""
animationSteps = 0
animationStartTime = 0
animationLog = ""
stateNameToBeSpawned = ""
mouseLeftPressed = 0
lastMousePressedTime = time.time()
inputUpdateSchedule = sched.scheduler(time.time, time.sleep)
stateCoordinates = {} #statename: XposxYpos (left corner)
transitionCoordinates = {} #src|dest: XposxYpos (circle's center)
stateColor = {}#statename: (R, G, B)
transitionColor = {}#src|dest: (R, G, B)
animationStatesPath = []


#Functions
##############################################################################################################################################
def stateMode():
	global modeOption
	modeOption = 1
	emptyEntries()
	label1.config(text="State name: ", state=NORMAL)
	label2.config(text="", state=DISABLED)
	label3.config(text="", state=DISABLED)
	label4.config(text="", state=DISABLED)
	entry1.config(state=NORMAL)
	entry2.config(state=DISABLED)
	entry3.config(state=DISABLED)
	entry4.config(state=DISABLED)
	pyWindowThreadUpdate()
	
def transitionMode():
	global modeOption
	modeOption = 2
	emptyEntries()
	label1.config(text="Transition name: ", state=NORMAL)
	label2.config(text="Condition: ", state=NORMAL)
	label3.config(text="Source name: ", state=NORMAL)
	label4.config(text="Destination name: ", state=NORMAL)
	entry1.config(state=NORMAL)
	entry2.config(state=NORMAL)
	entry3.config(state=NORMAL)
	entry4.config(state=NORMAL)
	pyWindowThreadUpdate()
	
def toggleMode():
	if modeOption == 1:
		transitionMode()
		paintAllTransitions(color["active"])
		paintAllStates(color["inactive"])
		pyWindowThreadUpdate()
	elif modeOption == 2:
		stateMode()
		paintAllTransitions(color["inactive"])
		paintAllStates(color["active"])
		pyWindowThreadUpdate()
		
def emptyEntries():
	entry1.delete(0, END)
	entry1.insert(0, "")
	entry2.delete(0, END)
	entry2.insert(0, "")
	entry3.delete(0, END)
	entry3.insert(0, "")
	entry4.delete(0, END)
	entry4.insert(0, "")

def addBtnCmd():
	global stateNameToBeSpawned
	if modeOption == 1:
		sname = entry1.get()
		result = CRUD.addState(sname)
		if result == "Success":
			logThisIn("State was added (name: " + sname + ")\n", logfile, 'a')
			stateNameToBeSpawned = sname
			stateColor[stateNameToBeSpawned] = color["pickedup"]
			emptyEntries()
			updateStartStateMenu()
			stateCoordinates[sname] = "100x100"
			threading.Thread(target=updateSTM).start()
			threading.Thread(target=updateCoordFile).start()
		else:
			popupmsg(result)
		
	elif modeOption == 2:
		result = CRUD.addTransition(entry1.get(), entry2.get(), entry3.get(), entry4.get())
		if result == "Success":
			logThisIn("Transition was added (name: " + entry1.get() + ", condition: " + entry2.get() + ", source: " + entry3.get() + ", destination: " + entry4.get() + ")\n", logfile, 'a')
			threading.Thread(target=updateSTM).start()
			transitionColor[entry3.get() + "|" + entry4.get()] = color["active"]
			emptyEntries()
			pyWindowThreadUpdate()
		else:
			popupmsg(result)
		
def removeBtnCmd():
	if modeOption == 1:
		sname = entry1.get()
		deletedTransitions = CRUD.getTransitionsIncluding(sname)
		result = CRUD.removeState(sname)
		if result == "Success":
			logThisIn("State was deleted (name: " + sname + ")\n", logfile, 'a')
			del stateCoordinates[sname]
			for dt in deletedTransitions:
				del transitionCoordinates[dt]
			threading.Thread(target=updateCoordFile).start()
			threading.Thread(target=updateSTM).start()
			emptyEntries()
			pyWindowThreadUpdate()
			updateStartStateMenu()
		else:
			popupmsg(result)
	elif modeOption == 2:
		src = entry3.get()
		dest = entry4.get()
		result = CRUD.removeTransition(src, dest)
		if result == "Success":
			logThisIn("Transition was deleted (source: " + src + ", destination: " + dest + ")\n", logfile, 'a')
			threading.Thread(target=updateSTM).start()
			del transitionCoordinates[src + "|" + dest]
			emptyEntries()
			pyWindowThreadUpdate()
		else:
			popupmsg(result)

def updateBtnCmd():
	if modeOption == 1:
		sname = entry1.get()
		result = CRUD.updateState(sname)
		if result == "Success":
			logThisIn("State was updated (name: " + sname + ")\n", logfile, 'a')
			threading.Thread(target=updateSTM).start()
			emptyEntries()
			pyWindowThreadUpdate()
		else:
			popupmsg(result)
	elif modeOption == 2:
		result = CRUD.updateTransition(entry1.get(), entry2.get(), entry3.get(), entry4.get())
		if result == "Success":
			logThisIn("Transition was updated (name: " + entry1.get() + ", condition: " + entry2.get() + ", source: " + entry3.get() + ", destination: " + entry4.get() + ")\n", logfile, 'a')
			threading.Thread(target=updateSTM).start()
			emptyEntries()
			pyWindowThreadUpdate()
		else:
			popupmsg(result)

def findBtnCmd():
	if modeOption == 1:
		result = CRUD.findState(entry1.get())
		popupmsg(result)
	elif modeOption == 2:
		result = CRUD.findTransition(entry3.get(), entry4.get())
		popupmsg(result)

def updateSTM():
	CRUD.updateFiles()
	#print CRUD.showSTM()

def updateCoordFile():
	f = open(coordFile, "wt")
	text = ""
	for co in stateCoordinates:
		text += stateCoordinates[co] + ","
	text = text[:-1]
	f.write(text)
	f.close()
	
def popupmsg(msg):
	popup = Toplevel()
	popup.title("!")
	popup.geometry(popUpMsgSize + "+" + str(tkWindowPosX + popUpMsgPosX) + "+" + str(tkWindowPosY + popUpMsgPosY))
	message = Message(popup, text=msg)
	message.pack()
	button = Button(popup, text="Ok", command=popup.destroy)
	button.pack()

def initPyWindow():
	global pywindow
	threading.Thread(target=updateSTM).start()
	readCoordinates()
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (pyWindowPosX,pyWindowPosY)
	pygame.init()
	pywindow = pygame.display.set_mode(pyWindowSize)
	pywindow.fill(color["background"])
	pygame.display.set_caption("STM configuration tool")
	pygame.mouse.set_cursor(*pygame.cursors.tri_left)
	paintAllStates(color["active"])
	paintAllTransitions(color["inactive"])
	pyWindowThreadUpdate()
	updateStartStateMenu()

def initTkWindow():
	global omStateVar, tkwindow
	global label1, label2, label3, label4, label5, label6
	global entry1, entry2, entry3, entry4, entry5
	global addBtn, removeBtn, updateBtn, findBtn, toggleCollisionBtn, toggleInfoBtn, runBtn
	global statesOptionMenu
	omStateVar = StringVar(tkwindow)
	omStateVar.set("-select-")
	omStateVar.trace("w", changeStartState)
	tkwindow.title("STM GUI")
	tkwindow.configure(background="grey")
	tkwindow.protocol("WM_DELETE_WINDOW", disable_event)
	tkwindow.geometry(tkWindowSize + "+" + str(tkWindowPosX) + "+" + str(tkWindowPosY))
	label1 = Label(tkwindow, text="State name:", bg="grey", fg="black", state=NORMAL)
	label1.grid(row=1, column=0, columnspan=2, sticky=N+S+W)
	label2 = Label(tkwindow, text="", bg="grey", fg="black", state=DISABLED)
	label2.grid(row=3, column=0, columnspan=2, sticky=N+S+W)
	label3 = Label(tkwindow, text="", bg="grey", fg="black", state=DISABLED)
	label3.grid(row=5, column=0, columnspan=2, sticky=N+S+W)
	label4 = Label(tkwindow, text="", bg="grey", fg="black", state=DISABLED)
	label4.grid(row=7, column=0, columnspan=2, sticky=N+S+W)
	label5 = Label(tkwindow, text="Starting state:", bg="grey", fg="black", state=NORMAL)
	label5.grid(row=13, column=0, sticky=N+S+W)
	label6 = Label(tkwindow, text="Steps:", bg="grey", fg="black", state=NORMAL)
	label6.grid(row=14, column=0, sticky=N+S+W)
	entry1 = Entry(tkwindow, state=NORMAL)
	entry1.grid(row=2, column=0, columnspan=2, sticky=N+E+S+W)
	entry2 = Entry(tkwindow, state=DISABLED)
	entry2.grid(row=4, column=0, columnspan=2, sticky=N+E+S+W)
	entry3 = Entry(tkwindow, state=DISABLED)
	entry3.grid(row=6, column=0, columnspan=2, sticky=N+E+S+W)
	entry4 = Entry(tkwindow, state=DISABLED)
	entry4.grid(row=8, column=0, columnspan=2, sticky=N+E+S+W)
	entry5 = Entry(tkwindow, state=NORMAL)
	entry5.grid(row=14, column=1, sticky=N+E+S+W)
	addBtn = Button(tkwindow, text="Add", bg="pink", command=addBtnCmd)
	addBtn.grid(row=9, column=0, sticky=N+E+S+W)
	removeBtn = Button(tkwindow, text="Remove", bg="pink", command=removeBtnCmd)
	removeBtn.grid(row=9, column=1, sticky=N+E+S+W)
	updateBtn = Button(tkwindow, text="Update", bg="pink", command=updateBtnCmd)
	updateBtn.grid(row=10, column=0, sticky=N+E+S+W)
	findBtn = Button(tkwindow, text="Find", bg="pink", command=findBtnCmd)
	findBtn.grid(row=10, column=1, sticky=N+E+S+W)
	toggleCollisionBtn = Button(tkwindow, text="Toggle Collision", bg="pink", command=toggleCollision)
	toggleCollisionBtn.grid(row=11, column=0, columnspan=2, sticky=N+E+S+W)
	toggleInfoBtn = Button(tkwindow, text="Toggle Info", bg="pink", command=toggleInfo)
	toggleInfoBtn.grid(row=12, column=0, columnspan=2, sticky=N+E+W)
	statesOptionMenu = OptionMenu(tkwindow, omStateVar, "")
	statesOptionMenu.grid(row=13, column=1, sticky=N+E+S+W)
	runBtn = Button(tkwindow, text="Start", bg="green", command=toggleRun)
	runBtn.grid(row=15, column=0, sticky=N+S+E+W)

def spawnStateRect(x, y, name):
	pygame.draw.rect(pywindow, stateColor[name], (x,y,stateRectWidth,stateRectHeight))
	font = pygame.font.SysFont("arial", 15, True)
	text = font.render(name, True, color["fontcolor"])
	pywindow.blit(text, (x + (stateRectWidth/2 - text.get_width()/2), y + (stateRectHeight/2 - text.get_height()/2)))

def spawnInfoRect(x, y, name, color):
	pygame.draw.rect(pywindow, color, (x,y,infoRectWidth,infoRectHeight))
	font = pygame.font.SysFont("arial", 15)
	text = font.render(name, True, (0,0,0))
	pywindow.blit(text, (x + (infoRectWidth/2 - text.get_width()/2), y + (infoRectHeight/2 - text.get_height()/2)))

def spawnTransitionLine(p1, p2, name):
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
		pygame.draw.line(pywindow, transitionColor[name], (srcx, srcy), (destx,desty), 3)
		pygame.draw.line(pywindow, transitionColor[name], (leftX, leftY), (ix, iy), 5)
		pygame.draw.line(pywindow, transitionColor[name], (rightX, rightY), (ix, iy), 5)
		transitionCoordinates[name] = str(int((ix + leftX + rightX)/3)) + "x" + str(int((iy + leftY + rightY)/3))

def getCenterOfShape(x, y):
	cx = x + stateRectWidth/2
	cy = y + stateRectHeight/2
	return cx, cy

def isEmptySpace(x, y):
	if collision == -1:
		return True
	cond4 = 0
	if x + stateRectWidth >= pyWindowSize[0]:
		return False
	if y + stateRectHeight >= pyWindowSize[1]:
		return False
	okColors = [color["background"], color["inactive"], color["pickedup"], color["running"]]
	if pywindow.get_at((x, y))[:3] in okColors:
		cond4 += 1
	if pywindow.get_at((x+stateRectWidth, y))[:3] in okColors:
		cond4+= 1
	if pywindow.get_at((x+stateRectWidth, y+stateRectHeight))[:3] in okColors:
		cond4+= 1
	if pywindow.get_at((x, y+stateRectHeight))[:3] in okColors:
		cond4+= 1
	if cond4 == 4:
		return True
	else:
		return False

def toggleCollision():
	global collision
	collision = -collision

def toggleInfo():
	global info
	info = -info
	pyWindowThreadUpdate()
	
def disable_event():
	global run 
	run = False

def readCoordinates():
	f = open(coordFile, "rt")
	coordinates = f.readline().split(",")
	for st, co in zip(CRUD.mySTM.statesDict, coordinates):
		stateCoordinates[CRUD.mySTM.statesDict[st].name] = co

def getTransitionNameAtPos(x, y):
	for tc in transitionCoordinates:
		tx, ty = transitionCoordinates[tc].split("x")
		if math.sqrt((x - int(tx))**2 + (y - int(ty))**2) <= 30:
			return tc
	return None

def getStateNameAtPos(x, y):
	for sc in stateCoordinates:
		sx, sy = stateCoordinates[sc].split("x")
		if x >= int(sx) and x <= int(sx)+stateRectWidth and y >= int(sy) and y <= int(sy)+stateRectHeight:
			return sc
	return ""

def statePickedMode():
	global stateNameToBeSpawned
	if stateNameToBeSpawned != "":
		if isEmptySpace(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
			stateCoordinates[stateNameToBeSpawned] = str(pygame.mouse.get_pos()[0]+1) + "x" + str(pygame.mouse.get_pos()[1]+1)
			pyWindowThreadUpdate()	

def stateRelease():
	global stateNameToBeSpawned
	threading.Thread(target=updateCoordFile).start()
	stateColor[stateNameToBeSpawned] = color["active"]
	stateNameToBeSpawned = ""
	pygame.mouse.set_cursor(*pygame.cursors.tri_left)
	pyWindowThreadUpdate()
				
def statePick():
	global stateNameToBeSpawned
	if animationRun == 0:
		if time.time() - lastMousePressedTime >= statePickTime and mouseLeftPressed == 1 and stateNameToBeSpawned == "" and getStateNameAtPos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) != "":
			stateNameToBeSpawned = getStateNameAtPos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
			stateColor[stateNameToBeSpawned] = color["pickedup"]
			pygame.mouse.set_cursor(*pygame.cursors.diamond)

def selectState():
	mx, my = pygame.mouse.get_pos()
	whatIsClicked = getStateNameAtPos(mx, my)
	if whatIsClicked != stateNameToBeSpawned:
		if whatIsClicked != None:
			if modeOption == 1:
				entry1.delete(0, END)
				entry1.insert(0, whatIsClicked)
			elif modeOption == 2:
				entry3.delete(0, END)
				entry3.insert(0, entry4.get())
				entry4.delete(0, END)
				entry4.insert(0, whatIsClicked)

def selectTransition():
	mx, my = pygame.mouse.get_pos()
	whatIsClicked = getTransitionNameAtPos(mx, my)
	if whatIsClicked != None:
		tname = CRUD.mySTM.transitionsDict[whatIsClicked].name
		tcond = CRUD.mySTM.transitionsDict[whatIsClicked].cond
		tsrc = CRUD.mySTM.transitionsDict[whatIsClicked].src.name
		tdest = CRUD.mySTM.transitionsDict[whatIsClicked].dest.name
		entry1.delete(0, END)
		entry1.insert(0, tname)
		entry2.delete(0, END)
		entry2.insert(0, tcond)
		entry3.delete(0, END)
		entry3.insert(0, tsrc)
		entry4.delete(0, END)
		entry4.insert(0, tdest)

def updatePyWindow():
	pywindow.fill(color["background"])
	for tr in CRUD.mySTM.transitionsDict:
		srcx, srcy = stateCoordinates[CRUD.mySTM.transitionsDict[tr].src.name].split("x")
		destx, desty = stateCoordinates[CRUD.mySTM.transitionsDict[tr].dest.name].split("x")
		spawnTransitionLine(getCenterOfShape(int(srcx), int(srcy)), getCenterOfShape(int(destx), int(desty)), tr)
	for sc in stateCoordinates:
		x, y = stateCoordinates[sc].split("x")
		spawnStateRect(int(x), int(y), str(sc))

def verifyKeyEvents(events):
	global lastMousePressedTime
	global mouseLeftPressed
	global run
	for event in events:
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.scancode == key["enter"]:
				addBtnCmd()
			elif event.scancode == key["delete"] or event.scancode == key["backspace"]:
				removeBtnCmd()
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			if modeOption == 1:
				mouseLeftPressed = 1
				lastMousePressedTime = time.time()
			elif modeOption == 2:
				selectTransition()
			selectState()
		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			if modeOption == 1:
				mouseLeftPressed = 0
				stateRelease()
		if event.type == pygame.MOUSEBUTTONDOWN and event.button in [4, 5]:
			toggleMode()
		if mouseLeftPressed == 1:
			statePick()

def verifyTimeEvents():
	global apptime
	if time.time() - apptime >= timeStep:
		apptime = time.time()
		animationTryStep()
		
def runOnModes(events):
	statePickedMode()

def showCursorCoordinates():
	spawnInfoRect(0, 0, str(pygame.mouse.get_pos()[0]) + ", " + str(pygame.mouse.get_pos()[1]), color["info"])

def showMode():
	if modeOption == 1:
		spawnInfoRect(infoRectWidth+2, 0, "State Mode", color["info"])
	elif modeOption == 2:
		spawnInfoRect(infoRectWidth+2, 0, "Transition Mode", color["info"])

def showCollisionInfo():
	if collision == 1:
		spawnInfoRect(2*infoRectWidth+3, 0, "Collision: On", color["info"])
	else:
		spawnInfoRect(2*infoRectWidth+3, 0, "Collision: Off", color["info"])

def showSystemInfo():
	if info == 1:
		showCursorCoordinates()
		showMode()
		showCollisionInfo()

def logThis(text):
	logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename="logfile.log")
	logging.info(text)

def logThisIn(text, file, mode):
	f = open(file, mode)
	f.write(text)
	f.close()

def changeStartState(*args):
	pass

def updateStartStateMenu():
	menu = statesOptionMenu["menu"]
	menu.delete(0, END)
	for st in CRUD.mySTM.statesDict:
		menu.add_command(label=st, command=lambda value=st: omStateVar.set(value))
	tkwindow.update()

def paintAllTransitions(color):
	global transitionColor
	transitionColor = {x: color for x in CRUD.mySTM.transitionsDict}

def paintAllStates(color):
	global stateColor
	stateColor = {x: color for x in CRUD.mySTM.statesDict}

def toggleRun():
	if animationRun == 0:
		if entry5.get() != "":
		 	startRun()
	else:
		stopRun()

def startRun():
	global animationRun
	global animationStartTime
	global currAnimationState
	global animationSteps
	global animationLog
	animationStartTime = time.time()
 	runBtn.config(text="Stop", bg="red")
	animationRun = 1
 	currAnimationState = str(omStateVar.get())
 	stateColor[currAnimationState] = color["running"]
 	animationSteps = int(entry5.get())
 	updateInputSchedule()
 	animationLog += "Run - " + str(time.asctime()) + "\n" + str(round(time.time() - animationStartTime,4)) + " - In state " + currAnimationState
 	pyWindowThreadUpdate()
	runScheduleThread = threading.Thread(target=inputUpdateSchedule.run)
	runScheduleThread.start()

def stopRun():
	global animationLog
	global animationRun
	runBtn.config(text="Start", bg="green")
	animationRun = 0
	if modeOption == 1:
		paintAllStates(color["active"])
		paintAllTransitions(color["inactive"])
	elif modeOption == 2:
		paintAllStates(color["inactive"])
		paintAllTransitions(color["active"])
	animationLog += "\nEnded after " + str(round(time.time() - animationStartTime,4)) + " seconds"
	logThisIn(animationLog, runlogfile, 'w')
	animationLog = ""
	pyWindowThreadUpdate()
	
def updateInputSchedule():
	global inputUpdateSchedule
	file = open('inputs.csv', 'r')
	reader = csv.reader(file)

	header = next(reader)
	data = [row for row in reader]
	for i in range(1, 12):
		for datarow in data:
			inputUpdateSchedule.enter(float(header[i]), 1, CRUD.updateInput, argument=(datarow[0], datarow[i]))
	file.close()

def animationTryStep():
	global animationSteps
	global animationLog
	global currAnimationState
	nextstate = ""
	if animationRun == 1:
		if animationSteps > 0:
			nextstate = CRUD.getNextStateFrom(currAnimationState)
			animationSteps -= 1
			if nextstate != None:
				animationLog += "\n" + str(round(time.time() - animationStartTime,4)) + " - In state " + nextstate
				transitionColor[currAnimationState + "|" + nextstate] = color["running"]
				stateColor[currAnimationState] = color["active"]
				currAnimationState = nextstate
				stateColor[currAnimationState] = color["running"]
				pyWindowThreadUpdate()
		else:
			stopRun()

def pyWindowThreadUpdate():
	pyUpdateThread = threading.Thread(target=updatePyWindow)
	pyUpdateThread.start()
	pyUpdateThread.join()

#TKWindow
##############################################################################################################################################
tkwindow = Tk()
initTkWindow()

#PYWindow
##############################################################################################################################################
initPyWindow()

#Main
##############################################################################################################################################
apptime = time.time()

while run:
	tkwindow.update()
	events = pygame.event.get()
	runOnModes(events)
	verifyTimeEvents()
	verifyKeyEvents(events)
	showSystemInfo()
	pygame.display.update()

pygame.quit()
