__author__ = 'Stefanos'
import numpy
from IPython import embed
import  xml.etree.cElementTree as ET

VERBOSE = True


class Data:
  folderName = '../data/'
  momdpOutFolderName = '../data/'
  #folderName = '../../MatlabOutputFiles/'
  
  #momdpOutFolderName = '../../output/'
  policyFileName = 'TableCarryingTask.policy'
  statesFileName = 'obsState.dat'

  def __init__(self, id):

    #loading data, these are the same for all users
    self.startStateTheta = 100
    self.goal1StateTheta = 0
    self.goal2StateTheta = 180
    self.NUMOFSTATES = 734
    self.NUMOFROBOTACTIONS = 2
    self.NUMOFHUMANACTIONS = 2
    self.NUMOFUNOBSSTATES = 5
    self.STR_ACTIONS = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE']
    self.R = numpy.zeros([self.NUMOFSTATES,self.NUMOFROBOTACTIONS, self.NUMOFHUMANACTIONS, self.NUMOFSTATES])
    self.T = numpy.zeros([self.NUMOFUNOBSSTATES, self.NUMOFSTATES, self.NUMOFROBOTACTIONS, self.NUMOFSTATES])
    self.NUMOFALPHAVECTORS = 7527
    #self.NUMOFALPHAVECTORS = 42
    self.A = numpy.zeros([self.NUMOFALPHAVECTORS, self.NUMOFUNOBSSTATES + 2])
    #assume that the state before last is the starting state. The last one is the absorbing state
    self.startStateIndx = 640#self.NUMOFSTATES-2
    print "Loading state names from file"
    stateNamesFile = open(self.folderName+self.statesFileName, 'r')
    self.stateNames = numpy.asarray([ line.split(' ') for line in stateNamesFile])[0]
    self.goal1RestartStateIndx = 645
    self.goal2RestartStateIndx = 648
    self.goal1StateTheta = 0
    self.goal2StateTheta = 180

    print "Loading reachability matrix from file"
    for ra in range(0,self.NUMOFROBOTACTIONS):
      for ha in range(0,self.NUMOFHUMANACTIONS):
        reachFile= open(self.folderName + 'R' + str(ra+1)+str(ha+1)+'.dat', 'r')
        reachMtx= numpy.asarray([map(float, line.split('\t')) for line in reachFile])
        for ss in range(0, self.NUMOFSTATES):
          for nss in range(0,self.NUMOFSTATES):
            self.R[ss][ra][ha][nss] = reachMtx[ss][nss]
    print "Loading Transition Matrix from file"
    for yIndx in range(0,self.NUMOFUNOBSSTATES):
        for ra in range(0, self.NUMOFROBOTACTIONS):
           transFile = open(self.folderName + 'T' + str(yIndx+1)+str(ra+1)+'.dat', 'r')
           transMtx= numpy.asarray([map(float, line.split('\t')) for line in transFile])
           for ss in range(0, self.NUMOFSTATES):
             for nss in range(0, self.NUMOFSTATES):
               self.T[yIndx][ss][ra][nss] = transMtx[ss][nss]
    print "Loading XML policy file"
    tree = ET.parse(self.momdpOutFolderName + self.policyFileName)
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
      self.A[counter][0] = float(obsValue)
      self.A[counter][1] = float(action)
      for vv in range(0,self.NUMOFUNOBSSTATES):
        self.A[counter][2+vv] = float(values[vv])
      counter = counter + 1

    ##############The following variables are different per user########################
    self.bel_t = numpy.ones([5,1])*0.2
    #self.bel_t[0] = 1.0
    #self.bel_t[1] = 0.0
    #self.bel_t[2] = 0.0
    #self.bel_t[3] = 0.0
    #self.bel_t[4] = 0.0
    #self.bel_t[0] = 0.14
    #self.bel_t[1] = 0.5
    #self.bel_t[2] = 0.005
    #self.bel_t[3] = 0.005
    #self.bel_t[4] = 0.35
    #self.bel_t[0] = 0.000
    #self.bel_t[1] = 0.5
    #self.bel_t[2] = 0.3811
    #self.bel_t[3] = 0.1189
    #self.bel_t[4] = 0.00

    # self.bel_t[0] = 0.0
    # self.bel_t[1] = 0.58
    # self.bel_t[2] = 0.34
    # self.bel_t[3] = 0.08
    # self.bel_t[4] = 0.0

    # self.bel_t[0] = 0.22
    # self.bel_t[1] = 0.22
    # self.bel_t[2] = 0.22
    # self.bel_t[3] = 0.17
    # self.bel_t[4] = 0.17

    # self.bel_t[0] = 0.3
    # self.bel_t[1] = 0.3
    # self.bel_t[2] = 0.13
    # self.bel_t[3] = 0.13
    # self.bel_t[4] = 0.14

    # self.bel_t[0] = 0.0
    # self.bel_t[1] = 0.4972
    # self.bel_t[2] = 0.2873
    # self.bel_t[3] = 0.2155
    # self.bel_t[4] = 0.0

    # self.bel_t[0] = 0.0
    # self.bel_t[1] = 0.6538
    # self.bel_t[2] = 0.2518
    # self.bel_t[3] = 0.0944
    # self.bel_t[4] = 0.0

    # # self.bel_t[0] = 0.0
    # self.bel_t[1] = 0.3488
    # self.bel_t[2] = 0.3721
    # self.bel_t[3] = 0.2791
    # self.bel_t[4] = 0.0
    # self.bel_t[0] = 0.00
    # self.bel_t[1] = 0.4680
    # self.bel_t[2] = 0.3961
    # self.bel_t[3] =0.1360
    # self.bel_t[4] = 0.0


    # self.bel_t[0] = 0.0
    # self.bel_t[1] = 0.45
    # self.bel_t[2] = 0.4
    # self.bel_t[3] = 0.15
    # self.bel_t[4] = 0.0
    # self.bel_t[0] = 0.0
    # self.bel_t[1] = 1.0
    # self.bel_t[2] = 0.0
    # self.bel_t[3] = 0.0
    # self.bel_t[4] = 0.0

    self.currState = self.startStateIndx
    self.id = id  #this is a user id

  def stateUpdateFromHumanAction(self,humanAction):
    robotAction = x.getRobotActionFromPolicy(self.currState, self.bel_t)
    print 'You execute action: ' + x.STR_ACTIONS[humanAction]
    print 'Robot does action: ' + x.STR_ACTIONS[robotAction]

    nextState = x.getNextStateFromHumanRobotAction(self.currState,robotAction, humanAction)
    new_bel_t = x.getNewBeliefFromHumanAction(self.currState,robotAction,nextState, self.bel_t)
    self.bel_t = new_bel_t
    self.currState = nextState
    currTableTheta = x.getTableThetaFromState(self.currState)
    return [currTableTheta, self.currState]


  def getRobotActionFromPolicy(self, ss, bel_t):
    action = -1
    maxVal = -1
    for aa in range(0, self.NUMOFALPHAVECTORS):
      if(self.A[aa][0] == ss):
        val = numpy.dot(self.A[aa][2:self.NUMOFUNOBSSTATES+2],bel_t)
        if(val > maxVal):
          maxVal = val
          action = int(self.A[aa][1])
    if VERBOSE:
      print "Value function is: " + str(maxVal)
      print "Robot action is: " + self.STR_ACTIONS[action]
    #return 0
    return action

  def getTableThetaFromState(self, ss):
    str_state = self.stateNames[ss]
    theta = int(str_state.split("_")[0][1:])
    if theta>=0 and theta<=180:
      return theta
    else:
     return self.startStateTheta

  def getNextStateFromHumanRobotAction(self, ss, ra, ha):
    nextStateMtx = self.R[ss][ra][ha][:]
    return nextStateMtx.argmax()

  def getNewBeliefFromHumanAction(self, ss, ra, nss, bel_t):
    bel_tp1 = numpy.zeros([self.NUMOFUNOBSSTATES,1])
    SumBeliefs = 0
    #embed()
    for yy in range(0, self.NUMOFUNOBSSTATES):
      bel_tp1[yy] = self.T[yy][ss][ra][nss]*bel_t[yy]
      SumBeliefs = SumBeliefs + bel_tp1[yy]
    bel_tp1 = bel_tp1 / SumBeliefs
    return bel_tp1




x = Data(1)
embed()
currTableTheta = x.startStateTheta
while (currTableTheta!=x.goal1StateTheta) and (currTableTheta!=x.goal2StateTheta):
  print "The table rotation angle is: " + str(currTableTheta) + " degrees. "
  if VERBOSE:
    print "The current state is: " + x.stateNames[x.currState]
    print "The current belief is: \n" + str(x.bel_t)
  try:
      humanAction = input('Enter human action [0 for ROTATE_CLOCKWISE, 1 for ROTATE_COUNTER_CLOCKWISE]: ')
  except Exception as e:
     print 'Exception: wrong input. '
     continue
  [currTableTheta, nextState] = x.stateUpdateFromHumanAction(humanAction)


if currTableTheta == x.goal1StateTheta:
  x.currState = x.goal1RestartStateIndx
elif currTableTheta == x.goal2StateTheta:
  x.currState = x.goal2RestartStateIndx
currTableTheta = x.startStateTheta
print "id={},current state is: {}\n".format(id, x.currState)
while (currTableTheta!=x.goal1StateTheta) and (currTableTheta!=x.goal2StateTheta):
  print "The table rotation angle is: " + str(currTableTheta) + " degrees. "
  if VERBOSE:
    print "The current state is: " + x.stateNames[x.currState]
    print "The current belief is: \n" + str(x.bel_t)

  try:
      humanAction = input('Enter human action [0 for ROTATE_CLOCKWISE, 1 for ROTATE_COUNTER_CLOCKWISE]: ')
  except Exception as e:
     print 'Exception: wrong input. '
     continue
  [currTableTheta, nextState] = x.stateUpdateFromHumanAction(humanAction)


print 'Goal state reached. '
