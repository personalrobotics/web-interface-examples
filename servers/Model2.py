__author__ = 'Stefanos'
import numpy
from IPython import embed
import  xml.etree.cElementTree as ET

VERBOSE = True  
#these are the same for all users
folderName = 'data/'
momdpOutFolderName = 'data/'
policyFileName = 'TableCarryingTask.policy'
statesFileName = 'obsState.dat'
startStateTheta = 100
goal1StateTheta = 0
goal2StateTheta = 180
NUMOFSTATES = 734
NUMOFROBOTACTIONS = 2
NUMOFHUMANACTIONS = 2
NUMOFUNOBSSTATES = 5
STR_ACTIONS = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE']
R = numpy.zeros([NUMOFSTATES,NUMOFROBOTACTIONS, NUMOFHUMANACTIONS, NUMOFSTATES])
T = numpy.zeros([NUMOFUNOBSSTATES, NUMOFSTATES, NUMOFROBOTACTIONS, NUMOFSTATES])
NUMOFALPHAVECTORS = 7029
A = numpy.zeros([NUMOFALPHAVECTORS, NUMOFUNOBSSTATES + 2])
startStateIndx = 640#NUMOFSTATES-2 #assume that the state before last is the starting one
goal1RestartStateIndx = 645
goal2RestartStateIndx = 648


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
  print "Loading XML policy file"
  tree = ET.parse(momdpOutFolderName + policyFileName)
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
    A[counter][0] = float(obsValue)
    A[counter][1] = float(action)
    for vv in range(0,NUMOFUNOBSSTATES):
      A[counter][2+vv] = float(values[vv])
    counter = counter + 1

class Data:

  def __init__(self, id):
    ##############The following variables are different per user########################
    self.bel_t = numpy.ones([5,1])*0.2
    #self.bel_t[0] = 1.0
    #self.bel_t[1] = 0.0
    #self.bel_t[2] = 0.0
    #self.bel_t[3] = 0.0
    #self.bel_t[4] = 0.0
    # self.bel_t[0] = 0.14
    # self.bel_t[1] = 0.5
    # self.bel_t[2] = 0.005
    # self.bel_t[3] = 0.005
    # self.bel_t[4] = 0.35
    self.currState = startStateIndx
    self.prevGoalStateTheta = -1
    self.id = id  #this is a user id

  def stateUpdateFromHumanAction(self,humanAction):
    global stateNames
    robotAction = self.getRobotActionFromPolicy(self.currState, self.bel_t)
    oldTableTheta = self.getTableThetaFromState(self.currState)
    nextState = self.getNextStateFromHumanRobotAction(self.currState,robotAction, humanAction)
    new_bel_t = self.getNewBeliefFromHumanAction(self.currState,robotAction,nextState, self.bel_t)
    self.bel_t = new_bel_t
    self.currState = nextState
    currTableTheta = self.getTableThetaFromState(self.currState)

    resultState = stateNames[self.currState]
    resultBelief = self.bel_t
    resultHAction = STR_ACTIONS[humanAction]
    resultRAction = STR_ACTIONS[robotAction]

    return (currTableTheta, resultState, resultBelief, resultHAction, resultRAction, oldTableTheta)

  def getRobotActionFromPolicy(self, ss, bel_t):
    action = -1
    maxVal = -1
    for aa in range(0, NUMOFALPHAVECTORS):
      if(A[aa][0] == ss):
        val = numpy.dot(A[aa][2:NUMOFUNOBSSTATES+2],bel_t)
        if(val > maxVal):
          maxVal = val
          action = int(A[aa][1])
    if VERBOSE:
      print "Value function is: " + str(maxVal)
      #print "Robot action is: " + self.STR_ACTIONS[action]
    print "ACTION: "
    print action
    #return action
    return 0;

  def getTableThetaFromState(self, ss):
    if(ss == startStateIndx):
       return startStateTheta
    else:
       str_state = stateNames[ss]
       theta = int(str_state.split("_")[0][1:])
      #if theta>=0 and theta<=180:
       return theta

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
def setPrevGoalStateTheta(d, id, prevGoalStateTheta):
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x  
    print ("Model2py@restartTask Error: No class instance found!")
    print("New class instance created: id={}".format(id))
  
  x.prevGoalStateTheta = prevGoalStateTheta

def resetTask(d, id): 
  print("IN:id={}".format(id))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x  
    print ("Model2py@resetTask Error: No class instance found!")
    print("New class instance created: id={}".format(id))
  x.currState = startStateIndx
  x.bel_t = numpy.ones([5,1])*0.2
  print "id={},current state is: {}\n".format(id, x.currState)


def restartTask(d, id):
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
  if x.prevGoalStateTheta == goal1StateTheta:
    x.currState = goal1RestartStateIndx
    print "id={},current state is: {}\n".format(id, x.currState)
  elif x.prevGoalStateTheta == goal2StateTheta:
    x.currState = goal2RestartStateIndx
    print "id={},current state is: {}\n".format(id, x.currState)
  else:
    print ("Model2py@restartTask invalid theta value {}".format(x.prevGoalStateTheta))
  
#the server will call this function passing the id and the button pressed
#we'll store the class instances in a dictionary with IDs as keys
#idInitiated helper function checks if id is in the dictionary
def getMove(d,id,humanAction, prior):
  print("IN:id={},action={}".format(id,humanAction))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x
    print("New class instance created: id={}".format(id))
  currTableTheta, resultState, resultBelief, resultHAction, resultRAction, oldTableTheta = \
    x.stateUpdateFromHumanAction(humanAction)
  print("OUT:theta={}".format(currTableTheta))

  if(prior): #Condition where we want to collect priors 
    if(resultHAction=='ROTATE_COUNTER_CLOCKWISE'):
      message =  'Let\'s rotate the table clockwise, by pressing the button on your LEFT!'
    elif(resultHAction=='ROTATE_CLOCKWISE'):
      message = 'You turned the table CLOCKWISE. HERB did the same action. <br> The table turned 20 degrees.'
    else:
      message = 'Model2py@getMove error: unknown string!' 
  else: #Condition where we don't collect priors 
    if(resultHAction=='ROTATE_CLOCKWISE')and(resultRAction=='ROTATE_CLOCKWISE'):
       message = 'You turned the table CLOCKWISE. HERB did the same action. <br> The table turned 20 degrees.'
    elif(resultHAction == 'ROTATE_COUNTER_CLOCKWISE')and(resultRAction == 'ROTATE_COUNTER_CLOCKWISE'):
       message = 'You turned the table COUNTER-CLOCKWISE. HERB did the same action. <br> The table turned 20 degrees.'
    elif(resultHAction == 'ROTATE_CLOCKWISE')and(resultRAction == 'ROTATE_COUNTER_CLOCKWISE'):
       message = 'You tried to turn the table CLOCKWISE. HERB tried to turn the table COUNTER-CLOCKWISE. <br> The table did not turn.'
    elif(resultHAction == 'ROTATE_COUNTER_CLOCKWISE')and(resultRAction == 'ROTATE_CLOCKWISE'):
       message = 'You tried to turn the table COUNTER-CLOCKWISE. HERB tried to turn the table CLOCKWISE. <br> The table did not turn.'
    else:
        message = 'Model2py@getMove error: unknown string!' 
        
  #for debugging
  instructionString ='''The current angle is: {}<br> The current state is: {}<br>  The current belief is: {}<br> You did action: {}<br> Robot did action: {}<br>
    Old angle is {}<br> '''.format(currTableTheta, resultState, resultBelief, resultHAction, resultRAction, oldTableTheta)
  message = message + instructionString
  #print "MESSAGE: " + message
  return (currTableTheta, oldTableTheta, resultBelief, resultHAction, message)


