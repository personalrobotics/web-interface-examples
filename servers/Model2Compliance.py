__author__ = 'Stefanos'
import numpy
from IPython import embed
import  xml.etree.cElementTree as ET

VERBOSE = True

folderName = 'dataCompliance/compliance/'
momdpOutFolderName = 'dataCompliance/compliance/'
#folderName = '../../MatlabOutputFiles/'  
#momdpOutFolderName = '../../output/'
policyFileName = 'TwoVariablesLong20-10NP3.policy'
statesFileName = 'obsState.dat'

#loading data, these are the same for all users
startStateTheta = 100
goal1StateTheta = 0
goal2StateTheta = 180
NUMOFSTATES = 4298
NUMOFROBOTACTIONS = 4
NUMOFHUMANACTIONS = 2
NUMOFZUNOBSSTATES = 5
NUMOFUNOBSSTATES = 5
NUMOFALLUNOBSSTATES = NUMOFZUNOBSSTATES * NUMOFUNOBSSTATES
STR_ACTIONS = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE','TALK_CLOCKWISE','TALK_COUNTERCLOCKWISE']
R = numpy.zeros([NUMOFSTATES,NUMOFROBOTACTIONS,NUMOFHUMANACTIONS])
T = []
for zz in range(NUMOFZUNOBSSTATES):
 zz = []
 for yy in range(NUMOFUNOBSSTATES):
   yy = []
   for ss in range(NUMOFSTATES):
     ss = []
     for ra in range(NUMOFROBOTACTIONS):
         ra = []
         ss.append(ra)
     yy.append(ss)
   zz.append(yy)
 T.append(zz)

Tprob = []
for zz in range(NUMOFZUNOBSSTATES):
 zz = []
 for yy in range(NUMOFUNOBSSTATES):
   yy = []
   for ss in range(NUMOFSTATES):
     ss = []
     for ra in range(NUMOFROBOTACTIONS):
         ra = []
         ss.append(ra)
     yy.append(ss)
   zz.append(yy)
 Tprob.append(zz)

#self.NUMOFALPHAVECTORS = 6932
NUMOFALPHAVECTORS = 50829
A = numpy.zeros([NUMOFALPHAVECTORS, NUMOFALLUNOBSSTATES + 2])
#assume that the state before last is the starting state. The last one is the absorbing state
startStateIndx = 0 #5120
print "Loading state names from file"
stateNamesFile = open(folderName+statesFileName, 'r')
stateNames = numpy.asarray([ line.split(' ') for line in stateNamesFile])[0]
goal1RestartStateIndx = 4234
goal2RestartStateIndx = 4133
goal1StateTheta = 0
goal2StateTheta = 180

def globalsInit():

    print "Loading reachability matrix from file"
    for ra in range(0,NUMOFROBOTACTIONS):
      for ha in range(0,NUMOFHUMANACTIONS):
        reachFile= open(folderName + 'R' + str(ra+1)+str(ha+1)+'.dat', 'r')
        #reachMtx= numpy.asarray([map(float, line.split('\n')) for line in reachFile])
        reachMtx = numpy.asarray(reachFile.readlines())
        for ss in range(0, NUMOFSTATES):
            R[ss][ra][ha] = reachMtx[ss]
            R[ss][ra][ha] = int(R[ss][ra][ha])-1
    print "Loading Transition Matrix from file"
    for zIndx in range(0,NUMOFZUNOBSSTATES):
      for yIndx in range(0,NUMOFUNOBSSTATES):
         for ra in range(0, NUMOFROBOTACTIONS):
            transFile = open(folderName + 'T' + str(zIndx+1) + str(yIndx+1)+str(ra+1)+'.dat', 'r')
            #transMtx= numpy.asarray([map(float, line.split('\t')) for line in transFile])
            results = []
            for line in transFile:
              results.append(line.strip().split('\t'))
            for ss in range(0, NUMOFSTATES):
                T[zIndx][yIndx][ss][ra] = results[ss]
                numEl = len(T[zIndx][yIndx][ss][ra])
                for el in range(0,numEl):
                  T[zIndx][yIndx][ss][ra][el] = int(T[zIndx][yIndx][ss][ra][el])-1


    
    print "Loading Transition Probability Matrix from file"
    for zIndx in range(0,NUMOFZUNOBSSTATES):
      for yIndx in range(0,NUMOFUNOBSSTATES):
         for ra in range(0, NUMOFROBOTACTIONS):
            transProbFile = open(folderName + 'Tprob' + str(zIndx+1) + str(yIndx+1)+str(ra+1)+'.dat', 'r')

            results = []
            for line in transProbFile:
              results.append(line.strip().split('\t'))
            for ss in range(0, NUMOFSTATES):
                Tprob[zIndx][yIndx][ss][ra] = results[ss]
                numEl = len(T[zIndx][yIndx][ss][ra])
                for nss in range(0, numEl):
                  Tprob[zIndx][yIndx][ss][ra][nss] = float(Tprob[zIndx][yIndx][ss][ra][nss])
 


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

	    # #loading data, these are the same for all users
	    # self.startStateTheta = 100
	    # self.goal1StateTheta = 0
	    # self.goal2StateTheta = 180
	    # self.NUMOFSTATES = 4298
	    # self.NUMOFROBOTACTIONS = 4
	    # self.NUMOFHUMANACTIONS = 2
	    # self.NUMOFZUNOBSSTATES = 5
	    # self.NUMOFUNOBSSTATES = 5
	    # self.NUMOFALLUNOBSSTATES = self.NUMOFZUNOBSSTATES * self.NUMOFUNOBSSTATES
	    # self.STR_ACTIONS = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE','TALK_CLOCKWISE','TALK_COUNTERCLOCKWISE']
	    # self.R = numpy.zeros([self.NUMOFSTATES,self.NUMOFROBOTACTIONS,self.NUMOFHUMANACTIONS])
	    # self.T = []
	    # for zz in range(self.NUMOFZUNOBSSTATES):
	    #  zz = []
	    #  for yy in range(self.NUMOFUNOBSSTATES):
	    #    yy = []
	    #    for ss in range(self.NUMOFSTATES):
	    #      ss = []
	    #      for ra in range(self.NUMOFROBOTACTIONS):
	    #          ra = []
	    #          ss.append(ra)
	    #      yy.append(ss)
	    #    zz.append(yy)
	    #  self.T.append(zz)

	    # self.Tprob = []
	    # for zz in range(self.NUMOFZUNOBSSTATES):
	    #  zz = []
	    #  for yy in range(self.NUMOFUNOBSSTATES):
	    #    yy = []
	    #    for ss in range(self.NUMOFSTATES):
	    #      ss = []
	    #      for ra in range(self.NUMOFROBOTACTIONS):
	    #          ra = []
	    #          ss.append(ra)
	    #      yy.append(ss)
	    #    zz.append(yy)
	    #  self.Tprob.append(zz)

	    # #self.NUMOFALPHAVECTORS = 6932
	    # self.NUMOFALPHAVECTORS = 50829
	    # self.A = numpy.zeros([self.NUMOFALPHAVECTORS, self.NUMOFALLUNOBSSTATES + 2])
	    # #assume that the state before last is the starting state. The last one is the absorbing state
	    # self.startStateIndx = 0 #5120
	    # print "Loading state names from file"
	    # stateNamesFile = open(self.folderName+self.statesFileName, 'r')
	    # self.stateNames = numpy.asarray([ line.split(' ') for line in stateNamesFile])[0]
	    # self.goal1RestartStateIndx = 4234
	    # self.goal2RestartStateIndx = 4133
	    # self.goal1StateTheta = 0
	    # self.goal2StateTheta = 180

	    # print "Loading reachability matrix from file"
	    # for ra in range(0,self.NUMOFROBOTACTIONS):
	    #   for ha in range(0,self.NUMOFHUMANACTIONS):
	    #     reachFile= open(self.folderName + 'R' + str(ra+1)+str(ha+1)+'.dat', 'r')
	    #     #reachMtx= numpy.asarray([map(float, line.split('\n')) for line in reachFile])
	    #     reachMtx = numpy.asarray(reachFile.readlines())
	    #     for ss in range(0, self.NUMOFSTATES):
	    #         self.R[ss][ra][ha] = reachMtx[ss]
	    #         self.R[ss][ra][ha] = int(self.R[ss][ra][ha])-1
	    # print "Loading Transition Matrix from file"
	    # for zIndx in range(0,self.NUMOFZUNOBSSTATES):
	    #   for yIndx in range(0,self.NUMOFUNOBSSTATES):
	    #      for ra in range(0, self.NUMOFROBOTACTIONS):
	    #         transFile = open(self.folderName + 'T' + str(zIndx+1) + str(yIndx+1)+str(ra+1)+'.dat', 'r')
	    #         #transMtx= numpy.asarray([map(float, line.split('\t')) for line in transFile])
	    #         results = []
	    #         for line in transFile:
	    #           results.append(line.strip().split('\t'))
	    #         for ss in range(0, self.NUMOFSTATES):
	    #             self.T[zIndx][yIndx][ss][ra] = results[ss]
	    #             numEl = len(self.T[zIndx][yIndx][ss][ra])
	    #             for el in range(0,numEl):
	    #               self.T[zIndx][yIndx][ss][ra][el] = int(self.T[zIndx][yIndx][ss][ra][el])-1


	    
	    # print "Loading Transition Probability Matrix from file"
	    # for zIndx in range(0,self.NUMOFZUNOBSSTATES):
	    #   for yIndx in range(0,self.NUMOFUNOBSSTATES):
	    #      for ra in range(0, self.NUMOFROBOTACTIONS):
	    #         transProbFile = open(self.folderName + 'Tprob' + str(zIndx+1) + str(yIndx+1)+str(ra+1)+'.dat', 'r')

	    #         results = []
	    #         for line in transProbFile:
	    #           results.append(line.strip().split('\t'))
	    #         for ss in range(0, self.NUMOFSTATES):
	    #             self.Tprob[zIndx][yIndx][ss][ra] = results[ss]
	    #             numEl = len(self.T[zIndx][yIndx][ss][ra])
	    #             for nss in range(0, numEl):
	    #               self.Tprob[zIndx][yIndx][ss][ra][nss] = float(self.Tprob[zIndx][yIndx][ss][ra][nss])
	 


	    # print "Loading XML policy file"
	    # tree = ET.parse(self.momdpOutFolderName + self.policyFileName)
	    # root = tree.getroot()
	    # numVectors = len(root.getchildren()[0].getchildren())
	    # print numVectors
	    # print root.iter('Vector')
	    # counter = 0
	    # for vector in root.iter('Vector'):
	    #   obsValue  = vector.get('obsValue')
	    #   action = vector.get('action')
	    #   values = vector.text.split(' ')

	    #   # vector format: obsValue, action, values
	    #   self.A[counter][0] = float(obsValue)
	    #   self.A[counter][1] = float(action)
	    #   for vv in range(0,self.NUMOFALLUNOBSSTATES):
	    #     self.A[counter][2+vv] = float(values[vv])
	    #   counter = counter + 1

	    ##############The following variables are different per user########################
	    #self.bel_t =  numpy.ones([self.NUMOFALLUNOBSSTATES,1])*(1.0/self.NUMOFALLUNOBSSTATES)

	    self.bel_t =  numpy.zeros([NUMOFALLUNOBSSTATES,1])*(1.0/NUMOFALLUNOBSSTATES)
	    #initialize belief
	    for zz in range(0, NUMOFZUNOBSSTATES):
	      for yy in range(0, NUMOFUNOBSSTATES):
	        bel_indx = NUMOFUNOBSSTATES*zz+yy
	        if yy == 0:
	            proby = 0.0364
	        elif yy == 1: 
	            proby = 0.2364
	        elif yy == 2:
	            proby = 0.3272
	        elif yy == 3:
	            proby = 0.1636
	        else: 
	            proby = 0.2364
	        #if zz == 0 or zz == 4:
	        #     probz = 0.5
	        #else: 
	        #     probz = 0.0
	        if zz == 0:
	            probz = 0.0400
	        elif zz == 1:
	            probz = 0.1000
	        elif zz == 2:
	            probz = 0.2000
	        elif zz == 3:
	            probz = 0.0600
	        else: 
	            probz = 0.6000
	 
	        prob = proby * probz
	        self.bel_t[bel_indx] = prob
	        
	    self.currState = startStateIndx
	    self.id = id  #this is a user id

	    #embed()

	def stateUpdateFromHumanAction(self,humanAction):
		#global x
		global stateNames
		# robotAction = x.getRobotActionFromPolicy(self.currState, self.bel_t)
		# print 'You execute action: ' + x.STR_ACTIONS[humanAction]
		# print 'Robot does action: ' + x.STR_ACTIONS[robotAction]
		# oldTableTheta = self.getTableThetaFromState(self.currState)
		# nextState = x.getNextStateFromHumanRobotAction(self.currState,robotAction, humanAction)
		# nextState = int(nextState)
		# new_bel_t = x.getNewBeliefFromHumanAction(self.currState,robotAction,nextState, self.bel_t)
		# self.bel_t = new_bel_t
		# self.currState = nextState
		# currTableTheta = x.getTableThetaFromState(self.currState)
		
		robotAction = self.getRobotActionFromPolicy(self.currState, self.bel_t)
		print 'You execute action: ' + STR_ACTIONS[humanAction]
		print 'Robot does action: ' + STR_ACTIONS[robotAction]
		oldTableTheta = self.getTableThetaFromState(self.currState)
		nextState = self.getNextStateFromHumanRobotAction(self.currState,robotAction, humanAction)
		nextState = int(nextState)
		new_bel_t = self.getNewBeliefFromHumanAction(self.currState,robotAction,nextState, self.bel_t)
		self.bel_t = new_bel_t
		self.currState = nextState
		currTableTheta = self.getTableThetaFromState(self.currState)
		#global stateNames

		resultState = stateNames[self.currState]
		resultBelief = self.bel_t
		resultHAction = STR_ACTIONS[humanAction]
		resultRAction = STR_ACTIONS[robotAction]

		return (currTableTheta, resultState, resultBelief, resultHAction, resultRAction, oldTableTheta)



	def getRobotActionFromPolicy(self, ss, bel_t):
	    action = -1
	    maxVal = -100000
	    bel_tp1 = numpy.zeros([NUMOFALLUNOBSSTATES,1])
	    #fix order of beliefs
	    bel_tp1[0] = bel_t[0]
	    bel_tp1[1] = bel_t[5]
	    bel_tp1[2] = bel_t[10]
	    bel_tp1[3] = bel_t[15]
	    bel_tp1[4] = bel_t[20]
	    bel_tp1[5] = bel_t[1]
	    bel_tp1[6] = bel_t[6]
	    bel_tp1[7] = bel_t[11]
	    bel_tp1[8] = bel_t[16]
	    bel_tp1[9] = bel_t[21]
	    bel_tp1[10] = bel_t[2]
	    bel_tp1[11] = bel_t[7]
	    bel_tp1[12] = bel_t[12]
	    bel_tp1[13] = bel_t[17]
	    bel_tp1[14] = bel_t[22]
	    bel_tp1[15] = bel_t[3]
	    bel_tp1[16] = bel_t[8]
	    bel_tp1[17] = bel_t[13]
	    bel_tp1[18] = bel_t[18]
	    bel_tp1[19] = bel_t[23]
	    bel_tp1[20] = bel_t[4]
	    bel_tp1[21] = bel_t[9]
	    bel_tp1[22] = bel_t[14]
	    bel_tp1[23] = bel_t[19]
	    bel_tp1[24] = bel_t[24]
	    #if ss == 2383:
	    #    embed()
	   
	    for aa in range(0, NUMOFALPHAVECTORS):
	      if(A[aa][0] == ss):
	        #embed()
	        val = numpy.dot(A[aa][2:NUMOFALLUNOBSSTATES+2],bel_tp1)
	        if(val > maxVal):
	          maxVal = val
	          action = int(A[aa][1])
	    if VERBOSE:
	      #print "state indx is: " + str(ss) 
	      print "Value function is: " + str(maxVal)
	      #print "Robot action is: " + self.STR_ACTIONS[action]
	      #print "belief for robot actions is: " + str(bel_t)
	    #return 0
	    return action

	def getTableThetaFromState(self, ss):
	    if ss == startStateIndx:
	      return startStateTheta
	    str_state = stateNames[ss]
	    theta = int(str_state.split("_")[0][1:])

	    if theta>=0 and theta<=180:
	      return theta
	    else:
	      print "Error! Unknown theta value!"
	      return -1

	def getNextStateFromHumanRobotAction(self, ss, ra, ha):
	    nextState = R[ss][ra][ha]
	    return nextState

	def getNewBeliefFromHumanAction(self, ss, ra, nss, bel_t):
	    bel_tp1 = numpy.zeros([NUMOFALLUNOBSSTATES,1])
	    SumBeliefs = 0
	    print 'new belief'
	    for zz in range(0, NUMOFZUNOBSSTATES):
	      for yy in range(0, NUMOFUNOBSSTATES):
	        bel_indx = NUMOFUNOBSSTATES*zz+yy
	        #embed()
	        nssIndx = T[zz][yy][ss][ra].index(nss)
	        bel_tp1[bel_indx] = Tprob[zz][yy][ss][ra][nssIndx]*bel_t[bel_indx]
	        SumBeliefs = SumBeliefs + bel_tp1[bel_indx]
	    bel_tp1 = bel_tp1 / SumBeliefs
	    return bel_tp1
#x=Data(1)	 


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
    print ("Model2py@setPrevGoalState Error: No class instance found!")
    print("New class instance setPrev created: id={}".format(id))
  
  x.prevGoalStateTheta = prevGoalStateTheta

def resetTask(d, id): 
  print("IN:id={}".format(id))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    #x = Data(id)
    d[id] = x  
    print ("Model2py@resetTask Error: No class instance found!")
    print("New class instance Reset created: id={}".format(id))
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
    #x = Data(id)
    d[id] = x  
    print ("Model2py@restartTask Error: No class instance found!")
    print("New class instance Restart created: id={}".format(id))
  #logic that says what the next state will be based on the previous goal
  if x.prevGoalStateTheta == goal1StateTheta:
    x.currState = goal1RestartStateIndx
    print "id={},current state is: {}\n".format(id, x.currState)
  elif x.prevGoalStateTheta == goal2StateTheta:
    x.currState = goal2RestartStateIndx
    print "id={},current states: {}\n".format(id, x.currState)
  else:
    print ("Model2py@restartTask invalid theta value {}".format(x.prevGoalStateTheta))
#x = Data(1)
#the server will call this function passing the id and the button pressed
#we'll store the class instances in a dictionary with IDs as keys
#idInitiated helper function checks if id is in the dictionary
def getMove(d,id,humanAction, prior):
  #global x
  #print("IN:id={},action={}".format(id,humanAction))
  #print "X:" + str(x)

  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    print "else statement"

    d[id] = x
    print("New class instance get Move created: id={}".format(id))
  currTableTheta, resultState, resultBelief, resultHAction, resultRAction, oldTableTheta = \
    x.stateUpdateFromHumanAction(humanAction)
  print("OUT:theta={}".format(currTableTheta))

  if(resultRAction=='TALK_CLOCKWISE'):
  	message = 'HERB says, "Let\'s turn the table CLOCKWISE." <br> The table did not turn' 
  elif(resultRAction=='TALK_COUNTERCLOCKWISE'):
  	message = 'HERB says, "Let\'s turn the table COUNTER-CLOCKWISE." <br> The table did not turn' 
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
  # instructionString ='''The current angle is: {}<br> The current state is: {}<br>  The current belief is: {}<br> You did action: {}<br> Robot did action: {}<br>
  #   Old angle is {}<br> '''.format(currTableTheta, resultState, resultBelief, resultHAction, resultRAction, oldTableTheta)
  # message = message + instructionString
  print "MESSAGE: " + message
  return (currTableTheta, oldTableTheta, resultBelief, resultHAction, message, resultRAction)


###############################################################################################################        

#x = Data(1)
# currTableTheta = x.startStateTheta
# while (currTableTheta!=x.goal1StateTheta) and (currTableTheta!=x.goal2StateTheta):
#   print "The table rotation angle is: " + str(currTableTheta) + " degrees. "
#   if VERBOSE:
#     print "The current state is: " + x.stateNames[x.currState]
#     print "state number: " + str(x.currState)
#     print "The current belief is: \n" + str(x.bel_t)
#   try:
#       humanAction = input('Enter human action [0 for ROTATE_CLOCKWISE, 1 for ROTATE_COUNTER_CLOCKWISE]: ')
#   except Exception as e:
#      print 'Exception: wrong input. '
#      continue
#  # [currTableTheta, nextState] = x.stateUpdateFromHumanAction(humanAction)
#   currTableTheta, resultState, resultBelief, resultHAction, resultRAction, oldTableTheta = \
#   	x.stateUpdateFromHumanAction(humanAction)


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


# print 'Goal state reached. '
