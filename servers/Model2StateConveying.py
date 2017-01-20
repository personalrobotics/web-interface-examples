__author__ = 'Stefanos'
import numpy
from IPython import embed
import  xml.etree.cElementTree as ET

VERBOSE = True


folderName = 'dataStateConveying/stateConveying/'
momdpOutFolderName = 'dataStateConveying/stateConveying/'
#folderName = '../../MatlabOutputFiles/'

#momdpOutFolderName = '../../output/'
policyFileName = 'mentalmodel20-15np2.policy'
statesFileName = 'obsState.dat'

startStateTheta = 100
goal1StateTheta = 0
goal2StateTheta = 180
NUMOFSTATES = 2360
NUMOFROBOTACTIONS = 3
NUMOFHUMANACTIONS = 2
NUMOFUNOBSSTATES = 5
NUMOFALLUNOBSSTATES = NUMOFUNOBSSTATES
STR_ACTIONS = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE','CONVEY_STATE']

R = numpy.zeros([NUMOFSTATES,NUMOFROBOTACTIONS, NUMOFHUMANACTIONS, NUMOFSTATES])
T = numpy.zeros([NUMOFUNOBSSTATES, NUMOFSTATES, NUMOFROBOTACTIONS, NUMOFSTATES])   
Tz = numpy.zeros([NUMOFUNOBSSTATES, NUMOFSTATES, NUMOFUNOBSSTATES])   

NUMOFALPHAVECTORS = 3375
A = numpy.zeros([NUMOFALPHAVECTORS, NUMOFUNOBSSTATES + 2])
#assume that the state before last is the starting state. The last one is the absorbing state
startStateIndx = 2160
print "Loading state names from file"
goal1RestartStateIndx = 2167
goal2RestartStateIndx = 2170
goal1StateTheta = 0
goal2StateTheta = 180

stateNames = None

def globalsInit():
  
  global stateNames, R, T, A 
  print "loading state names from file"

  with open(folderName+statesFileName, 'r') as stateNamesFile:
    stateNames = numpy.asarray([ line.split(' ') for line in stateNamesFile])[0]
    print "Loading reachability matrix from file"
    for ra in range(0,NUMOFROBOTACTIONS):
      for ha in range(0,NUMOFHUMANACTIONS):
        with open(folderName + 'R' + str(ra+1)+str(ha+1)+'.dat', 'r') as reachFile:
          reachMtx= numpy.asarray([map(float, line.split('\t')) for line in reachFile])
          for ss in range(0, NUMOFSTATES):
            R[ss][ra][ha] = reachMtx[ss]
    
  print "Loading Transition Matrix from file"
  for yIndx in range(0,NUMOFUNOBSSTATES):
      for ra in range(0, NUMOFROBOTACTIONS):
        with open(folderName + 'T' + str(yIndx+1)+str(ra+1)+'.dat', 'r') as transFile:
          transMtx= numpy.asarray([map(float, line.split('\t')) for line in transFile])
          for ss in range(0, NUMOFSTATES):
            T[yIndx][ss][ra] = transMtx[ss]
 
  print "Loading Transition Matrix of unobserved states from file"
  for yIndx in range(0,NUMOFUNOBSSTATES):
      for ra in range(0, NUMOFROBOTACTIONS):
          with open(folderName + 'Tz' + str(yIndx+1)+str(ra+1)+'.dat', 'r')  as ytransFile:
            ytransMtx= numpy.asarray([map(float, line.split('\t')) for line in ytransFile])
            for nyIndx in range(0,NUMOFUNOBSSTATES):
              Tz[yIndx][ra][nyIndx] = ytransMtx[nyIndx]


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
    for vv in range(0,NUMOFALLUNOBSSTATES):
      A[counter][2+vv] = float(values[vv])
    counter = counter + 1


class Data: 
  
  def __init__(self, id):

    #loading data, these are the same for all users
    self.bel_t =  numpy.ones([NUMOFUNOBSSTATES,1])*(1.0/NUMOFUNOBSSTATES)

    self.bel_t[0] = 0.0364
    self.bel_t[1] = 0.2363
    self.bel_t[2] = 0.3273
    self.bel_t[3] = 0.1636
    self.bel_t[4] = 0.2364
    # bel_t[0] = 0.0
    # bel_t[1] = 0.58
    # bel_t[2] = 0.34
    # bel_t[3] = 0.08
    # bel_t[4] = 0.0
        
    self.currState = startStateIndx
    self.id = id  #this is a user id

    #embed()

  def stateUpdateFromHumanAction(self,humanAction):
    global stateNames
    robotAction = self.getRobotActionFromPolicy(self.currState, self.bel_t)
    #print 'You execute action: ' + STR_ACTIONS[humanAction]
    #print 'Robot does action: ' + STR_ACTIONS[robotAction]
    oldTableTheta = self.getTableThetaFromState(self.currState)

    nextState = self.getNextStateFromHumanRobotAction(self.currState,robotAction, humanAction)
    nextState = int(nextState)
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
      print "Robot action is: " + STR_ACTIONS[action]
    #return 0
    return action

  def getTableThetaFromState(self, ss):
    if (ss == startStateIndx):
      return startStateTheta
    else: 
      str_state = stateNames[ss]
      theta = int(str_state.split("_")[0][1:])
    return theta
    #if theta>=0 and theta<=180:
    #  return theta
    #else:
    # return startStateTheta

  def getNextStateFromHumanRobotAction(self, ss, ra, ha):
    nextStateMtx = R[ss][ra][ha][:]
    return nextStateMtx.argmax()

  def getNewBeliefFromHumanAction(self, ss, ra, nss, bel_t):
    bel_tp1 = numpy.zeros([NUMOFUNOBSSTATES,1])
    SumBeliefs = 0
    #embed()
    for nyy in range(0, NUMOFUNOBSSTATES): 
      for yy in range(0,  NUMOFUNOBSSTATES):
        bel_tp1[nyy] = bel_tp1[nyy] + T[yy][ss][ra][nss]*Tz[yy][ra][nyy]*bel_t[yy]
    
      SumBeliefs = SumBeliefs + bel_tp1[nyy]
    
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
  print "RESTART TASK!!"
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
  if(resultRAction=='TALK'):
    message = 'HERB says, "I know the best way to do the task." The table did not move.'
  elif(resultHAction=='ROTATE_CLOCKWISE')and(resultRAction=='ROTATE_CLOCKWISE'):
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
  return (currTableTheta, oldTableTheta, resultBelief, resultHAction, message, resultRAction)


# x = Data(1)
# currTableTheta = x.startStateTheta
# while (currTableTheta!=x.goal1StateTheta) and (currTableTheta!=x.goal2StateTheta):
#   print "The table rotation angle is: " + str(currTableTheta) + " degrees. "
#   if VERBOSE:
#     print "The current state is: " + x.stateNames[x.currState]
#     print "The current belief is: \n" + str(x.bel_t)
#   try:
#       humanAction = input('Enter human action [0 for ROTATE_CLOCKWISE, 1 for ROTATE_COUNTER_CLOCKWISE]: ')
#   except Exception as e:
#      print 'Exception: wrong input. '
#      continue
#   [currTableTheta, nextState] = x.stateUpdateFromHumanAction(humanAction)


# if currTableTheta == x.goal1StateTheta:
#   x.currState = x.goal1RestartStateIndx
# elif currTableTheta == x.goal2StateTheta:
#   x.currState = x.goal2RestartStateIndx
# #x.currState = x.startStateIndx
# currTableTheta = x.startStateTheta
# print "id={},current state is: {}\n".format(id, x.currState)
# while (currTableTheta!=x.goal1StateTheta) and (currTableTheta!=x.goal2StateTheta):
#   print "The table rotation angle is: " + str(currTableTheta) + " degrees. "
#   if VERBOSE:
#     print "The current state is: " + x.stateNames[x.currState]
#     print "The current belief is: \n" + str(x.bel_t)

#   try:
#       humanAction = input('Enter human action [0 for ROTATE_CLOCKWISE, 1 for ROTATE_COUNTER_CLOCKWISE]: ')
#   except Exception as e:
#      print 'Exception: wrong input. '
#      continue
#   [currTableTheta, nextState] = x.stateUpdateFromHumanAction(humanAction)


print 'Goal state reached. '
