$datetime_inputs=$("input[role='datatime_trigger']");
for (i=0;i<$datetime_inputs.length;i++){
    $datetime_inputs.eq(i).datetimepicker();
}


$("#submit_button").bind("click",
    function(e){
        e.preventDefault();
        for (i=0;i<$datetime_inputs.length;i++){
            normalize_date_time($datetime_inputs.eq(i));
        }
        // vaidate weightage
        if (!validate_weightage()){
            return false;
        }
        $("#data_form").eq(0).trigger("submit");
        // show modal
        show_wait_modal();
    }
);

function normalize_date_time(text_control){
    original_value=text_control.val();
    var find = '/';
    var re = new RegExp(find, 'g');
    normalized_value = original_value.replace(re, '-');
    text_control.val(normalized_value);
}
