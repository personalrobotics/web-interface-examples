// buttonoptions.js
//
// demonstrates how to send button clicks to a server

// when used by itself as a function, jQuery's $(func) will call its
// argument when the page is truly done loading
$(init);

var buttonPOSTUrl = "../ui/button";
var sessionData = {"questionsAnswered": 0};
var buttonIDs = ["#left-button", "#right-button"];

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
}

function buttonClicked(idx) {
    disableButtons();
    var postData = {"sessionData": sessionData,
                    "buttonID": idx};
    // Note: posted data *has* to be stringified for bottle.py to understand
    $.post(buttonPOSTUrl, JSON.stringify(postData), handleResponse);
}

function handleResponse(rawData) {
    var jsonData = JSON.parse(rawData);
    sessionData = jsonData["sessionData"];
    if("imageURL" in jsonData) {
        changeImage(jsonData["imageURL"]);
    }
    if("buttonLabels" in jsonData) {
        changeButtonLabels(jsonData["buttonLabels"]);
    }
    if("instructionText" in jsonData) {
        $("#instruction-text").html(jsonData["instructionText"]);
    }
    enableButtons();
}

function disableButtons() {
    $('.ui-button').prop('disabled', true);
}

function enableButtons() {
    $('.ui-button').prop('disabled', false);
}

function changeImage(newImageURL) {
    $("#ui-image").attr("src", newImageURL);
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