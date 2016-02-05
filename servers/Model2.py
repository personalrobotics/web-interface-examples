__author__ = 'Stefanos'
import numpy
from IPython import embed
import  xml.etree.cElementTree as ET

VERBOSE = True  
#these are the same for all users
folderName = 'data/'
momdpOutFolderName = 'data/'
policyFileNameLeft = 'CorridorHumanPrefLeft.policy'
policyFileNameRight = 'CorridorHumanPrefRight.policy'
statesFileName = 'obsState.dat'
startStateHumanPos = 0
startStateRobotPos = 0
goal1StateHumanPos = 1 #goal 1(optimal): human left, robot right
goal1StateRobotPos = 2
goal2StateHumanPos = 2 #goal 2(suboptimal): human right, robot left
goal2StateRobotPos = 1
NUMOFSTATES = 340
NUMOFROBOTACTIONS = 2
NUMOFHUMANACTIONS = 2
NUMOFUNOBSSTATES = 5
STR_POSITIONS = [ 'START','LEFT', 'RIGHT']
STR_ACTIONS = ['MOVE_LEFT', 'MOVE_RIGHT']
R = numpy.zeros([NUMOFSTATES,NUMOFROBOTACTIONS, NUMOFHUMANACTIONS, NUMOFSTATES])
T = numpy.zeros([NUMOFUNOBSSTATES, NUMOFSTATES, NUMOFROBOTACTIONS, NUMOFSTATES])
NUMOFALPHAVECTORS = 469
#self.NUMOFALPHAVECTORS = 42
A_LEFT = numpy.zeros([NUMOFALPHAVECTORS, NUMOFUNOBSSTATES + 2])
A_RIGHT = numpy.zeros([NUMOFALPHAVECTORS, NUMOFUNOBSSTATES + 2])
#assume that the state before last is the starting state. The last one is the absorbing state
startStateIndx = 256#self.NUMOFSTATES-2
print "Loading state names from file"
stateNamesFile = open(folderName+statesFileName, 'r')

goal1RestartStateIndx = 337 # robot_pos = 1, human_pos = 0, mobs = MRIGHT, mprev = MLEFT
goal2RestartStateIndx = 338


#uninitiated globals for globalsInit()
stateNames = None

def globalsInit():
  global stateNames, R, T, A
  print "Loading state names from file"
  with open(folderName+statesFileName, 'r') as stateNamesFile:
    stateNames = numpy.asarray([ line.split(' ') for line in stateNamesFile])[0]

  print "Loading reachability matrix from file"
  for ra in range(0,NUMOFROBOTACTIONS):
    for ha in range(0,NUMOFHUMANACTIONS):
      with open(folderName + 'R' + str(ra+1)+str(ha+1)+'.dat', 'r') as reachFile:
        reachMtx = numpy.asarray([map(float, line.split('\t')) for line in reachFile])
        for ss in range(0, NUMOFSTATES):
          for nss in range(0,NUMOFSTATES):
            R[ss][ra][ha][nss] = reachMtx[ss][nss]
  print "Loading Transition Matrix from file"
  for yIndx in range(0,NUMOFUNOBSSTATES):
      for ra in range(0, NUMOFROBOTACTIONS):
        with open(folderName + 'T' + str(yIndx+1)+str(ra+1)+'.dat', 'r') as transFile:
          transMtx = numpy.asarray([map(float, line.split('\t')) for line in transFile])
          for ss in range(0, NUMOFSTATES):
            for nss in range(0, NUMOFSTATES):
              T[yIndx][ss][ra][nss] = transMtx[ss][nss]
  print "Loading XML policy file left"
  tree = ET.parse(momdpOutFolderName + policyFileNameLeft)
  root = tree.getroot()
  numVectors = len(root.getchildren()[0].getchildren())
  print numVectors
  print root.iter('Vector')
  counter = 0
  for vector in root.iter('Vector'):
    obsValue  = vector.get('obsValue')
    action = vector.get('action')
    values = vector.text.split(' ')
    # vector format: obsValue, action, values
    A_LEFT[counter][0] = float(obsValue)
    A_LEFT[counter][1] = float(action)
    for vv in range(0,NUMOFUNOBSSTATES):
      A_LEFT[counter][2+vv] = float(values[vv])
    counter = counter + 1

  tree = ET.parse(momdpOutFolderName + policyFileNameRight)
  root = tree.getroot()
  numVectors = len(root.getchildren()[0].getchildren())
  print numVectors
  print root.iter('Vector')
  counter = 0
  for vector in root.iter('Vector'):
    obsValue  = vector.get('obsValue')
    action = vector.get('action')
    values = vector.text.split(' ')

    # vector format: obsValue, action, values
    A_RIGHT[counter][0] = float(obsValue)
    A_RIGHT[counter][1] = float(action)
    for vv in range(0,NUMOFUNOBSSTATES):
      A_RIGHT[counter][2+vv] = float(values[vv])
    counter = counter + 1

class Data:

  def __init__(self, id):
    ##############The following variables are different per user########################
    self.bel_t = numpy.ones([5,1])*0.2
    self.currState = startStateIndx
    self.prevGoalHumanPos = -1
    self.prevGoalRobotPos = -1
    self.id = id  #this is a user id

  def stateUpdateFromHumanAction(self,humanAction):
    global stateNames
    robotAction = self.getRobotActionFromPolicy(self.currState, self.bel_t)
    oldHumanPos, oldRobotPos = self.getHumanRobotPosFromState(self.currState)
    nextState = self.getNextStateFromHumanRobotAction(self.currState,robotAction, humanAction)
    print "DEBUGGING: next state is ", str(nextState)
    new_bel_t = self.getNewBeliefFromHumanAction(self.currState,robotAction,nextState, self.bel_t)
    self.bel_t = new_bel_t
    self.currState = nextState
    currHumanPos, currRobotPos = self.getHumanRobotPosFromState(self.currState)

    resultState = stateNames[self.currState]
    resultBelief = self.bel_t
    resultHAction = STR_ACTIONS[humanAction]
    resultRAction = STR_ACTIONS[robotAction]

    return (currHumanPos, currRobotPos, resultState, resultBelief, resultHAction, resultRAction, oldHumanPos, oldRobotPos)

  def getRobotActionFromPolicy(self, ss, bel_t, human_pref):
    action = -1
    maxVal = -1
    for aa in range(0, NUMOFALPHAVECTORS):
      if human_pref == "move_right":
        if(A_RIGHT[aa][0] == ss):
          val = numpy.dot(A_RIGHT[aa][2:NUMOFUNOBSSTATES+2],bel_t)
          if(val > maxVal):
            maxVal = val
            action = int(A_RIGHT[aa][1])
      if human_pref == "move_left":
        if(A_LEFT[aa][0] == ss):
          val = numpy.dot(A_RIGHT[aa][2:NUMOFUNOBSSTATES+2],bel_t)
          if(val > maxVal):
            maxVal = val
            action = int(A_RIGHT[aa][1])
    if VERBOSE:
      print "Value function is: " + str(maxVal)
      #print "Robot action is: " + self.STR_ACTIONS[action]
    return action

  def getHumanRobotPosFromState(self, ss):
      str_state = stateNames[ss]
      print "str_state: ", str_state

      if ss == startStateIndx:
          return startStateHumanPos, startStateRobotPos

      humanPos = int(str_state.split("H")[1][0])
      robotPos = int(str_state.split("R")[1][0])
      if humanPos>=1 and humanPos<=2: #not start state
        return humanPos, robotPos
      else:
        print "Error! Unknown human/robot pos!"
        return startStateHumanPos, startStateRobotPos

  def getNextStateFromHumanRobotAction(self, ss, ra, ha):
    nextStateMtx = R[ss][ra][ha][:]
    return nextStateMtx.argmax()

  def getNewBeliefFromHumanAction(self, ss, ra, nss, bel_t):
    bel_tp1 = numpy.zeros([NUMOFUNOBSSTATES,1])
    SumBeliefs = 0
    for yy in range(0, NUMOFUNOBSSTATES):
      bel_tp1[yy] = T[yy][ss][ra][nss]*bel_t[yy]
      SumBeliefs = SumBeliefs + bel_tp1[yy]
    bel_tp1 = bel_tp1 / SumBeliefs
    return bel_tp1

def idInitiated(id,d):
  if id in d:
    return True
  else:
    return False

#the server will call this function passing the id and the button pressed.
#it will then reset the observable state for that class
def setPrevGoalHumanRobotPos(d, id, prevGoalHumanPos, prevGoalRobotPos):
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x  
    print ("Model2py@restartTask Error: No class instance found!")
    print("New class instance created: id={}".format(id))
  
  x.prevGoalHumanPos = prevGoalHumanPos
  x.prevGoalRobotPos = prevGoalRobotPos

def restartTask(d, id):
  print "DEBUGGING: restarting task!!"
  print("IN:id={}".format(id))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x  
    print ("Model2py@restartTask Error: No class instance found!")
    print("New class instance created: id={}".format(id))
  #logic that says what the next state will be based on the previous goal
  if (x.prevGoalHumanPos == goal1StateHumanPos) and (x.prevGoalRobotPos == goal1StateRobotPos):
    x.currState = goal1RestartStateIndx
    print "id={},current state is: {}\n".format(id, x.currState)
  elif (x.prevGoalHumanPos == goal2StateHumanPos) and (x.prevGoalRobotPos == goal2StateRobotPos):
    x.currState = goal2RestartStateIndx
    print "id={},current state is: {}\n".format(id, x.currState)
  else:
    print ("Model2py@restartTask invalid human / robot pos value {}{}".format(x.prevGoalHumanPos,x.prevGoalRobotPos))
  
#the server will call this function passing the id and the button pressed
#we'll store the class instances in a dictionary with IDs as keys
#idInitiated helper function checks if id is in the dictionary
def getMove(d,id,humanAction):
  print("IN:id={},action={}".format(id,humanAction))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x
    print("New class instance created: id={}".format(id))
  currHumanPos, currRobotPos, resultState, resultBelief, resultHAction, resultRAction, oldHumanPos, oldRobotPos = \
    x.stateUpdateFromHumanAction(humanAction)
  print("OUT:humanPos={}{}".format(currHumanPos, currRobotPos))
  if(resultHAction=='MOVE_LEFT')and(resultRAction=='MOVE_LEFT'):
     message = 'You moved LEFT. HERB did the same action.'
  elif(resultHAction == 'MOVE_RIGHT')and(resultRAction == 'MOVE_RIGHT'):
     message = 'You moved RIGHT. HERB did the same action.'
  elif(resultHAction == 'MOVE_RIGHT')and(resultRAction == 'MOVE_LEFT'):
     message = 'You moved RIGHT. HERB moved LEFT.'
  elif(resultHAction == 'MOVE_LEFT')and(resultRAction == 'MOVE_RIGHT'):
     message = 'You moved LEFT. HERB moved RIGHT.'
  else:
      message = 'Model2py@getMove error: unknown string!' 
  #for debugging
  instructionString ='''The current human/robot position is: {},{}<br> The current state is: {}<br>  The current belief is: {}<br> You did action: {}<br> Robot did action: {}<br>
   Old human/robot position is {}{}<br> '''.format(currHumanPos, currRobotPos, resultState, resultBelief, resultHAction, resultRAction, oldHumanPos, oldRobotPos)
  message = message + instructionString
  return (currHumanPos, currRobotPos, oldHumanPos, oldRobotPos, resultBelief, message)
