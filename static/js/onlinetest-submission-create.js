$submit_button=$("input[type='submit']");
$code_text_areas=$("textarea[name='code']");
$form=$("#code_form");
// add event listener for check button
$(document).ready(
    function(e){
        bindSubmitEvent();
        setTimer();
        // confirmation for stopping the test
        $(window).bind('beforeunload', function(){
          return 'Are you sure you want to leave the online test?';
        });

//        $('body').scrollspy({ target: '#test_left_panel' });
    }
);

function bindSubmitEvent(){
    for (i=0;i<$submit_button.length;i++){
        $submit_button.eq(i).click(function(e){
            $(window).unbind("beforeunload");
            populate_text_areas();
            $("#msg_modal").modal({backdrop: 'static',
                    keyboard: false});
        });
    }

}

function populate_text_areas(){
    for (i=0;i<$code_text_areas.length;i++){
        $text_area=$code_text_areas.eq(i);
        $text_area.html(ace_edtiors[i].getValue());
    }
}

function setTimer(){
          minutes=$("input[name='time_limit']").val();
          end_time=new Date(Number(END_YEAR),Number(END_MONTH)-1,Number(END_DAY),Number(END_HOUR),Number(END_MINUTE),Number(END_SECOND),0);
          $('#test_timer').countdown({until: end_time,
              compact: true, format: 'HMS',
              description: '', alwaysExpire: true, onExpiry: testExpired});
}

function testExpired() {
    // unbind leave page event
    $(window).unbind("beforeunload");
    if (AUTO_SUBMIT_UPON_TIMEOUT){
        populate_text_areas();
        $("#msg_modal").modal({backdrop: 'static',
                keyboard: false});
        $form.submit();
    }
    else{
        // redirect to submission page
        alert("Time is over!");
        window.location.href=REDIRECT_URL;
    }
}