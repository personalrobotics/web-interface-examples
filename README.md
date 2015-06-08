# web-interface-examples
Examples of connecting ROS to web technologies

General hints:

Running rosbridge server: rosrun rosbridge_server rosbridge.py
	
Running mjpeg server: rosrun mjpeg_server mjpeg_server

Easiest way to run a webserver:
In the directory you want to serve:
* python 2.x: python -m SimpleHTTPServer 8080
* python 3.x: python -m http.server 8080

## buttonoptions.html

Run the server:
```
cd [directory where you've put this repo]
python servers/buttonserver.py
```

Navigate to the webpage at http://localhost:8080/buttonoptions.html
