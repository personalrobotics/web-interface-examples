// buttonoptions.js
//
// demonstrates how to send button clicks to a server

// when used by itself as a function, jQuery's $(func) will call its
// argument when the page is truly done loading
$(init);

var buttonPOSTUrl = "ui/button";
var sessionData = {"picCount": 0};
var buttonIDs = ["#left-button", "#right-button"];
var cheating = true;
// if(cheating == true && document.URL=="http://localhost:8085/survey.html"){
// console.log("CHEATING TRUE");

// window.location.href = "cheating.html";
// }

// Because of the strange way that javascript scoping works, in order
// to actually get the value i into a closure we need to actually have
// another level of function outside of it (in javascript only functions
// create new variable scope)
function makeClickHandler(i) {
    var idx = i;
    return function(e) { buttonClicked(idx); };
}

function init() {
    // there are other, arguably more 'elegant' ways to bind button
    // handlers (e.g., with data attributes), but for this example we
    // will individually bind the buttons
    for(var i = 0; i < buttonIDs.length; ++i) {
        $(buttonIDs[i]).click(makeClickHandler(i));
    }

    //prevents users from creating a new row by pressing enter on the welcome screen
    $('#text_welcome').keydown(function(e){
        if(e.keyCode==13){
            e.preventDefault();
        }
    });
}

function buttonClicked(idx) {
    //disableButtons();

    var postData = {}

    if (sessionData["picCount"] == 13 || sessionData["picCount"]==12) {
        cheating = false;
    }




    if (sessionData["picCount"]==0){
        //postData = {"sessionData": "", "buttonID": ""}
        //disableButtons();
        text = $.trim($("#text_welcome").val());
        len = text.length;
        if(len==0){
            $('#prompt_welcome').css('color', 'red');        
                }

        if(len>0){
            enableButtons();
            postData = {"sessionData": sessionData,
                            "buttonID": idx,
                            "worker_id": text};
            }
        }

    if(sessionData["picCount"]!=0){
        postData = {"sessionData": sessionData, "buttonID": idx, "worker_id":$.trim($("#text_welcome").val())};
    }

    if (sessionData["picCount"]==4){
        $(".text-danger").show()
        if ((!$("input[name=1]:checked").val())&&(postData["buttonID"]==1)){
            $(".text-danger").removeClass('hide');
            enableButtons();
        }
        else if((!$("input[name=1]:checked").val())&&(postData["buttonID"]==0)){
            $(".radio").hide()
            $(".text-danger").hide()
            $.post(buttonPOSTUrl, JSON.stringify(postData), handleResponse);
        }
        else{
            radioChoice = $("input[name=1]:checked").val()
            $(".radio").hide()
            $(".text-danger").hide()
            postData["radioChoice"] = radioChoice
            $.post(buttonPOSTUrl, JSON.stringify(postData), handleResponse);
        }
    }
    else if(sessionData["picCount"]==6){
     $(".text-danger").show()
        if (((!$("input[name=t1]:checked").val()))&&(postData["buttonID"]==1)){
            $(".text-danger").removeClass('hide');
            enableButtons();
        }
        else if(postData["buttonID"]==0){
            $(".trust1").hide()
            $(".trust1text").hide()
            $(".text-danger").hide()
            $.post(buttonPOSTUrl, JSON.stringify(postData), handleResponse);
        }
        else if(($("input[name=t1]:checked").val())&&(postData["buttonID"]==1)){
            radioChoice = $("input[name=t1]:checked").val()
            $(".trust1").hide()
            $(".trust1text").hide()
            $(".text-danger").hide()
            postData["trustRate1"] = radioChoice
            $.post(buttonPOSTUrl, JSON.stringify(postData), handleResponse);
        }
    }
   else if(sessionData["picCount"]==11){
        $(".text-danger").show()
        if (((!$("input[name=t2]:checked").val()))&&(postData["buttonID"]==1)){
            $(".text-danger").removeClass('hide');
            enableButtons();
        }
        else if(postData["buttonID"]==0){
            $(".trust2").hide()
            $(".trust2text").hide()
            $(".text-danger").hide()
            $.post(buttonPOSTUrl, JSON.stringify(postData), handleResponse);
        }
        else if(($("input[name=t2]:checked").val())&&(postData["buttonID"]==1)){
            radioChoice = $("input[name=t2]:checked").val()
            $(".trust2").hide()
            $(".trust2text").hide()

            $(".text-danger").hide()
            postData["trustRate2"] = radioChoice

            $.post(buttonPOSTUrl, JSON.stringify(postData), handleResponse);
        }
    }
    else
        // Note: posted data *has* to be stringified for bottle.py to understand
        $.post(buttonPOSTUrl, JSON.stringify(postData), handleResponse);
}
// handleResponse takes the data returned by the python server
function handleResponse(rawData) {
    var jsonData = JSON.parse(rawData);
    sessionData = jsonData["sessionData"];
    // when the server determines that the game is over,
    //  it notifies via toSurvey var
    //   and javascripts load the survey page from the directory
    if ("toSurvey" in jsonData){
        window.location.href = "survey.html";

    }
    console.log(cheating);
    if(cheating == true && document.URL=="http://localhost:8085/survey.html"){
    console.log("CHEATING TRUE");
    window.location.href = "cheating.html";
    }

    //server may provide a new image, new buttons text, colors, instructions
    else{
        enableButtons();
        if("instructionText" in jsonData) {
            $("#instruction-text").html(jsonData["instructionText"]);
        }

        if(sessionData["picCount"]==0){
            $("#group_welcome").show();

        }
        // console.log('hide')
        else{
            $("#group_welcome").hide();
        }


        if(sessionData["picCount"]==9 || sessionData["picCount"]==10|| sessionData["picCount"]==11|| 
sessionData["picCount"]==13){
            //videos start only after instructions
            if (sessionData["playVideo"]==1){ //remove now for debugging
                //disable buttons until the video is over
                disableButtons();
                $("#instruction-text").html("<br>"); //disable html text while video is playing
                $('#ui-video').attr('src', jsonData["videoURL"]);
                $('#ui-image').hide();
                $('#ui-video').removeAttr('style');
                //can work with video only when the page is done loading
                var vid = document.getElementById("ui-video");
                vid.onended = function() {
                    $("#instruction-text").html(jsonData["instructionText"]);
                    $('#ui-image').removeAttr('style');
                    $('#ui-image').attr('src', jsonData["imageURL"]);
                    $('#ui-video').hide();
                    if("buttonLabels" in jsonData) {
                        if (jsonData["buttonLabels"][0]!="null"){
                            $('#left-button').removeAttr('style');
                        }
                        else{
                            $('#left-button').hide();
                        }
                        changeButtonLabels(jsonData["buttonLabels"]);
                    }
                    //handle changing button colors upon server request 
                    var bclasses = "btn-primary btn-success btn-danger btn-warning";
                    var newclass = jsonData["buttonClass"] || "btn-primary";
                    $(".ui-button").removeClass(bclasses).addClass(newclass);
                    enableButtons();
                };
            }
            else{
                changeImage(jsonData["imageURL"]);
                if("buttonLabels" in jsonData) {
                    if (jsonData["buttonLabels"][0]!="null"){
                        $('#left-button').removeAttr('style');
                    }
                    else{
                        $('#left-button').hide();
                    }
                    changeButtonLabels(jsonData["buttonLabels"]);
                }
                //handle changing button colors upon server request 
                var bclasses = "btn-primary btn-success btn-danger btn-warning";
                var newclass = jsonData["buttonClass"] || "btn-primary";
                $(".ui-button").removeClass(bclasses).addClass(newclass);
            }
        }
        else if("imageURL" in jsonData) {
            changeImage(jsonData["imageURL"]);
            if("buttonLabels" in jsonData) {
                if (jsonData["buttonLabels"][0]!="null"){
                    $('#left-button').removeAttr('style');
                }
                else{
                    $('#left-button').hide();
                }
                changeButtonLabels(jsonData["buttonLabels"]);
            }
            //handle changing button colors upon server request 
            var bclasses = "btn-primary btn-success btn-danger btn-warning";
            var newclass = jsonData["buttonClass"] || "btn-primary";
            $(".ui-button").removeClass(bclasses).addClass(newclass);
        }
        //dont frame the buttons as previously selected
        $('.ui-button').blur();

         if(sessionData["picCount"]==2){
         }
        else if (sessionData["picCount"]==4){
            $('.radio').removeAttr('style');
        }
        else if(sessionData["picCount"] == 6){
            $('.trust1').removeAttr('style');
            $('.trust1text').removeAttr('style');           
        }
        else if(sessionData["picCount"] == 11){
            $('.trust2').removeAttr('style');
            $('.trust2text').removeAttr('style');
        }
    }
}

function disableButtons() {
    $('.ui-button').prop('disabled', true);
}

function enableButtons() {
    $('.ui-button').prop('disabled', false);
}

function changeImage(newImageURL) {
    if (newImageURL==""){
       $("#ui-image").hide();
    }
    else{
       $("#ui-image").show();
       $("#ui-image").attr("src", newImageURL);
    } 
}

function changeButtonLabels(newlabels) {
    for(var i = 0; i < newlabels.length && i < buttonIDs.length; ++i) {
        // Note: we could use .text(newlabels[i]) if we wanted to 
        // prevent the button label from being interpreted as html,
        // but because we trust the source (it's our own server) and
        // we might want to have labels with e.g. icons, we will let
        // the label be arbitrary html
        $(buttonIDs[i]).html(newlabels[i]);
    }
}

// $(window).load(function(){
//     console.log(cheating);
//     console.log(document.URL);
//     if(cheating == true && document.URL=="http://localhost:8085/survey.html"){
//         console.log("CHEATING TRUE");

//         window.location.href = "cheating.html";
//     }
// });

// window.document.onload = function(e){
//     if(cheating == true){
//         window.location.href = "cheating.html";
//     }
// }
