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
preference = dict()
#loads static pages from the directory
#example: website.com/index.html
#server will load index.html from the directory
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
  if sessionData["picCount"]<7:
    if buttonClicked==0:
      sessionData["picCount"] -= 1
    elif buttonClicked==1:
      sessionData["picCount"] += 1

  if sessionData["picCount"]==1:
    ret = {"imageURL": "images/Slide1.JPG",
           "buttonLabels": ["null", "Next"],
           "instructionText": "Instructions 1/3",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==2:
    ret = {"imageURL": "images/Slide2.JPG",
           "buttonLabels": ["null", "Next"],
           "instructionText": " ",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==3:
    ret = {"imageURL": "images/Slide3.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)
  
  if sessionData["picCount"]==4:
    ret = {"imageURL": "images/Slide3b.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)

  #following code may need mturk_id, so get it once now
  mturk_id = request.cookies.get('mturk_id','NOT SET')
  
  if sessionData["picCount"]==5:
    #generate a cookie with user's ID
    gen_id = ''.join(random.choice(string.ascii_uppercase +
      string.digits) for _ in range(6))
    response.set_cookie('mturk_id', gen_id, max_age=survey_duration, path='/')
    data[gen_id] = []
    #get ip
    ip = request.environ.get('REMOTE_ADDR')
    data[gen_id].append(ip)
    ret = {"imageURL": "images/Slide4.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)

  #following code may need mturk_id, so get it once now
  mturk_id = request.cookies.get('mturk_id','NOT SET')

  if sessionData["picCount"]==6:
    # we got the results from slide4 radio
    if "radioChoice" in requestData.keys():
       data[mturk_id].append("radioChoice: "+ requestData["radioChoice"])
       preference[mturk_id] = requestData["radioChoice"]
    ret = {"imageURL": "images/Slide5.JPG",
           "buttonLabels": ["Prev", "START"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==7:
    #timestamp
    startTime = datetime.datetime.now()
    data[mturk_id].append("start: "+ str(startTime))
    timestart1[mturk_id] = startTime
    sessionData["playVideo"] = 0
    sessionData["playedLong"] = 0
    ret = {"imageURL": "images/START.jpg",
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": " ",
           "sessionData": sessionData,
       "buttonClass": "btn-success"}
    sessionData["picCount"]+=1       
    return json.dumps(ret)

  if sessionData["picCount"]==9:
    sessionData["playVideo"] = 0
    ret = {"imageURL": "images/Slide6.JPG",
           "buttonLabels": ["null", "START"],
           "instructionText": " ",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    data[mturk_id].append("round two")
    sessionData["picCount"]+=1
    #timestamp
    firstFinish = datetime.datetime.now()
    data[mturk_id].append("firstFinish: "+ str(firstFinish))
    timeDelta = firstFinish-timestart1[mturk_id]
    data[mturk_id].append("timeDelta: "+ str(timeDelta.total_seconds()))
    return json.dumps(ret)

  if sessionData["picCount"]==10:
    sessionData["playVideo"] = 0
    Model2.restartTask(d,request.cookies.get('mturk_id','NOT SET'))
    ret = {"imageURL": "images/START.jpg",
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": " ",
           "sessionData": sessionData,
       "buttonClass": "btn-success"}
    #timestamp
    secondStart = datetime.datetime.now()
    data[mturk_id].append("secondStart: "+ str(secondStart))
    timestart2[mturk_id] = secondStart
    sessionData["picCount"]+=1  
    return json.dumps(ret)  
  
  #record in log
  data[mturk_id].append(buttonClicked)

  #get next move
  currHumanPos, currRobotPos, oldHumanPos, oldRobotPos, resultBelief, message = \
    Model2.getMove(d,request.cookies.get('mturk_id','NOT SET'),buttonClicked, preference[mturk_id])
  print "DEBUGGING: ", str(message)
  #debugging
  #print "Belief is: {}".format(resultBelief)
  #play the long video if the human-robot actions
  # are the same and it's the first time this is happening
  suffix=""
  if currHumanPos == currRobotPos and sessionData["playedLong"] == 0:
  #if oldTableTheta==currTableTheta and sessionData["playedLong"]==0:
    suffix="l"
    sessionData["playedLong"]=1
  videoLink = "videos/R{}H{}toR{}H{}.mp4".format(oldRobotPos,oldHumanPos,currRobotPos,currHumanPos,suffix)
  imageLink = "images/R{}H{}.jpg".format(currRobotPos,currHumanPos)
  if currHumanPos != currRobotPos:
    sessionData["changeButton"] = 0
  #if currTableTheta==0 or currTableTheta==180:
    if sessionData["picCount"]==8:
      Model2.setPrevGoalHumanRobotPos(d,request.cookies.get('mturk_id','NOT SET'), currHumanPos, currRobotPos)
      sessionData["picCount"]+=1
    elif sessionData["picCount"]==11:
      sessionData["toSurvey"] = True
      #timestamp
      secondFinish = datetime.datetime.now()
      data[mturk_id].append("secondFinish: "+ str(secondFinish))
      timeDelta = secondFinish-timestart2[mturk_id]
      data[mturk_id].append("timeDelta2: "+ str(timeDelta.total_seconds()))
      data[mturk_id].append("belief0:" + str(resultBelief[0][0]))
      data[mturk_id].append("belief1:" + str(resultBelief[1][0]))
      data[mturk_id].append("belief2:" + str(resultBelief[2][0]))
      data[mturk_id].append("belief3:" + str(resultBelief[3][0]))
      data[mturk_id].append("belief4:" + str(resultBelief[4][0]))

    ret = {"videoURL": videoLink,
           "imageURL": imageLink,
           "buttonLabels": ["null","Next"],
           "instructionText": "You crossed the hallway!",
           "sessionData": sessionData}
    return json.dumps(ret)
  else:
    if currHumanPos == currRobotPos and currHumanPos == 2:
	   sessionData["changeButton"] = 2
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
  for i in xrange(1,17):
    data[mturk_id].append(request.forms.get(str(i)))
  with open('output/log.json', 'w') as outfile:
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
run(app, host='0.0.0.0', port=2223)
