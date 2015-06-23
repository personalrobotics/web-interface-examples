// surveyhandler.js:
// -catches the survey submit button press
// -stops from going to the page the submit button linked to
//  if any of the inputs is empty
jQuery(function ($) {
    function demandCompletion(e){
        e.preventDefault();
        $(".text-danger").removeClass('hide');
    }
    //submit the form only if it's complete
    $('#survey').submit(function (e) {
        //check multiple-choice
        if (!$("input[name=1]:checked").val()) demandCompletion(e);
        if (!$("input[name=2]:checked").val()) demandCompletion(e);
        if (!$("input[name=3]:checked").val()) demandCompletion(e);
        if (!$("input[name=4]:checked").val()) demandCompletion(e);

        //check questionnaire
        if (!$("input[name=5]:checked").val()) demandCompletion(e);
        if (!$("input[name=6]:checked").val()) demandCompletion(e);
        if (!$("input[name=7]:checked").val()) demandCompletion(e);
        if (!$("input[name=8]:checked").val()) demandCompletion(e);
        if (!$("input[name=9]:checked").val()) demandCompletion(e);
        if (!$("input[name=10]:checked").val()) demandCompletion(e);
        if (!$("input[name=11]:checked").val()) demandCompletion(e);
        if (!$("input[name=12]:checked").val()) demandCompletion(e);
        if (!$("input[name=13]:checked").val()) demandCompletion(e);

        //check free response
        if ($(".fr1").val()=='') demandCompletion(e);
        if ($(".fr2").val()=='') demandCompletion(e);
    })
})