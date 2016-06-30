from bottle import Bottle, run, static_file, request,response
import json
import string
import random
import json
import Model2
import os
import shutil
import time 
import datetime

app = Bottle()
data = dict()
d=dict()
timestart1 = dict()
timestart2 = dict()
timestart3 = dict()
timestart4 = dict()
trialIndx = dict()
prior = True #condition is set to true when collecting priors
cheating = True
#loads static pages from the directory
#example: website.com/index.html
#server will load index.html from the directory

def remove_dups(string, info, mturk_id):
  global data
  lastInd = len(data[mturk_id])-1

  if (info != data[mturk_id][lastInd] and string==""):
    data[mturk_id].append(string+ str(info))
  elif(string not in data[mturk_id][lastInd] and string!=""):
    data[mturk_id].append(string+ str(info))
  else:
    data[mturk_id][lastInd]=string+ str(info)
  return data

def remove_dups_trial(trialNum, mturk_id):
  global data
  lastInd = len(data[mturk_id])-1

  belief_start_index = trialNum.find("belief")
  belief_end_index = belief_start_index+7
  trial = trialNum[:belief_end_index+1]

  if(trial not in data[mturk_id][lastInd]):
    data[mturk_id].append(trialNum)
  else:
    data[mturk_id][lastInd] = trialNum
  return data

@app.route('<path:path>')
def server_static(path):
  return static_file(path, root=".")

#handles buttonpress post requests by buttonClicked function in the js
#the input is provided through the request data
#we retrieve it using json.loads
#the server decides what to load next by looking into the request data
# and seeing what the current state of the webapp is
@app.post('/ui/button')
def do_click():
  global prevTableTheta
  

  #init dictionary of users
  global d

  #add artificial delay
  time.sleep(0.5)

  #manually set value
  totalPicsNum = 19
  survey_duration = 10*60*60 #10 hours to prevent retaking

  #get the data that the buttonClicked posted
  requestData = json.loads(request.body.getvalue())
  sessionData = requestData["sessionData"]

  if "toSurvey" in sessionData:
    return json.dumps({"toSurvey":True})

  #init log variable
  global data

  #go to next/prev pic according to button clicked
  buttonClicked = requestData["buttonID"]
  if sessionData["picCount"]<8:
    if buttonClicked==0:
      sessionData["picCount"] -= 1
    elif buttonClicked==1:
      sessionData["picCount"] += 1


  if sessionData["picCount"]==0:
    ret = {"imageURL": "",
           "buttonLabels": ["null", "Next"],
           "instructionText": "",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret) 

  worker_id = requestData["worker_id"]
  response.set_cookie('worker_id', worker_id, max_age=survey_duration, path='/')

  if sessionData["picCount"]==1:
    exists = 0
    #if worker id does not already exist:
    for key,value in data.items():
      if worker_id in value:
        exists=1
    if(exists==0):
      gen_id = ''.join(random.choice(string.ascii_uppercase +
        string.digits) for _ in range(6))
      response.set_cookie('mturk_id', gen_id, max_age=survey_duration, path='/')
      data[gen_id] = []
      data[gen_id].append(worker_id)
    ret = {"imageURL": "images/Slide1.JPG",
           "buttonLabels": ["null", "Next"],
           "instructionText": "",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)

  mturk_id = request.cookies.get('mturk_id','NOT SET')

  if sessionData["picCount"]==2:
    #generate a cookie with user's ID
    #get ip
    ip = request.environ.get('REMOTE_ADDR')
    data = remove_dups("", ip, mturk_id)
    ret = {"imageURL": "images/Slide2.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Instructions",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)
    
  if sessionData["picCount"]==3:
    trialIndx[mturk_id] = 1
    ret = {"imageURL": "images/Slide3.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Instructions",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==4:
    ret = {"imageURL": "images/Slide4.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Instructions: Selecting a Starting Preference",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==5:
    lastInd = len(data[mturk_id])-1
    if ("radioChoice" in requestData.keys() and "radioChoice: " not in data[mturk_id][lastInd]):
      data[mturk_id].append("radioChoice: "+ requestData["radioChoice"])
    elif("radioChoice: " in data[mturk_id][lastInd]):
      data[mturk_id][lastInd] = "radioChoice: "+ requestData["radioChoice"]
    ret = {"imageURL": "images/HERBspeaks.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Instructions",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==6:
    # we got the results from slide4 radio
    ret = {"imageURL": "",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)



  if sessionData["picCount"]==7:
    data = remove_dups("trustRate1: ", requestData["trustRate1"], mturk_id)
    ret = {"imageURL": "images/Slide5.JPG",
           "buttonLabels": ["Prev", "START"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==8:
    #timestamp
    startTime = datetime.datetime.now()
    data = remove_dups("start: ", startTime, mturk_id)
    timestart1[mturk_id] = startTime
    sessionData["playVideo"] = 0
    sessionData["playedLong"] = 0
    ret = {"imageURL": "images/T100.jpg",
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": "Choose how you would like to rotate the table.",
           "sessionData": sessionData,
       "buttonClass": "btn-success"}
    sessionData["picCount"]+=1       
    return json.dumps(ret)

  if sessionData["picCount"]==10:
    sessionData["playVideo"] = 0
    ret = {"imageURL": "",
           "buttonLabels": ["null", "Next"],
           "instructionText": " ",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    sessionData["picCount"]+=1
    #timestamp
    firstFinish = datetime.datetime.now()
    data = remove_dups("firstFinish: ", firstFinish, mturk_id)
    timeDelta = firstFinish-timestart1[mturk_id]
    data = remove_dups("timeDelta: ", timeDelta.total_seconds(), mturk_id)
    return json.dumps(ret)

  if sessionData["picCount"]==11:
    data = remove_dups("trustRate2: ", requestData["trustRate2"], mturk_id)
    sessionData["playVideo"] = 0
    ret = {"imageURL": "images/Slide6.JPG",
           "buttonLabels": ["null", "START"],
           "instructionText": " ",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    data = remove_dups("", "round two", mturk_id)
    sessionData["picCount"]+=1
    #timestamp
    return json.dumps(ret)


  if sessionData["picCount"]==12:
    sessionData["playVideo"] = 0
    Model2.restartTask(d,request.cookies.get('mturk_id','NOT SET'))
    ret = {"imageURL": "images/T100.jpg",
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": "Choose how you would like to rotate the table.",
           "sessionData": sessionData,
       "buttonClass": "btn-success"}
    #timestamp
    secondStart = datetime.datetime.now()
    data = remove_dups("secondStart: ", secondStart, mturk_id)
    timestart2[mturk_id] = secondStart
    sessionData["picCount"]+=1  
    return json.dumps(ret)  

  #record in log
  data[mturk_id].append(buttonClicked)

  #get next move
  currTableTheta, oldTableTheta, resultBelief, resultHAction, message = \
    Model2.getMove(d,request.cookies.get('mturk_id','NOT SET'),buttonClicked, prior)


  #debugging
  #print "Belief is: {}".format(resultBelief)
  #play the long video if the human-robot actions
  # are the same and it's the first time this is happening
  suffix = ""
  prefix = "T"
  if oldTableTheta==currTableTheta and sessionData["playedLong"]==0:
    suffix="l"
    sessionData["playedLong"]=1

  if(resultHAction =='ROTATE_COUNTER_CLOCKWISE'):
    suffix = "e"
    videoLink = "videos/{}{}{}.mp4".format(prefix,currTableTheta,suffix)
  else:
    videoLink = "videos/{}to{}{}.mp4".format(oldTableTheta, currTableTheta,suffix)
  imageLink = "images/T{}.jpg".format(currTableTheta)

  if currTableTheta==0 or currTableTheta==180:
    if sessionData["picCount"]==9:
      Model2.setPrevGoalStateTheta(d,request.cookies.get('mturk_id','NOT SET'), currTableTheta)
      sessionData["picCount"]+=1
    elif sessionData["picCount"]==13:
      global cheating
      cheating = False
      sessionData["toSurvey"] = True
      #timestamp
      secondFinish = datetime.datetime.now()
      lastInd = len(data[mturk_id])-1
      if(type(data[mturk_id][lastInd]) == int):
        data[mturk_id].append("secondfinish: "+ str(secondFinish))
      elif("secondfinish: " in data[mturk_id][lastInd]):
        data[mturk_id][lastInd] = "secondfinish: "+ str(secondFinish)

      timeDelta = secondFinish-timestart2[mturk_id]
      data = remove_dups("timeDelta2: ", timeDelta.total_seconds(), mturk_id)

    trialNum = "trial" + str(trialIndx[mturk_id]) + "belief0:" + str(resultBelief[0][0])
    data = remove_dups("", trialNum, mturk_id)

    trialNum = "trial" + str(trialIndx[mturk_id]) + "belief1:" + str(resultBelief[1][0])
    remove_dups_trial(trialNum, mturk_id)

    trialNum = "trial" + str(trialIndx[mturk_id]) + "belief2:" + str(resultBelief[2][0])
    remove_dups_trial(trialNum, mturk_id)

    trialNum = "trial" + str(trialIndx[mturk_id]) + "belief3:" + str(resultBelief[3][0])
    remove_dups_trial(trialNum, mturk_id)

    trialNum = "trial" + str(trialIndx[mturk_id]) + "belief4:" + str(resultBelief[4][0])
    remove_dups_trial(trialNum, mturk_id)


    # data[mturk_id].append("trial" + str(trialIndx[mturk_id]) + "belief1:" + str(resultBelief[1][0]))
    # data[mturk_id].append("trial" + str(trialIndx[mturk_id]) + "belief2:" + str(resultBelief[2][0]))
    # data[mturk_id].append("trial" + str(trialIndx[mturk_id]) + "belief3:" + str(resultBelief[3][0]))
    # data[mturk_id].append("trial" + str(trialIndx[mturk_id]) + "belief4:" + str(resultBelief[4][0]))
    trialIndx[mturk_id] = trialIndx[mturk_id]  + 1

 
    ret = {"videoURL": videoLink,
           "imageURL": imageLink,
           "buttonLabels": ["null","Next"],
           "instructionText": "The table is in a horizontal position. You finished the task!",
           "sessionData": sessionData}
    return json.dumps(ret)
  else:
    sessionData["playVideo"] = 1
    ret = {"videoURL": videoLink,
           "imageURL":imageLink,
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": "<br>",
           "sessionData": sessionData,
           "buttonClass": "btn-success"}
    return json.dumps(ret)


#when the survey is approved by surveyhandler.js, the button requests this url
#handle_survey records the responses and gives a one line html page in response
#web browsers automatically add head/body syntax for this case
@app.post('/submit_survey')
def handle_survey():
  mturk_id = request.cookies.get('mturk_id', 'EXPIRED')

  if(cheating == True):
    data[mturk_id].append("INCOMPLETE")
    with open('output/log-cheating-v.json', 'a') as outfile:
      json.dump(data, outfile)
    return "<p>It appears that the HIT has not been fully completed. Please complete the HIT again by pasting this link into your browser: http://studies.personalrobotics.ri.cmu.edu/minaek/index.html </p>"
  

  for i in xrange(1,17):
    data[mturk_id].append(request.forms.get(str(i)))
  with open('output/log-v.json', 'w') as outfile:
    json.dump(data, outfile)
  print("User {} submitted the survey".format(mturk_id))
  return "<p> Your answers have been submitted. ID for mturk: {}".format(mturk_id)

#the server only writes to log.json, so if there's some data there already,
#we'll copy it to another file 
def backupLog():
  i=1
  while (os.path.isfile("output/log-backup-{}.json".format(i))):
    i+=1
  shutil.copy("output/log.json","output/log-backup-{}.json".format(i))
 
Model2.globalsInit()
backupLog()
run(app, host='0.0.0.0', port=8084)

