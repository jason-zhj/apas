$(document).ready(
    function(){
        // hide the file path in the file input controls
        hide_file_path();

        style_inputs();

        attach_modal_show_event();

        style_multi_select();
    }
);


function attach_modal_show_event(){
    $("[role='modal_trigger']").click(
        function (e) {
            if ($(this).attr("modal_message")){
                $("#msg_modal").find("[role='message']").html($(this).attr("message"));
            }
            $("#msg_modal").modal({backdrop: 'static',
                keyboard: false});
        }
    );
    $("[role='confirm_modal_trigger']").click(
        function (e) {
            // ask for confirmation
            confirm_message="Are you sure to do this operation?";
            if ($(this).attr("confirm_message")){
                confirm_message=$(this).attr("confirm_message");
            }
            if (!confirm(confirm_message)){
                return false;
            }
            // confirmed, show modal
            if ($(this).attr("modal_message")){
                $("#msg_modal").find("[role='message']").html($(this).attr("message"));
            }
            $("#msg_modal").modal({backdrop: 'static',
                keyboard: false});
        }
    );
}

function show_wait_modal(){
    $("#msg_modal").modal({backdrop: 'static',
                keyboard: false});
}

function hide_file_path(){
            $file_inputs=$("input[type='file']");
        for(i=0;i<$file_inputs.length;i++){
            // find the anchor tag on the same level of DOM
            $anchor=$file_inputs.eq(i).parent().find('a').eq(0);
            if (!$anchor){
                continue;
            }
            text=$anchor.html();
            if (text){
                indexOfSlash=text.lastIndexOf('/');
                if (indexOfSlash!=-1){
                    $anchor.html(text.substring(indexOfSlash+1,text.length));
                }
            }

        }
}

function style_inputs(){
    $inputs=$('input');
    $test_areas=$('textarea');
    $selects=$('select');
    for (i=0;i<$inputs.length;i++){
        $input=$inputs.eq(i);
        if ($input.attr("type")!="checkbox"){
            $input.addClass("form-control");
        }
    }
    if ($test_areas.length!=0){
        $test_areas.addClass("form-control");
    }

        for (i=0;i<$selects.length;i++){
            if ($selects.eq(i).prop("multiple")==false){
                $selects.eq(i).addClass("form-control");
            }
            else{
                $selects.eq(i).addClass("form-control");
            }
        }

}

function style_multi_select(){
    // styling using jquery multi-select
    $multi_selects=$("select[multiple='multiple']");
    for (i=0;i<$multi_selects.length;i++){
        $multi_selects.eq(i).parent().find("span").html("Select items to the right");
        $multi_selects.eq(i).multiSelect();
    }

}
