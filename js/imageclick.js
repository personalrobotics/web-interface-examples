// imageclick.js
//
// demonstrates how to send click events on an image to ROS

// when used by itself as a function, jQuery's $(func) will call its
// argument when the page is truly done loading
$(init);

var ros = null, sendTopic = null;
var sendTopicName = "/webui/clicks"
var mjpegURL = "http://herb0:8080/stream?topic=/head/kinect2/rgb/image";
var rosbridgeServerUrl = "ws://herb0:9090";

function init() {
    ros = new ROSLIB.Ros({
        url : rosbridgeServerUrl
    });
   
    ros.on('connection', function() {
        console.log('Connected to websocket server.');
    });
   
    ros.on('error', function(error) {
        console.log('Error connecting to websocket server: ', error);
    });
   
    ros.on('close', function() {
        console.log('Connection to websocket server closed.');
    });

    sendTopic = new ROSLIB.Topic({
        ros : ros,
        name : sendTopicName,
        messageType : 'std_msgs/String'
    });

    // playing an mjpeg stream is no more complicated than just
    // creating (or setting) an image with its URL
    $("#ros-stream").attr("src", mjpegURL);

    $("#ros-stream").click(function(e){
        // $(this) in a jquery event handler will return the
        // jquery element that the handler is attached to
        var imageOrigin = $(this).offset(); 
        var relX = e.pageX - imageOrigin.left;
        var relY = e.pageY - imageOrigin.top;
        publishClick(relX, relY);
    });
}

// publish a click as a space-separated plain-text pair
// e.g.: "123 928"
function publishClick(x, y) {
    var coordString = x + " " + y;
    console.log("Publishing: " + coordString);

    var rosmsg = new ROSLIB.Message({
        data: coordString
    });

    sendTopic.publish(rosmsg);
}