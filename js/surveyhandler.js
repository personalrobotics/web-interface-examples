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
        if (!$("input[name=4]:checked").val()) demandCompletion(e);


        if (!$("input[name=t5]:checked").val()) demandCompletion(e);
        if (!$("input[name=sc5]:checked").val()) demandCompletion(e);

        //check free response
        if ($(".fr1").val()=='') demandCompletion(e);
        if ($(".fr2").val()=='') demandCompletion(e);
        if ($(".fr3").val()=='') demandCompletion(e);
    })
})