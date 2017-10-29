$start_submission_time_text=$('#id_start_test_time');
$end_submission_time_text=$('#id_end_test_time');
$start_submission_time_text.datetimepicker();
$end_submission_time_text.datetimepicker();

$("#submit_button").bind("click",
    function(e){
        e.preventDefault();
        normalize_date_time($start_submission_time_text);
        normalize_date_time($end_submission_time_text);

        $("input[type='submit']").eq(0).trigger("submit");
    }
);

function normalize_date_time(text_control){
    original_value=text_control.val();
    var find = '/';
    var re = new RegExp(find, 'g');
    normalized_value = original_value.replace(re, '-');
    text_control.val(normalized_value);
}