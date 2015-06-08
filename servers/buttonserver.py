from bottle import Bottle, run, static_file, request
import json

app = Bottle()

@app.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root=".")

@app.post('/ui/button') # or @route('/login', method='POST')
def do_click():
    requestData = json.loads(request.body.getvalue())
    sessionData = requestData["sessionData"]
    buttonClicked = requestData["buttonID"]
    print("User clicked on button {}".format(buttonClicked))
    numAnswered = sessionData["questionsAnswered"]
    sessionData["questionsAnswered"] += 1
    ret = {"imageURL": "images/dog.jpg",
           "buttonLabels": ["cats", "dogs"],
           "instructionText": "Question {}: Which do you like more?".format(numAnswered),
           "sessionData": sessionData}
    return json.dumps(ret)

run(app, host='localhost', port=8080)