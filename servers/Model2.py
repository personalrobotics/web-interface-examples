__author__ = 'Stefanos'
import numpy 
from IPython import embed
import  xml.etree.cElementTree as ET

VERBOSE = True  

#loading data, these are the same for all users
alpha = 1
startStateTheta = 100
goal1StateTheta = 0
goal2StateTheta = 180
NUMOFSTATES = 11
NUMOFROBOTACTIONS = 2
NUMOFHUMANACTIONS = 2
highRewardStateIndx = 0
lowRewardStateIndx = 9
HIGH_REWARD  = 14
LOW_REWARD = 10
STR_ACTIONS = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE']
R = numpy.zeros([NUMOFSTATES,NUMOFROBOTACTIONS, NUMOFHUMANACTIONS, NUMOFSTATES])
FORWARD_PHASE = 0
ROTATION_PHASE = 1
EXECUTION_PHASE = 2
#T = numpy.zeros([self.NUMOFSTATES, self.NUMOFROBOTACTIONS, self.NUMOFSTATES])
#Rew = numpy.zeros([self.NUMOFSTATES, self.NUMOFROBOTACTIONS])
stateNames = numpy.array(["0","20","40","60","80","100","120","140","160","180","FINAL_STATE"], dtype='object')
#assume that the state before last is the starting state. The last one is the absorbing state
startStateIndx = 5


def globalsInit():
  global R 
  print "Loading reachability matrix from file"
  for ra in range(0, NUMOFROBOTACTIONS):
    for ha in range(0, NUMOFHUMANACTIONS):
       for ss in range(0, NUMOFSTATES):
          nss = getNextStateFromRobotHumanAction(ss,ra,ha)
          R[ss][ra][ha][nss] = 1

def getNextStateFromRobotHumanAction(ss, ra, ha):
    nss = ss
    if(ss>0)and(ss<9):
      if(ra==0) and (ha==0):
        nss = max(ss - 1,0)
        #print '00'
      elif(ra==1)and(ha==1):
        nss = min(ss+1,9)
        #print '11'
      else:
        #print '01'
        nss = ss
    else:
      #print 'final'
      nss = NUMOFSTATES-1
    return nss



class Data:

  def __init__(self, id):
    ##############The following variables are different per user########################
    self.bel_t = numpy.ones([5,1])*0.2
    self.bel_t[0] = 0.14
    self.bel_t[1] = 0.5
    self.bel_t[2] = 0.005
    self.bel_t[3] = 0.005
    self.bel_t[4] = 0.35
    self.currState = startStateIndx
    self.prevGoalStateTheta = -1
    self.phase = FORWARD_PHASE
    self.stateActionSeqForw = []
    self.stateActionSeqForw.append(startStateIndx)

    self.id = id  #this is a user id

    #cross-training user-specific data
    self.T = numpy.zeros([NUMOFSTATES, NUMOFROBOTACTIONS, NUMOFSTATES])
    self.Rew = numpy.zeros([NUMOFSTATES, NUMOFROBOTACTIONS])
    print "Generating Transition Matrix"
    for ra in range(0, NUMOFROBOTACTIONS):
      for ss in range(0, NUMOFSTATES):
        Sum = 0
        for nss in range(0, NUMOFSTATES):
          if(R[ss][ra][0][nss]==1):
             #uniform transition matrix
              #self.T[ss][ra][nss] = 1
              if(ra == 0):
                self.T[ss][ra][nss] = 1
          elif(R[ss][ra][1][nss]==1):
             #uniform transition matrix
             #self.T[ss][ra][nss] = 1
              # robot-follower transition matrix
             if(ra == 1):
                self.T[ss][ra][nss] = 1

          Sum = Sum + self.T[ss][ra][nss]

        for nss in range(0, NUMOFSTATES):
          self.T[ss][ra][nss] = self.T[ss][ra][nss]/Sum

    print "Generating Reward Matrix"
    for ss in range(0, NUMOFSTATES):
      if(ss == highRewardStateIndx):
        self.Rew[ss] = HIGH_REWARD
      elif(ss==lowRewardStateIndx):
        self.Rew[ss] = LOW_REWARD
      else:
        self.Rew[ss] = 0

    self.ValueIteration()
    self.PrintPolicy()

  def getRobotActionFromPolicy(self, ss):
    action = int(self.Pi[ss])
    return action

  def getTableThetaFromState(self, ss):
    thetaIndx = int(ss)
    if(thetaIndx>=0) and (thetaIndx<=9):
     return thetaIndx*20 #assume 20 degree increments
    else:
     return self.startStateTheta

  def getNextStateFromReachMtx(self, ss, ra, ha):
    if VERBOSE:
      print "The current state is: " + stateNames[ss]
      print 'Human does action: ' + STR_ACTIONS[ha]
      print 'Robot does action: ' + STR_ACTIONS[int(ra)]
    nextStateMtx = R[ss][ra][ha][:]
    nextStateIndx = nextStateMtx.argmax()
    #nextStateTheta = self.getTableThetaFromState(nextStateIndx)
    return nextStateIndx

  def getHumanAction(self, ss, ra, nss):
    for ha in range(0, NUMOFHUMANACTIONS):
      if(R[ss][ra][ha][nss]==1):
        return ha
  
  def printState(self,ss):
     print 'State is: ' + stateNames[ss]
     return stateNames[ss]

  def printAction(self,aa):
     print 'Action is: ' + STR_ACTIONS[aa]
     return STR_ACTIONS[aa]

  def updateReward(self, stateActionSeq):
  	c = 20
  	print "\n Updating Reward Function"

  	#set closest final state with maximum reward, to ensure task will finish
  	final_state = stateActionSeq[len(stateActionSeq)-1]
  	for aa in range(0, NUMOFROBOTACTIONS):
  	  if(final_state== highRewardStateIndx):
  		  self.Rew[highRewardStateIndx][aa] = c
  	  elif(final_state== lowRewardStateIndx):
  		  self.Rew[lowRewardStateIndx][aa] = c
  	  else:
  		  print "error: final_state not one of the two final states"
 
  def updateTransitionProb(self, stateActionSeq):
    print "\nUpdating Transition Matrix"
    ii = 0
    while(ii < len(stateActionSeq)-2):
      ss = stateActionSeq[ii]
      aa = stateActionSeq[ii+1]
      nss = stateActionSeq[ii+2]
      ii = ii + 2
      if VERBOSE:
        self.printState(int(ss))
        self.printAction(int(aa))
        self.printState(int(nss))
      self.T[ss][aa][nss] = self.T[ss][aa][nss] + alpha
    #normalization
    for ss in range(0, NUMOFSTATES):
      for ra in range(0, NUMOFROBOTACTIONS):
        Sum = 0
        for nss in range(0, NUMOFSTATES):
          Sum = Sum + self.T[ss][ra][nss]
        for nss in range(0, NUMOFSTATES):
          self.T[ss][ra][nss]  = self.T[ss][ra][nss]/Sum
  
  def sampleHumanAction(self, ss, ra):
    probs = []
    has = []
    for nss in range(0, NUMOFSTATES):
      if(self.T[ss][ra][nss]>0):
        probs.append(self.T[ss][ra][nss])
        has.append(self.getHumanAction(ss,ra,nss))
    haIndx = numpy.argmax(numpy.random.multinomial(1,probs,size=1))
    return has[haIndx]

  def PrintPolicy(self):
    for ss in range(0, NUMOFSTATES):
      print  "[" + self.printState(ss) + "]: "
      print  self.printAction(int(self.Pi[ss])) + "\n"

  def ValueIteration(self):
    self.Pi = numpy.zeros(NUMOFSTATES)
    eps = 1e-3
    gamma = 0.9
    prevV = numpy.zeros(NUMOFSTATES)
    self.V = numpy.zeros(NUMOFSTATES)
    while(True):
      for ss in range(0, NUMOFSTATES):
        maxActionIndx = -1
        maxActionVal = float('-inf')
        for ra in range(0, NUMOFROBOTACTIONS):
          actionVal = self.Rew[ss][ra]
          for nss in range(0, NUMOFSTATES):
               actionVal = actionVal + gamma * self.T[ss][ra][nss]* prevV[nss]
          if(actionVal > maxActionVal):
            maxActionVal = actionVal
            maxActionIndx = ra
        self.V[ss] =  maxActionVal
        self.Pi[ss] = maxActionIndx
      diff = self.V - prevV
      maxDiff = numpy.max(diff)
      print maxDiff
      if(maxDiff<eps):
        break

      for ss in range(0,NUMOFSTATES):
        prevV[ss] = self.V[ss]
      #from IPython import embed
      #embed()

def idInitiated(id,d):
  if id in d:
    return True
  else:
    return False

def startTaskExecutionPhase(d, id):
  print("IN:id={}".format(id))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x  
    print ("Model2py@startTaskExecutionPhase Error: No class instance found!")
    print("New class instance created: id={}".format(id))

  x.updateReward(x.stateActionSeqRot)
  x.ValueIteration()
  x.PrintPolicy()
  x.phase = EXECUTION_PHASE
  x.currState = startStateIndx


def startRotationPhase(d, id):
  print("IN:id={}".format(id))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x  
    print ("Model2py@startRotationPhase Error: No class instance found!")
    print("New class instance created: id={}".format(id))

  x.updateTransitionProb(x.stateActionSeqForw)
  x.phase = ROTATION_PHASE
  x.currState = startStateIndx
  x.stateActionSeqRot = []
  x.stateActionSeqRot.append(startStateIndx)



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
  if x.phase == FORWARD_PHASE:
     robotAction = x.getRobotActionFromPolicy(x.currState)
     x.stateActionSeqForw.append(robotAction)

     oldTableTheta = x.getTableThetaFromState(x.currState)
     if VERBOSE:
        print "The current state is: " + stateNames[x.currState]
        print 'Human does action: ' + STR_ACTIONS[humanAction]
        print 'Robot does action: ' + STR_ACTIONS[int(robotAction)]

     nextState = x.getNextStateFromReachMtx(x.currState, robotAction, humanAction)
     x.currState = nextState
     currTableTheta = x.getTableThetaFromState(x.currState)  
     x.stateActionSeqForw.append(x.currState)

  elif x.phase == ROTATION_PHASE:
     #in the rotation phase the human action is actually the robotAction
     oldTableTheta = x.getTableThetaFromState(x.currState)
     robotAction = humanAction
     x.stateActionSeqRot.append(robotAction)
     humanAction = x.sampleHumanAction(x.currState, robotAction)
     if VERBOSE:
        print "The current state is: " + stateNames[x.currState]
        print 'Human demonstrates robot action: ' + STR_ACTIONS[robotAction]
        print 'Robot samples human action: ' + STR_ACTIONS[int(humanAction)]
      #stateActionSeqRot.append(robotAction)
     x.currState = x.getNextStateFromReachMtx(x.currState, robotAction, humanAction)
     currTableTheta = x.getTableThetaFromState(x.currState)  
     x.stateActionSeqRot.append(x.currState)

  elif x.phase == EXECUTION_PHASE:
     #in the execution phase
     robotAction = x.getRobotActionFromPolicy(x.currState)
     oldTableTheta = x.getTableThetaFromState(x.currState)
     if VERBOSE:
        print "The current state is: " + stateNames[x.currState]
        print 'Human does action: ' + STR_ACTIONS[humanAction]
        print 'Robot does action: ' + STR_ACTIONS[int(robotAction)]

     nextState = x.getNextStateFromReachMtx(x.currState, robotAction, humanAction)
     x.currState = nextState
     currTableTheta = x.getTableThetaFromState(x.currState)  
  else:
     print "Model2@Error: unknown phase!"

  
  resultState = stateNames[x.currState]
  resultHAction = STR_ACTIONS[humanAction]
  resultRAction = STR_ACTIONS[robotAction]  
  resultBelief = ' '
     #currTableTheta, resultState, resultBelief, resultHAction, resultRAction, oldTableTheta = \
     #x.stateUpdateFromHumanAction(humanAction)
  # elif x.phase == "ROTATION_PHASE":


  print("OUT:theta={}".format(currTableTheta))
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
  return (currTableTheta, oldTableTheta, message)
