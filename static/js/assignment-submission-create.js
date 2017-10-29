$submit_button=$("input[type='submit']").eq(0);
$code_text_areas=$("textarea[name='code']");
$form=$("#code_form");

$(document).ready(
    function(e){
        bindSubmitEvent();
        $(window).bind('beforeunload', function(){
          return 'Are you sure you want to leave the assignment submission?';
        });
    }
);

function bindSubmitEvent(){
    $submit_button.click(function(e){
        $(window).unbind("beforeunload");
        populate_text_areas();
    });
}

function populate_text_areas(){
    for (i=0;i<$code_text_areas.length;i++){
        $text_area=$code_text_areas.eq(i);
        $text_area.html(ace_edtiors[i].getValue());
    }
}